from pathlib import Path
import json, time, hashlib, shutil, py_compile, sys

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "var" / "patch_gate"
PROPOSALS = GATE / "proposals"
APPLIED = GATE / "applied"
REJECTED = GATE / "rejected"
BACKUPS = GATE / "backups"
LOGS = GATE / "logs"

ALLOWED_PREFIXES = (
    "runtime/",
    "kernel/",
    "templates/",
    "static/",
    "var/",
    "app_chatroom.py",
)

PROTECTED_FILES = {
    "runtime/full_leveon_response_v82.py",
}

def _now():
    return time.strftime("%Y%m%d_%H%M%S")

def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def _write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _append_log(data):
    LOGS.mkdir(parents=True, exist_ok=True)
    with (LOGS / "patch_gate_events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def _safe_rel(path):
    rel = str(path).replace("\\", "/").lstrip("/")
    if not rel or ".." in Path(rel).parts:
        raise ValueError(f"unsafe path: {rel}")
    if rel.startswith("."):
        raise ValueError(f"hidden path blocked: {rel}")
    if not any(rel == p or rel.startswith(p) for p in ALLOWED_PREFIXES):
        raise ValueError(f"path outside allowed patch zone: {rel}")
    return rel

def _target(rel):
    return ROOT / rel

def _backup(rel, proposal_id):
    src = _target(rel)
    dst = BACKUPS / proposal_id / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy2(src, dst)
        return {"path": rel, "backup": str(dst.relative_to(ROOT)), "existed": True}
    return {"path": rel, "backup": None, "existed": False}

def _restore(record):
    rel = record["path"]
    target = _target(rel)
    if record.get("existed") and record.get("backup"):
        backup = ROOT / record["backup"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup, target)
    else:
        if target.exists():
            target.unlink()

def _compile(paths):
    compiled = []
    for rel in paths:
        if rel.endswith(".py"):
            py_compile.compile(str(_target(rel)), doraise=True)
            compiled.append(rel)
    if (ROOT / "app_chatroom.py").exists():
        py_compile.compile(str(ROOT / "app_chatroom.py"), doraise=True)
        compiled.append("app_chatroom.py")
    return compiled

def validate(proposal):
    if not isinstance(proposal, dict):
        raise ValueError("proposal must be object")

    proposal_id = proposal.get("proposal_id")
    if not proposal_id:
        proposal_id = "proposal_" + hashlib.sha256(json.dumps(proposal, sort_keys=True).encode()).hexdigest()[:12]
        proposal["proposal_id"] = proposal_id

    if proposal.get("human_approved") is not True:
        raise PermissionError("blocked: human_approved must be true")

    ops = proposal.get("ops")
    if not isinstance(ops, list) or not ops:
        raise ValueError("proposal requires non-empty ops")

    for op in ops:
        rel = _safe_rel(op.get("path", ""))
        if rel in PROTECTED_FILES and not proposal.get("approved_spine_write"):
            raise PermissionError(f"protected spine file blocked: {rel}")

        kind = op.get("op")
        if kind not in {"create", "append_end", "replace_once", "append_after"}:
            raise ValueError(f"unsupported op: {kind}")

        if kind in {"create", "append_end"} and "content" not in op:
            raise ValueError(f"{kind} requires content")

        if kind == "replace_once" and ("find" not in op or "replace" not in op):
            raise ValueError("replace_once requires find and replace")

        if kind == "append_after" and ("find" not in op or "content" not in op):
            raise ValueError("append_after requires find and content")

    return proposal

def apply_proposal(path):
    proposal = _read_json(path)
    result = {
        "ts": time.time(),
        "proposal_path": str(path),
        "status": "started",
        "backups": [],
        "changed": [],
        "compiled": [],
        "error": None,
        "law": "v116_controlled_patch_gate_backup_apply_compile_revert",
    }

    try:
        proposal = validate(proposal)
        proposal_id = proposal["proposal_id"]
        result["proposal_id"] = proposal_id
        result["title"] = proposal.get("title", "")

        for op in proposal["ops"]:
            rel = _safe_rel(op["path"])
            result["backups"].append(_backup(rel, proposal_id))

        for op in proposal["ops"]:
            rel = _safe_rel(op["path"])
            path = _target(rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            kind = op["op"]

            if kind == "create":
                if path.exists() and not op.get("overwrite", False):
                    raise FileExistsError(f"exists and overwrite=false: {rel}")
                path.write_text(op["content"], encoding="utf-8")

            elif kind == "append_end":
                old = path.read_text(encoding="utf-8") if path.exists() else ""
                path.write_text(old.rstrip() + "\n\n" + op["content"].rstrip() + "\n", encoding="utf-8")

            elif kind == "replace_once":
                old = path.read_text(encoding="utf-8")
                count = old.count(op["find"])
                if count != 1:
                    raise ValueError(f"replace_once expected 1 match in {rel}, found {count}")
                path.write_text(old.replace(op["find"], op["replace"], 1), encoding="utf-8")

            elif kind == "append_after":
                old = path.read_text(encoding="utf-8")
                if op["find"] not in old:
                    raise ValueError(f"append_after marker not found in {rel}")
                path.write_text(old.replace(op["find"], op["find"] + op["content"], 1), encoding="utf-8")

            result["changed"].append(rel)

        compile_targets = list(dict.fromkeys(result["changed"] + proposal.get("compile", [])))
        result["compiled"] = _compile(compile_targets)
        result["status"] = "applied"

        APPLIED.mkdir(parents=True, exist_ok=True)
        _write_json(APPLIED / f"{proposal_id}_{_now()}.json", {"proposal": proposal, "result": result})
        _append_log(result)
        return result

    except Exception as e:
        result["status"] = "reverted"
        result["error"] = repr(e)

        for record in reversed(result.get("backups", [])):
            try:
                _restore(record)
            except Exception as re:
                result.setdefault("rollback_errors", []).append(repr(re))

        REJECTED.mkdir(parents=True, exist_ok=True)
        proposal_id = result.get("proposal_id", "unknown")
        _write_json(REJECTED / f"{proposal_id}_{_now()}.json", {"proposal": proposal, "result": result})
        _append_log(result)
        return result

def make_probe():
    PROPOSALS.mkdir(parents=True, exist_ok=True)
    proposal = {
        "proposal_id": "v116_probe_create_safe_runtime_file",
        "title": "Probe controlled patch gate",
        "human_approved": True,
        "ops": [
            {
                "op": "create",
                "path": "runtime/patch_gate_probe_v116.py",
                "overwrite": True,
                "content": "PROBE_OK = True\n\ndef probe():\n    return 'v116_patch_gate_alive'\n",
            }
        ],
        "compile": ["runtime/patch_gate_probe_v116.py"],
        "law": "probe_patch_only_no_core_mutation",
    }
    path = PROPOSALS / "v116_probe_create_safe_runtime_file.json"
    _write_json(path, proposal)
    return path

def main(argv):
    for d in [PROPOSALS, APPLIED, REJECTED, BACKUPS, LOGS]:
        d.mkdir(parents=True, exist_ok=True)

    if "--make-probe" in argv:
        print(make_probe())
        return 0

    if "--apply" in argv:
        idx = argv.index("--apply")
        print(json.dumps(apply_proposal(argv[idx + 1]), indent=2, ensure_ascii=False))
        return 0

    if "--apply-latest" in argv:
        files = sorted(PROPOSALS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            print("no proposals found")
            return 1
        print(json.dumps(apply_proposal(files[0]), indent=2, ensure_ascii=False))
        return 0

    print("usage: python -m runtime.patch_gate_v116 --make-probe | --apply <proposal.json> | --apply-latest")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

