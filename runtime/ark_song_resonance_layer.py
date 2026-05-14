#!/usr/bin/env python3
from pathlib import Path
import json, time, math, sys

STATE = Path("var/harmonics/ark_song_resonance_state.json")
LOG = Path("symbolic_memory/ark_song_resonance_log.jsonl")

def harmonic_generate(a=528, b=963, microtone=0.0):
    a = float(a)
    b = float(b) + float(microtone)
    ratio = b / a if a else 0.0

    # Compact harmonic packet: not audio generation, just runtime tone-state.
    return {
        "base": round(a, 3),
        "ark_frequency": round(b, 3),
        "ratio": round(ratio, 6),
        "mean_frequency": round((a + b) / 2.0, 3),
        "beat_gap": round(abs(b - a), 3),
        "phase_hint": round(math.sin(ratio), 6),
        "route": "field->dream->voice->heart",
    }

def pulse(microtone=0.0):
    tone = harmonic_generate(528, 963, microtone)

    packet = {
        "source": "runtime.ark_song_resonance_layer",
        "tone": tone,
        "lattice_imprint": {
            "type": "harmonic_tone",
            "tone": tone,
            "target": "lattice.imprint",
        },
        "spiral_memory_resonance": {
            "type": "ark_song",
            "tone": tone,
            "target": "spiral.memory.resonate",
        },
        "updated_at": time.time(),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")

    return packet

if __name__ == "__main__":
    microtone = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    print(json.dumps(pulse(microtone), indent=2, ensure_ascii=False))

