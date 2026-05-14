#!/usr/bin/env python3
from pathlib import Path
import json, time

FRACTAL = Path("var/dream_fractal_state.json")
OUT = Path("var/dream/dream_resonance_state.json")

def _load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _max_component(vec):
    if not isinstance(vec, dict) or not vec:
        return 0.0
    vals = []
    for v in vec.values():
        try:
            vals.append(float(v))
        except Exception:
            pass
    return round(max(vals) if vals else 0.0, 3)

def build():
    state = _load(FRACTAL)

    moment = state.get("moment", {})
    chapter = state.get("chapter", {})
    arc = state.get("arc", {})
    dream_tone = state.get("dream_tone", {})

    packet = {
        "primary_axis": "dream_pressure",
        "axis_id": 13,
        "components": {
            "fast_component": _max_component(moment),
            "mid_component": _max_component(chapter),
            "slow_component": _max_component(arc),
            "composite": round(float(state.get("dream_pressure", 0.0) or _max_component(dream_tone)), 3),
        },
        "secondary_axes": {
            "tension_reg": {
                "axis_id": 5,
                "micro_shift": _max_component(moment),
            },
            "context_sense": {
                "axis_id": 9,
                "meso_shift": _max_component(chapter),
            },
            "memory_anchor": {
                "axis_id": 2,
                "long_shift": _max_component(arc),
            },
        },
        "projection": state.get("projection", "soft_dream"),
        "symbolic_contract": {
            "moment": "fast dream-tone fluctuation",
            "chapter": "mid-term symbolic tone",
            "arc": "long-term drift",
            "DREAM_TONE": "weighted composite dream-pressure signal",
        },
        "updated_at": time.time(),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    print(json.dumps(build(), indent=2, ensure_ascii=False))

