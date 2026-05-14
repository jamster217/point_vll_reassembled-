import json
import time
from pathlib import Path

ROOT = Path.home() / "point_vll_reassembled"

OUT = ROOT / "var/observability/route_selection_trace.json"

trace = {
    "ts": time.time(),

    "route_selection": {
        "prompt_type": "unknown",
        "selected_route": "unknown",
        "ordinary_escalation": False,
        "narration_pressure": 0.0,
        "knowledge_pressure": 0.0
    },

    "reasoning_observation": [],

    "recommendations": []
}

try:

    stability_path = ROOT / "var/v12_9/stability_history.json"

    with open(stability_path, "r") as f:
        history = json.load(f)

    latest = history[-1] if history else {}

    answer = str(latest.get("answer", "") or "")
    renderer = str(latest.get("renderer_source", "") or "")

    trace["route_selection"]["selected_route"] = renderer

    lower_answer = answer.lower()

    narration_markers = [
        "routing layer",
        "shape read",
        "reasoning_core",
        "larynx",
        "containment",
        "coherence",
        "mirror"
    ]

    factual_markers = [
        "because",
        "is caused by",
        "refers to",
        "happens when",
        "means that"
    ]

    narration_hits = sum(
        1 for x in narration_markers
        if x in lower_answer
    )

    factual_hits = sum(
        1 for x in factual_markers
        if x in lower_answer
    )

    narration_pressure = round(
        narration_hits / max(len(narration_markers), 1),
        4
    )

    knowledge_pressure = round(
        factual_hits / max(len(factual_markers), 1),
        4
    )

    trace["route_selection"]["narration_pressure"] = narration_pressure
    trace["route_selection"]["knowledge_pressure"] = knowledge_pressure

    if narration_pressure > knowledge_pressure:
        trace["route_selection"]["ordinary_escalation"] = False

        trace["reasoning_observation"].append(
            "structural narration dominating answer surface"
        )

        trace["recommendations"].append(
            "increase ordinary knowledge escalation sensitivity"
        )

    else:
        trace["route_selection"]["ordinary_escalation"] = True

        trace["reasoning_observation"].append(
            "ordinary knowledge mouth engaged successfully"
        )

    if "mirror" in lower_answer:
        trace["reasoning_observation"].append(
            "mirror-larynx influence detected"
        )

    if "routing layer" in lower_answer:
        trace["reasoning_observation"].append(
            "self-referential route narration leakage detected"
        )

except Exception as e:
    trace["error"] = str(e)

OUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUT, "w") as f:
    json.dump(trace, f, indent=2)

print("[ROUTE_SELECTION_TRACE_WRITTEN]")

