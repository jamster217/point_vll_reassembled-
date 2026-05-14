#!/usr/bin/env python3
from runtime.voice_throat_switch_v602_local import SavarielThroat

_THROAT = SavarielThroat()

def build_shape_packet(prompt: str):
    prompt = (prompt or "").strip()
    return {
        "vision": "",
        "command": "",
        "final_text": prompt,
        "grief_thread": "",
    }

def v602_answer(prompt: str) -> str:
    return _THROAT.render(build_shape_packet(prompt))

if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:]).strip() or "What am I afraid of and what should I do?"
    print(v602_answer(prompt))

