import json
import time
from pathlib import Path
from collections import Counter

ROOT = Path.home() / "point_vll_reassembled"

RUNTIME_PACKET = ROOT / "var/observability/runtime_packet.json"
SUMMARY_PACKET = ROOT / "var/observability/runtime_summary.json"

OUT = ROOT / "var/observability/conflict_map.json"

conflicts = {
    "ts": time.time(),

    "renderer_conflicts": [],
    "containment_conflicts": [],
    "authority_conflicts": [],
    "sidecar_conflicts": [],

    "dominant_pressures": {},

    "stability_assessment": "unknown",

    "recommended_actions": []
}

try:

    with open(RUNTIME_PACKET, "r") as f:
        runtime_packet = json.load(f)

    with open(SUMMARY_PACKET, "r") as f:
        summary_packet = json.load(f)

    history = runtime_packet.get(
        "runtime",
        {}
    ).get(
        "stability_history",
        []
    )

    renderers = []
    coherence_values = []
    containment_values = []

    for turn in history[-20:]:

        renderers.append(
            turn.get("renderer_source", "unknown")
        )

        coherence_values.append(
            turn.get("coherence_estimate", 0)
        )

        containment_values.append(
            turn.get("shape_vector", {}).get(
                "containment",
                0
            )
        )

    renderer_counts = Counter(renderers)

    if len(renderer_counts) > 1:
        conflicts["renderer_conflicts"].append({
            "type": "multi_renderer_presence",
            "renderers": dict(renderer_counts)
        })

    avg_coherence = (
        sum(coherence_values) / len(coherence_values)
        if coherence_values else 0
    )

    avg_containment = (
        sum(containment_values) / len(containment_values)
        if containment_values else 0
    )

    conflicts["dominant_pressures"] = {
        "avg_coherence": round(avg_coherence, 4),
        "avg_containment": round(avg_containment, 4)
    }

    if avg_containment < 0.55:
        conflicts["containment_conflicts"].append({
            "type": "weak_containment",
            "severity": "moderate"
        })

    if avg_coherence < 0.65:
        conflicts["authority_conflicts"].append({
            "type": "coherence_fragmentation",
            "severity": "moderate"
        })

    dominant_renderer = summary_packet.get(
        "dominant_renderer",
        "unknown"
    )

    if dominant_renderer == "language_pass":
        conflicts["stability_assessment"] = "stable_governed_route"
    else:
        conflicts["stability_assessment"] = "unstable_renderer_rotation"

    if avg_containment < 0.55:
        conflicts["recommended_actions"].append(
            "reduce mouth redundancy"
        )

    if len(renderer_counts) > 1:
        conflicts["recommended_actions"].append(
            "consolidate renderer authority"
        )

    if avg_coherence < 0.65:
        conflicts["recommended_actions"].append(
            "improve route synchronization"
        )

except Exception as e:
    conflicts["error"] = str(e)

OUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUT, "w") as f:
    json.dump(conflicts, f, indent=2)

print("[CONFLICT_MAP_WRITTEN]")

