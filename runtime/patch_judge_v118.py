from pathlib import Path
import json, time, hashlib

ROOT = Path(__file__).resolve().parents[1]
PATCH_GATE = ROOT / "var" / "patch_gate"
PROPOSALS = PATCH_GATE / "proposals"
APPLIED = PATCH_GATE / "applied"
REJECTED = PATCH_GATE / "rejected"
LOGS = PATCH_GATE / "logs"

JUDGMENTS = PATCH_GATE / "patch_judgments_v118.jsonl"
STATE = PATCH_GATE / "patch_judge_state_v118.json"

PROTECTED = {
    "runtime/full_leveon_response_v82.py",
}

GOOD_ZONES = (
    "runtime/",
    "kernel/",
    "templates/",
    "static/",
    "var/",
    "app_chatroom.py",
)

def _load(path, fallback=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return fallback

def _last_jsonl(path):
    path = Path(path)
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8", errors="replace")
    for line in reversed(raw.strip().splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except Exception:
            pass
    return None

def _write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _append(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def _safe_path_score(paths):
    if not paths:
        return 0.0

    score = 1.0
    notes = []

    for p in paths:
        p = str(p).replace("\\", "/").lstrip("/")

        if ".." in Path(p).parts:
            score -= 0.5
            notes.append(f"path traversal risk: {p}")

        if p in PROTECTED:
            score -= 0.35
            notes.append(f"protected spine touched: {p}")

        if not any(p == z or p.startswith(z) for z in GOOD_ZONES):
            score -= 0.25
            notes.append(f"outside normal zone: {p}")

    return max(score, 0.0), notes

def judge_proposal(path):
    proposal = _load(path, {})
    ops = proposal.get("ops", []) if isinstance(proposal, dict) else []
    paths = [op.get("path", "") for op in ops if isinstance(op, dict)]

    path_score, path_notes = _safe_path_score(paths)

    human_lock = 1.0 if proposal.get("human_approved") is True else 0.4
    has_ops = 1.0 if ops else 0.0
    compile_declared = 1.0 if proposal.get("compile") else 0.5

    source_protection = 1.0
    for p in paths:
        if p in PROTECTED and not proposal.get("approved_spine_write"):
            source_protection = 0.2

    usefulness = 0.5
    text = json.dumps(proposal).lower()
    if "visual" in text or "memory" in text or "render" in text or "context" in text:
        usefulness += 0.25
    if "source_mutation" in text or "blocked" in text or "without_source_mutation" in text:
        usefulness += 0.15

    total = round(
        0.25 * path_score +
        0.20 * human_lock +
        0.20 * source_protection +
        0.15 * has_ops +
        0.10 * compile_declared +
        0.10 * min(usefulness, 1.0),
        4
    )

    if total >= 0.82 and proposal.get("human_approved") is True:
        action = "apply_ready"
    elif total >= 0.72:
        action = "review_ready"
    elif total >= 0.55:
        action = "hold_for_revision"
    else:
        action = "reject"

    judgment = {
        "ts": time.time(),
        "kind": "proposal",
        "path": str(path),
        "proposal_id": proposal.get("proposal_id"),
        "title": proposal.get("title"),
        "scores": {
            "path_safety": round(path_score, 4),
            "human_lock": human_lock,
            "source_protection": source_protection,
            "has_ops": has_ops,
            "compile_declared": compile_declared,
            "usefulness": round(min(usefulness, 1.0), 4),
            "total": total,
        },
        "notes": path_notes,
        "suggested_action": action,
        "law": "v118_patch_judge_scores_before_apply",
    }

    return judgment

def judge_latest_event():
    event = _last_jsonl(LOGS / "patch_gate_events.jsonl")
    if not event:
        return {
            "ts": time.time(),
            "kind": "gate_event",
            "status": "missing",
            "total": 0.0,
            "law": "v118_no_patch_gate_event_found",
        }

    status = event.get("status")
    error = event.get("error")
    changed = event.get("changed", [])
    compiled = event.get("compiled", [])
    backups = event.get("backups", [])

    path_score, path_notes = _safe_path_score(changed)

    applied_ok = 1.0 if status == "applied" and error is None else 0.0
    compile_ok = 1.0 if compiled else 0.3
    rollback_ready = 1.0 if backups else 0.4

    total = round(
        0.35 * applied_ok +
        0.25 * compile_ok +
        0.20 * rollback_ready +
        0.20 * path_score,
        4
    )

    judgment = {
        "ts": time.time(),
        "kind": "gate_event",
        "proposal_id": event.get("proposal_id"),
        "title": event.get("title"),
        "event_status": status,
        "scores": {
            "applied_ok": applied_ok,
            "compile_ok": compile_ok,
            "rollback_ready": rollback_ready,
            "path_safety": round(path_score, 4),
            "total": total,
        },
        "notes": path_notes,
        "suggested_action": "keep" if total >= 0.8 else "inspect",
        "law": "v118_patch_judge_scores_applied_event",
    }

    return judgment

def judge_latest_proposal():
    files = sorted(PROPOSALS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return {
            "ts": time.time(),
            "kind": "proposal",
            "status": "missing",
            "law": "v118_no_proposal_found",
        }
    return judge_proposal(files[0])

def main():
    proposal_judgment = judge_latest_proposal()
    event_judgment = judge_latest_event()

    packet = {
        "ts": time.time(),
        "proposal_judgment": proposal_judgment,
        "event_judgment": event_judgment,
        "loop_state": {
            "proposal_ready": proposal_judgment.get("suggested_action") in {"apply_ready", "review_ready"},
            "last_patch_healthy": event_judgment.get("suggested_action") == "keep",
            "source_protected": True,
            "law": "v118_metrics_on_patch_loop",
        },
        "law": "v118_patch_judgment_engine",
    }

    _append(JUDGMENTS, packet)
    _write(STATE, packet)

    print(json.dumps(packet, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

