from pathlib import Path
import json, time, subprocess, sys, hashlib

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "var" / "patch_gate"

STATE = PATCH / "rapid_improvement_state_v121.json"
LOG = PATCH / "rapid_improvement_events_v121.jsonl"
LOCK = PATCH / "rapid_improvement_v121.lock"

MAX_DEFAULT_CYCLES = 3
MIN_TOTAL_SCORE = 0.90
MAX_REPEATED_PROPOSALS = 2

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

def score_from_auto_state(state):
    judge = state.get("judge_after_apply") or state.get("judge_before_apply") or {}
    proposal_total = (
        judge.get("proposal_judgment", {})
        .get("scores", {})
        .get("total", 0.0)
    )
    event_total = (
        judge.get("event_judgment", {})
        .get("scores", {})
        .get("total", 0.0)
    )
    healthy = judge.get("loop_state", {}).get("last_patch_healthy") is True
    protected = judge.get("loop_state", {}).get("source_protected") is True
    total = round((float(proposal_total or 0) + float(event_total or 0)) / 2, 4)
    return total, healthy, protected

def proposal_fingerprint(state):
    path = state.get("proposal_path", "")
    proposal = load(path, {})
    raw = json.dumps(proposal.get("ops", []), sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:12], proposal.get("proposal_id")

def run_cycle(index):
    auto = run([sys.executable, "-m", "runtime.auto_patch_loop_v120"])
    state = load(PATCH / "auto_patch_loop_state_v120.json", {})

    score, healthy, protected = score_from_auto_state(state)
    fp, proposal_id = proposal_fingerprint(state)

    return {
        "cycle": index,
        "auto_run": auto,
        "auto_status": state.get("status"),
        "auto_result": state.get("result"),
        "proposal_path": state.get("proposal_path"),
        "proposal_id": proposal_id,
        "proposal_fingerprint": fp,
        "score": score,
        "healthy": healthy,
        "source_protected": protected,
        "law": "v121_one_rapid_improvement_cycle",
    }

def main(argv=None):
    argv = argv or sys.argv[1:]

    cycles = MAX_DEFAULT_CYCLES
    if "--cycles" in argv:
        try:
            cycles = int(argv[argv.index("--cycles") + 1])
        except Exception:
            cycles = MAX_DEFAULT_CYCLES

    cycles = max(1, min(cycles, 5))

    if LOCK.exists():
        state = {
            "ts": time.time(),
            "status": "blocked_lock_exists",
            "lock": str(LOCK),
            "law": "v121_prevent_nested_rapid_loops",
        }
        print(json.dumps(state, indent=2, ensure_ascii=False))
        return 1

    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(str(time.time()), encoding="utf-8")

    event = {
        "ts": time.time(),
        "stage": "v121_multi_cycle_rapid_improvement",
        "requested_cycles": cycles,
        "completed_cycles": 0,
        "cycles": [],
        "stop_reason": None,
        "status": "started",
        "safety": {
            "max_cycles": cycles,
            "min_total_score": MIN_TOTAL_SCORE,
            "max_repeated_proposals": MAX_REPEATED_PROPOSALS,
            "source_protected_required": True,
            "healthy_required": True,
        },
        "law": "v121_capped_multi_cycle_auto_improvement",
    }

    try:
        previous_score = None
        seen = {}

        for i in range(1, cycles + 1):
            cycle = run_cycle(i)
            event["cycles"].append(cycle)
            event["completed_cycles"] = i

            fp = cycle.get("proposal_fingerprint")
            seen[fp] = seen.get(fp, 0) + 1

            if cycle.get("auto_status") != "auto_applied_healthy":
                event["stop_reason"] = f"auto status not healthy: {cycle.get('auto_status')}"
                event["status"] = "stopped_unhealthy"
                break

            if not cycle.get("healthy"):
                event["stop_reason"] = "patch judge did not mark latest patch healthy"
                event["status"] = "stopped_unhealthy"
                break

            if not cycle.get("source_protected"):
                event["stop_reason"] = "source protection not confirmed"
                event["status"] = "stopped_source_risk"
                break

            score = float(cycle.get("score") or 0.0)

            if score < MIN_TOTAL_SCORE:
                event["stop_reason"] = f"score below threshold: {score}"
                event["status"] = "stopped_score_low"
                break

            if previous_score is not None and score < previous_score:
                event["stop_reason"] = f"score dropped from {previous_score} to {score}"
                event["status"] = "stopped_score_drop"
                break

            if seen.get(fp, 0) > MAX_REPEATED_PROPOSALS:
                event["stop_reason"] = f"repeated proposal fingerprint: {fp}"
                event["status"] = "stopped_repetition"
                break

            previous_score = score

        else:
            event["status"] = "completed_cap"

        if not event.get("stop_reason"):
            event["stop_reason"] = "cycle cap reached cleanly"

        event["final_score"] = event["cycles"][-1]["score"] if event["cycles"] else 0
        event["final_health"] = event["cycles"][-1]["healthy"] if event["cycles"] else False
        event["source_protected"] = all(c.get("source_protected") for c in event["cycles"]) if event["cycles"] else False

        write(STATE, event)
        append(LOG, event)

        print(json.dumps(event, indent=2, ensure_ascii=False))
        return 0

    finally:
        try:
            LOCK.unlink()
        except Exception:
            pass

if __name__ == "__main__":
    raise SystemExit(main())

