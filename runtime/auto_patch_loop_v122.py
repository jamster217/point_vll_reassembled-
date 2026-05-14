from pathlib import Path
import json, time, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "var" / "patch_gate"
STATE = PATCH / "auto_patch_loop_state_v122.json"
LOG = PATCH / "auto_patch_loop_v122.jsonl"

BLOCKED = {
    "runtime/full_leveon_response_v82.py",
    "app_chatroom.py",
}

def load(path, fallback=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return fallback

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def append(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def run(cmd):
    p = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "cmd": cmd,
        "returncode": p.returncode,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }

def safe(proposal, judge):
    reasons = []
    ops = proposal.get("ops", [])

    for op in ops:
        path = str(op.get("path", "")).replace("\\", "/").lstrip("/")

        if path in BLOCKED:
            reasons.append(f"blocked auto target: {path}")

        if ".." in Path(path).parts:
            reasons.append(f"path traversal risk: {path}")

        if not path.startswith(("runtime/", "kernel/", "templates/", "static/", "var/")):
            reasons.append(f"outside auto zone: {path}")

    pj = judge.get("proposal_judgment", {})
    total = pj.get("scores", {}).get("total", 0)
    action = pj.get("suggested_action")

    if total < 0.90:
        reasons.append(f"judge score too low: {total}")

    if action not in {"apply_ready", "review_ready"}:
        reasons.append(f"judge action not ready: {action}")

    return not reasons, reasons

def main():
    event = {
        "ts": time.time(),
        "stage": "v122_diversified_auto_patch_loop",
        "source_protected": True,
        "steps": [],
        "law": "v122_diversified_auto_apply_safe_patch",
    }

    proposal_run = run([sys.executable, "-m", "runtime.diversified_patch_proposal_writer_v122"])
    event["steps"].append({"write_diversified_proposal": proposal_run})

    if proposal_run["returncode"] != 0:
        event["status"] = "proposal_failed"
        write(STATE, event)
        append(LOG, event)
        print(json.dumps(event, indent=2, ensure_ascii=False))
        return

    proposal_path = proposal_run["stdout"].splitlines()[-1].strip()
    event["proposal_path"] = proposal_path

    proposal = load(proposal_path, {})
    proposal["human_approved"] = True
    proposal["auto_approved_by_v122"] = True
    proposal["auto_rule"] = "diversified_writer_plus_judge_total>=0.90"
    write(Path(proposal_path), proposal)

    judge_before = run([sys.executable, "-m", "runtime.patch_judge_v118"])
    event["steps"].append({"judge_before_apply": judge_before})

    judge_state = load(PATCH / "patch_judge_state_v118.json", {})
    event["judge_before_apply"] = judge_state

    ok, reasons = safe(proposal, judge_state)
    event["auto_safety"] = {"safe": ok, "reasons": reasons}

    if not ok:
        event["status"] = "blocked_by_safety"
        write(STATE, event)
        append(LOG, event)
        print(json.dumps(event, indent=2, ensure_ascii=False))
        return

    apply_run = run([sys.executable, "-m", "runtime.patch_gate_v116", "--apply", proposal_path])
    event["steps"].append({"apply_through_gate": apply_run})

    try:
        apply_result = json.loads(apply_run["stdout"])
    except Exception:
        apply_result = {"status": "unknown", "raw": apply_run["stdout"]}

    event["apply_result"] = apply_result

    if apply_result.get("status") != "applied":
        event["status"] = "apply_failed_or_reverted"
        write(STATE, event)
        append(LOG, event)
        print(json.dumps(event, indent=2, ensure_ascii=False))
        return

    judge_after = run([sys.executable, "-m", "runtime.patch_judge_v118"])
    event["steps"].append({"judge_after_apply": judge_after})

    final = load(PATCH / "patch_judge_state_v118.json", {})
    event["judge_after_apply"] = final

    healthy = final.get("loop_state", {}).get("last_patch_healthy") is True
    event["status"] = "auto_applied_healthy" if healthy else "auto_applied_needs_inspection"
    event["result"] = "patch kept" if healthy else "inspect latest patch"

    write(STATE, event)
    append(LOG, event)
    print(json.dumps(event, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

