#!/usr/bin/env python3
from pathlib import Path
import json, time, math

STATE = Path("var/lattice/octa_harmonic_state.json")

def _load():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "phase_index": 0,
            "degrees": 0,
            "octa_nodes": [1.0] * 8,
            "last_output": None,
        }

def _save(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state

def _clamp(x, lo=0.0, hi=2.0):
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo

def shift(state_value=1.0):
    old = _load()
    phase = (int(old.get("phase_index", 0)) + 1) % 8
    degrees = phase * 45

    base = _clamp(state_value, 0.0, 2.0)

    # 8-node symbolic rotation field.
    nodes = []
    for i in range(8):
        angle = math.radians((i * 45 + degrees) % 360)
        val = base * (0.75 + 0.25 * math.cos(angle))
        nodes.append(round(_clamp(val), 3))

    packet = {
        "source": "runtime.octa_harmonic",
        "phase_index": phase,
        "degrees": degrees,
        "octa_nodes": nodes,
        "octa_mean": round(sum(nodes) / len(nodes), 3),
        "updated_at": time.time(),
    }

    return _save(packet)

def output(input_value=1.0):
    state = _load()
    mean = float(state.get("octa_mean", 1.0) or 1.0)
    out = round(_clamp(float(input_value) * mean), 3)

    state["last_output"] = {
        "input": input_value,
        "octa_mean": round(mean, 3),
        "output": out,
        "updated_at": time.time(),
    }

    return _save(state)

if __name__ == "__main__":
    import sys
    value = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    shift(value)
    print(json.dumps(output(value), indent=2, ensure_ascii=False))

