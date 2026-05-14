import json
import statistics
import time
from pathlib import Path

ROOT = Path.home() / "point_vll_reassembled"

RUNTIME_PACKET = ROOT / "var/observability/runtime_packet.json"
OUT = ROOT / "var/observability/runtime_summary.json"

summary = {
    "ts": time.time(),
    "runtime_posture": "unknown",
    "dominant_renderer": "unknown",
    "coherence_trend": "unknown",
    "containment_status": "unknown",
    "mouth_integrity": "unknown",
    "ghost_risk": "unknown",
    "optimization_targets": [],
    "signals": {}
}

try:
    with open(RUNTIME_PACKET, "r") as f:
        packet = json.load(f)

    history = packet.get("runtime", {}).get(
        "stability_history",
        []
    )

    if history:

        recent = history[-8:]

        coherences = [
            x.get("coherence_estimate", 0)
            for x in recent
            if x.get("coherence_estimate") is not None
        ]

        containments = [
            x.get("shape_vector", {}).get("containment", 0)
            for x in recent
        ]

        renderers = [
            x.get("renderer_source", "unknown")
            for x in recent
        ]

        avg_coherence = round(
            statistics.mean(coherences),
            4
        ) if coherences else 0

        avg_containment = round(
            statistics.mean(containments),
            4
        ) if containments else 0

        dominant_renderer = max(
            set(renderers),
            key=renderers.count
        )

        summary["dominant_renderer"] = dominant_renderer

        summary["signals"]["avg_coherence"] = avg_coherence
        summary["signals"]["avg_containment"] = avg_containment

        if avg_coherence >= 0.70:
            summary["runtime_posture"] = "stable"
        elif avg_coherence >= 0.55:
            summary["runtime_posture"] = "transitional"
        else:
            summary["runtime_posture"] = "unstable"

        if avg_containment >= 0.60:
            summary["containment_status"] = "healthy"
        else:
            summary["containment_status"] = "weak"

        if dominant_renderer == "language_pass":
            summary["mouth_integrity"] = "stable"
        else:
            summary["mouth_integrity"] = "variable"

        summary["ghost_risk"] = "low"

        if avg_containment < 0.60:
            summary["optimization_targets"].append(
                "containment stabilization"
            )

        if avg_coherence < 0.72:
            summary["optimization_targets"].append(
                "coherence refinement"
            )

        if renderers.count(dominant_renderer) < len(renderers):
            summary["optimization_targets"].append(
                "renderer consolidation"
            )

except Exception as e:
    summary["error"] = str(e)

OUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUT, "w") as f:
    json.dump(summary, f, indent=2)

print("[OBSERVABILITY_SUMMARY_WRITTEN]")

