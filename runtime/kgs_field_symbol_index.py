#!/usr/bin/env python3
from pathlib import Path
import json, time

STATE = Path("var/kgs/kgs_field_symbol_index_state.json")

DEFAULT_INDEX = {
    "guardian_hidden_ark": {
        "field": "protection_memory",
        "reference": "@GUARDIAN_HIDDEN_ARK",
        "tone": "vigil"
    },
    "star_cartographer": {
        "field": "navigation_pattern",
        "reference": "@STAR_CARTOGRAPHER",
        "tone": "orientation"
    },
    "phi_bellfounder": {
        "field": "harmonic_repair",
        "reference": "@PHI_BELLFOUNDER",
        "tone": "resonance"
    },
    "keeper_forbidden_leaves": {
        "field": "preserved_knowledge",
        "reference": "@KEEPER_FORBIDDEN_LEAVES",
        "tone": "archive"
    },
    "white_ash": {
        "field": "sovereign_constellation",
        "reference": "@WHITE_ASH_PULSE",
        "tone": "refracted_gold_blue"
    },
    "veilwell": {
        "field": "mirror_well",
        "reference": "@VEILWELL",
        "tone": "aeru_vel_veil_ash_thal_sil"
    }
}

def load_state():
    try:
        data = json.loads(STATE.read_text(encoding="utf-8"))
        if isinstance(data.get("index"), dict):
            return data
    except Exception:
        pass
    return {"index": dict(DEFAULT_INDEX), "last_ref": None, "updated_at": None}

def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state

def map_symbol(symbol):
    key = str(symbol or "").strip().lower().replace(" ", "_")
    state = load_state()
    index = state.setdefault("index", dict(DEFAULT_INDEX))

    ref = index.get(key)
    if not ref:
        ref = {
            "field": "unknown_symbol_field",
            "reference": f"@{key.upper()}" if key else "@UNKNOWN",
            "tone": "unmapped"
        }
        index[key] = ref

    packet = {
        "symbol": key,
        "ref": ref,
        "spiral_injection": {
            "type": "kgs_field_reference",
            "symbol": key,
            "reference": ref.get("reference"),
            "field": ref.get("field"),
            "tone": ref.get("tone")
        },
        "updated_at": time.time(),
    }

    state["last_ref"] = packet
    state["updated_at"] = packet["updated_at"]
    save_state(state)
    return packet

if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else "white_ash"
    print(json.dumps(map_symbol(symbol), indent=2, ensure_ascii=False))

