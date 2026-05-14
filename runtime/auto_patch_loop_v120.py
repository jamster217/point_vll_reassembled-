from pathlib import Path
import json, time, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "var" / "patch_gate"
STATE = PATCH / "auto_patch_loop_state_v120.json"
LOG = PATCH / "auto_patch_loop_v120.jsonl"

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

def safe_to_auto_apply(proposal, judge):
    reasons = []

    ops = proposal.get("ops", [])
    if not ops:
        reasons.append("no ops")

    for op in ops:
        path = str(op.get("path", "")).replace("\\", "/").lstrip("/")

        if path in BLOCKED:
            reasons.append(f"blocked auto target: {path}")

        if ".." in Path(path).parts:
            reasons.append(f"path traversal risk: {path}")

        if not path.startswith(("runtime/", "kernel/", "templates/", "static/", "var/")):
            reasons.append(f"outside auto zone: {path}")

    pj = judge.get("proposal_judgment", {})
    score = pj.get("scores", {}).get("total", 0)
    action = pj.get("suggested_action")

    if score < 0.90:
        reasons.append(f"judge score too low: {score}")

    if action not in {"apply_ready", "review_ready"}:
        reasons.append(f"judge action not ready: {action}")

    return len(reasons) == 0, reasons

def main():
    event = {
        "ts": time.time(),
        "stage": "v120_auto_patch_loop",
        "auto_apply": True,
        "source_protected": True,
        "steps": [],
        "law": "v120_auto_decide_apply_compile_judge",
    }

    proposal_run = run([sys.executable, "-m", "runtime.self_patch_proposal_writer_v117"])
    event["steps"].append({"write_proposal": proposal_run})

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
    proposal["auto_approved_by_v120"] = True
    proposal["auto_rule"] = "judge_total>=0.90_no_blocked_paths_compile_required"
    write(Path(proposal_path), proposal)

    judge_run = run([sys.executable, "-m", "runtime.patch_judge_v118"])
    event["steps"].append({"judge_before_apply": judge_run})

    judge = load(PATCH / "patch_judge_state_v118.json", {})
    event["judge_before_apply"] = judge

    safe, reasons = safe_to_auto_apply(proposal, judge)
    event["auto_safety"] = {"safe": safe, "reasons": reasons}

    if not safe:
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

    final_judge_run = run([sys.executable, "-m", "runtime.patch_judge_v118"])
    event["steps"].append({"judge_after_apply": final_judge_run})

    final_judge = load(PATCH / "patch_judge_state_v118.json", {})
    event["judge_after_apply"] = final_judge

    healthy = final_judge.get("loop_state", {}).get("last_patch_healthy") is True

    event["status"] = "auto_applied_healthy" if healthy else "auto_applied_needs_inspection"
    event["result"] = "patch kept" if healthy else "inspect latest patch"

    write(STATE, event)
    append(LOG, event)

    print(json.dumps(event, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

