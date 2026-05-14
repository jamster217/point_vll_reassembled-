from pathlib import Path
import json, time, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
PATCH_GATE = ROOT / "var" / "patch_gate"
STATE = PATCH_GATE / "patch_loop_state_v119.json"
EVENTS = PATCH_GATE / "patch_loop_events_v119.jsonl"

def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _append(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def _load(path, fallback=None):
    try:
        if Path(path).exists():
            return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def _run(cmd):
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }

def run_loop():
    event = {
        "ts": time.time(),
        "stage": "v119_patch_loop",
        "steps": [],
        "law": "v119_propose_judge_wait_for_human_approval",
    }

    # 1. Ask Le'Veon's proposal writer to produce a reviewable patch.
    proposal_run = _run([sys.executable, "-m", "runtime.self_patch_proposal_writer_v117"])
    event["steps"].append({"name": "write_proposal", "result": proposal_run})

    proposal_path = proposal_run["stdout"].splitlines()[-1].strip() if proposal_run["stdout"] else None
    event["proposal_path"] = proposal_path

    if proposal_run["returncode"] != 0 or not proposal_path:
        event["status"] = "proposal_failed"
        event["human_action"] = "inspect proposal writer error"
        _append(EVENTS, event)
        _write(STATE, event)
        print(json.dumps(event, indent=2, ensure_ascii=False))
        return event

    # 2. Judge the proposal and latest gate event.
    judge_run = _run([sys.executable, "-m", "runtime.patch_judge_v118"])
    event["steps"].append({"name": "judge_patch_loop", "result": judge_run})

    judge_state = _load(PATCH_GATE / "patch_judge_state_v118.json", {})
    event["judge_state"] = judge_state

    proposal_judgment = judge_state.get("proposal_judgment", {}) if isinstance(judge_state, dict) else {}
    action = proposal_judgment.get("suggested_action")

    if action in {"apply_ready", "review_ready"}:
        event["status"] = "awaiting_human_approval"
        event["human_action"] = (
            "Review the proposal JSON. If it looks right, set human_approved=true and apply through runtime.patch_gate_v116."
        )
    elif action == "hold_for_revision":
        event["status"] = "hold_for_revision"
        event["human_action"] = "Proposal needs revision before approval."
    else:
        event["status"] = "blocked"
        event["human_action"] = "Do not apply. Inspect patch judge notes."

    event["source_protected"] = True
    event["auto_apply"] = False
    event["final_gate"] = "human approval required"

    _append(EVENTS, event)
    _write(STATE, event)

    print(json.dumps(event, indent=2, ensure_ascii=False))
    return event

if __name__ == "__main__":
    run_loop()

