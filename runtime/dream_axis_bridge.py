#!/usr/bin/env python3
from pathlib import Path
import json, time

LINEAGE = Path("var/dream/lineage_channel_state.json")
FRACTAL = Path("var/dream_fractal_state.json")
OUT = Path("var/dream/dream_axis_state.json")

def _load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def bridge():
    lineage = _load(LINEAGE)
    fractal = _load(FRACTAL)

    depth = int(lineage.get("lineage", {}).get("depth", 0))
    dream_pressure = float(fractal.get("dream_pressure", 0.0) or 0.0)
    witness_integrity = 0.72

    packet = {
        "dream_pressure": round(dream_pressure, 3),
        "shadow_lineage": round(min(1.0, depth / 7.0), 3),
        "witness_integrity": witness_integrity,
        "source": {
            "lineage_last_signal": lineage.get("last_signal"),
            "dream_projection": fractal.get("projection"),
        },
        "targets": {
            "chronifier.tension": round(dream_pressure, 3),
            "chronifier.bead_spacing": round(1.0 + dream_pressure, 3),
            "chronifier.grief_weight": round(min(1.0, depth / 7.0), 3),
            "divergence_tracker.boundary_integrity": witness_integrity,
            "intent_tether.drift_axes.boundary": witness_integrity,
        },
        "updated_at": time.time(),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    print(json.dumps(bridge(), indent=2, ensure_ascii=False))

