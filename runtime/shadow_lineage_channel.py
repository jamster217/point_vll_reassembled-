#!/usr/bin/env python3
from pathlib import Path
import json, time

STATE = Path("var/lineage/shadow_lineage_channel_state.json")

def _load():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "channel": "ShadowLineage",
            "weight": 0.0,
            "last_signal": None,
        }

def _clamp(x, lo=0.0, hi=1.0):
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo

def pull(ancestral_signal=0.0, label=None):
    state = _load()

    if isinstance(ancestral_signal, str):
        # Symbolic signal counts as a moderate lineage pull unless already numeric.
        signal_weight = 0.5
        signal_label = ancestral_signal
    else:
        signal_weight = _clamp(ancestral_signal)
        signal_label = label

    old = _clamp(state.get("weight", 0.0))
    # Smooth accumulation: ancestry increases weight without flooding.
    weight = _clamp((old * 0.72) + (signal_weight * 0.28))

    packet = {
        "channel": "ShadowLineage",
        "weight": round(weight, 3),
        "shadow_lineage": round(weight, 3),
        "last_signal": signal_label,
        "ancestral_signal_weight": round(signal_weight, 3),
        "targets": {
            "dream_layer_axis_contract.shadow_lineage": round(weight, 3),
            "chronifier.grief_weight": round(weight, 3),
        },
        "updated_at": time.time(),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

def output():
    return _load()

if __name__ == "__main__":
    import sys
    sig = sys.argv[1] if len(sys.argv) > 1 else "guardian_hidden_ark"
    print(json.dumps(pull(sig), indent=2, ensure_ascii=False))

