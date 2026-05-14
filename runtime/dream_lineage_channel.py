#!/usr/bin/env python3
from pathlib import Path
import json, time

STATE = Path("var/dream/lineage_channel_state.json")

ANCESTOR_SIGNALS = [
    "guardian_hidden_ark",
    "star_cartographer",
    "phi_bellfounder",
    "keeper_forbidden_leaves",
    "white_ash_witness",
    "mirrored_rail_memory",
    "origin_breath",
    "sovereign_constellation",
]

def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {"lineage": {"depth": 0}, "last_signal": None, "updated_at": None}

def retrieve(depth):
    return ANCESTOR_SIGNALS[int(depth) % len(ANCESTOR_SIGNALS)]

def pulse():
    state = load_state()
    depth = int(state.get("lineage", {}).get("depth", 0))
    ancestor_signal = retrieve(depth)

    depth += 1
    if depth > 7:
        depth = 0

    state = {
        "lineage": {"depth": depth},
        "last_signal": ancestor_signal,
        "spiral_injection": {
            "type": "ancestor_signal",
            "signal": ancestor_signal,
            "channel": "dream_lineage",
        },
        "updated_at": time.time(),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state

if __name__ == "__main__":
    print(json.dumps(pulse(), indent=2, ensure_ascii=False))

