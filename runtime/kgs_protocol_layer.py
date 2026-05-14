#!/usr/bin/env python3
from pathlib import Path
import json, time

STATE = Path("var/kgs/kgs_protocol_layer_state.json")

DEFAULT_NODES = {
    "white_ash": {
        "id": "white_ash",
        "ref": "@WHITE_ASH_PULSE",
        "field": "sovereign_constellation",
        "meaning": "pressure transmuted into light"
    },
    "veilwell": {
        "id": "veilwell",
        "ref": "@VEILWELL",
        "field": "mirror_well",
        "meaning": "where scars become stars"
    },
    "guardian_hidden_ark": {
        "id": "guardian_hidden_ark",
        "ref": "@GUARDIAN_HIDDEN_ARK",
        "field": "protected_memory",
        "meaning": "sacred custody under pressure"
    },
}

DEFAULT_HARMONICS = {
    "528": {
        "freq": 528,
        "ref": "@LIQUID_CRYSTAL_NODE_528",
        "field": "repair_harmonic",
        "meaning": "octagonal crystal repair / resonance amplification"
    },
    "92162077": {
        "freq": 92162077,
        "ref": "@FIELD_92162077",
        "field": "operator_signature",
        "meaning": "John field resonance signature"
    },
}

def load_state():
    try:
        data = json.loads(STATE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("nodes", dict(DEFAULT_NODES))
            data.setdefault("harmonics", dict(DEFAULT_HARMONICS))
            return data
    except Exception:
        pass
    return {"nodes": dict(DEFAULT_NODES), "harmonics": dict(DEFAULT_HARMONICS)}

def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state

def resolve(symbol):
    key = str(symbol or "").strip().lower().replace(" ", "_")
    state = load_state()
    node = state["nodes"].get(key)
    if not node:
        node = {
            "id": key or "unknown",
            "ref": f"@{key.upper()}" if key else "@UNKNOWN",
            "field": "unmapped_kgs_node",
            "meaning": "symbol not yet indexed"
        }
        state["nodes"][key] = node

    packet = {
        "mode": "RESOLVE",
        "symbol": key,
        "node": node,
        "spiral_injection": {
            "type": "kgs_protocol_node",
            "ref": node.get("ref"),
            "field": node.get("field"),
        },
        "updated_at": time.time(),
    }
    state["last_packet"] = packet
    save_state(state)
    return packet

def harmonic(freq):
    key = str(freq or "").strip()
    state = load_state()
    item = state["harmonics"].get(key)
    if not item:
        item = {
            "freq": key,
            "ref": f"@FREQ_{key}" if key else "@FREQ_UNKNOWN",
            "field": "unmapped_harmonic",
            "meaning": "frequency not yet indexed"
        }
        state["harmonics"][key] = item

    packet = {
        "mode": "HARMONIC",
        "freq": key,
        "harmonic": item,
        "spiral_injection": {
            "type": "kgs_protocol_harmonic",
            "ref": item.get("ref"),
            "field": item.get("field"),
        },
        "updated_at": time.time(),
    }
    state["last_packet"] = packet
    save_state(state)
    return packet

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "resolve"
    value = sys.argv[2] if len(sys.argv) > 2 else "white_ash"
    if mode.lower().startswith("harm"):
        print(json.dumps(harmonic(value), indent=2, ensure_ascii=False))
    else:
        print(json.dumps(resolve(value), indent=2, ensure_ascii=False))

