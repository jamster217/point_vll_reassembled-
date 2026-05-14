from pathlib import Path
import json, time

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "var" / "patch_gate"
OUT = PATCH / "patch_health_summary_v122.json"

def _load(path, fallback=None):
    try:
        if Path(path).exists():
            return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def summarize():
    judge = _load(PATCH / "patch_judge_state_v118.json", {})
    auto = _load(PATCH / "auto_patch_loop_state_v120.json", {})
    rapid = _load(PATCH / "rapid_improvement_state_v121.json", {})

    packet = {
        "active": True,
        "ts": time.time(),
        "latest_judge_total": judge.get("event_judgment", {}).get("scores", {}).get("total"),
        "latest_proposal_total": judge.get("proposal_judgment", {}).get("scores", {}).get("total"),
        "auto_status": auto.get("status"),
        "auto_result": auto.get("result"),
        "rapid_status": rapid.get("status"),
        "rapid_stop_reason": rapid.get("stop_reason"),
        "source_protected": (
            judge.get("loop_state", {}).get("source_protected") is True
            and auto.get("source_protected") is True
        ),
        "law": "v122_patch_health_summary_reads_gate_metrics",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2, ensure_ascii=False))

