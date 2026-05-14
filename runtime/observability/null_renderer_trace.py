import json
import time
from pathlib import Path

ROOT = Path.home() / "point_vll_reassembled"

RUNTIME_PACKET = ROOT / "var/observability/runtime_packet.json"
OUT = ROOT / "var/observability/null_renderer_trace.json"

trace = {
    "ts": time.time(),
    "null_renderer_events": [],
    "summary": {
        "total_nulls": 0,
        "suspected_cause": [],
        "dominant_patterns": []
    }
}

try:

    with open(RUNTIME_PACKET, "r") as f:
        packet = json.load(f)

    history = packet.get(
        "runtime",
        {}
    ).get(
        "stability_history",
        []
    )

    for idx, turn in enumerate(history):

        renderer = turn.get("renderer_source")

        if renderer in [None, "null", "unknown"]:

            event = {
                "index": idx,
                "ts": turn.get("ts"),
                "answer_mode": turn.get("answer_mode"),
                "status": turn.get("status"),
                "live_mouth_bridge_status":
                    turn.get("live_mouth_bridge_status"),
                "ordinary_bridge_status":
                    turn.get("ordinary_bridge_status"),
                "coherence_estimate":
                    turn.get("coherence_estimate"),
                "answer_preview":
                    str(turn.get("answer", ""))[:140]
            }

            if idx > 0:
                prev_turn = history[idx - 1]

                event["previous_renderer"] = prev_turn.get(
                    "renderer_source"
                )

                event["previous_coherence"] = prev_turn.get(
                    "coherence_estimate"
                )

            trace["null_renderer_events"].append(event)

    trace["summary"]["total_nulls"] = len(
        trace["null_renderer_events"]
    )

    if trace["summary"]["total_nulls"] > 0:
        trace["summary"]["suspected_cause"].append(
            "renderer assignment bypass"
        )

        trace["summary"]["suspected_cause"].append(
            "fallback route leakage"
        )

        trace["summary"]["dominant_patterns"].append(
            "governed route mostly survives"
        )

except Exception as e:
    trace["error"] = str(e)

OUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUT, "w") as f:
    json.dump(trace, f, indent=2)

print("[NULL_RENDERER_TRACE_WRITTEN]")

