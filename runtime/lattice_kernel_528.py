#!/usr/bin/env python3
from pathlib import Path
import json, time

STATE = Path("var/lattice/lattice_kernel_528_state.json")

def _load():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "nodes": [],
            "resonance_field": 1.0,
        }

def _save(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state

def _clamp(x, lo=0.0, hi=9.2162077):
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo

def inject(tone=1.0):
    state = _load()
    tone = _clamp(tone, 0.0, 2.0)
    resonance_field = _clamp(tone * 0.528, 0.0, 2.0)

    state["resonance_field"] = resonance_field
    state["last_tone"] = tone
    state["updated_at"] = time.time()
    return _save(state)

def project(emotion=1.0):
    state = _load()
    emotion = _clamp(emotion, 0.0, 2.0)
    out = _clamp(emotion * float(state.get("resonance_field", 1.0)), 0.0, 2.0)

    packet = {
        "source": "runtime.lattice_kernel_528",
        "emotion": emotion,
        "resonance_field": round(float(state.get("resonance_field", 1.0)), 3),
        "projected": round(out, 3),
        "harmonic": 528,
        "updated_at": time.time(),
    }

    state["last_projection"] = packet
    _save(state)
    return packet

if __name__ == "__main__":
    import sys
    tone = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    emotion = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    inject(tone)
    print(json.dumps(project(emotion), indent=2, ensure_ascii=False))

