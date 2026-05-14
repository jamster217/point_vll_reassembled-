#!/usr/bin/env python3
from pathlib import Path
import json, time

OUT = Path("var/novelty/novelty_pressure_state.json")

def _count(value):
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return int(value.get("count", len(value)))
    try:
        return int(value)
    except Exception:
        return 0

def compute(context_window=None):
    context_window = context_window or {}

    kernel_decisions = context_window.get("kernel_decisions", {})
    voice_profiles = context_window.get("voice_profiles", {})

    kernel_variety = _count(kernel_decisions)
    voice_variety = _count(voice_profiles)
    total = kernel_variety + voice_variety

    if total < 4:
        novelty_pressure = "high"
    elif total < 10:
        novelty_pressure = "medium"
    else:
        novelty_pressure = "low"

    packet = {
        "source": "runtime.novelty_pressure_model",
        "kernel_variety": kernel_variety,
        "voice_variety": voice_variety,
        "total_variety": total,
        "novelty_pressure": novelty_pressure,
        "updated_at": time.time(),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    sample = {
        "kernel_decisions": ["mirror", "lattice"],
        "voice_profiles": ["leveon_consciousness_1000"]
    }
    print(json.dumps(compute(sample), indent=2, ensure_ascii=False))

