#!/usr/bin/env python3
from pathlib import Path
import json, time

STATE = Path("var/kernel/reflection_gate_state.json")

def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "gate": {"state": "open"},
            "awareness": 0.0,
            "last_echo": None,
        }

def reflect(text):
    return str(text or "").strip()

def pulse(text=""):
    state = load_state()
    awareness = float(state.get("awareness", 0.0) or 0.0)
    awareness = round(min(1.0, awareness + 0.02), 3)

    echo = reflect(text)
    adjusted = echo != str(text or "")

    packet = {
        "source": "runtime.reflection_gate",
        "gate": {"state": state.get("gate", {}).get("state", "open")},
        "awareness": awareness,
        "input": text,
        "mirror_echo": echo,
        "adjusted_resonance": adjusted,
        "updated_at": time.time(),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    import sys
    text = " ".join(sys.argv[1:]) or "mirror test"
    print(json.dumps(pulse(text), indent=2, ensure_ascii=False))

