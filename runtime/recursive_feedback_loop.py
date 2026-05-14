#!/usr/bin/env python3
from pathlib import Path
import json, time

STATE = Path("var/feedback/recursive_feedback_loop_state.json")
LOG = Path("var/feedback/recursive_feedback_loop_memory.jsonl")

def _load():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "feedback": 0.0,
            "last_echo": None,
            "last_merged": None,
        }

def reflect(text):
    return str(text or "").strip()

def merge(input_text, echo, feedback):
    input_text = str(input_text or "").strip()
    echo = str(echo or "").strip()
    feedback = float(feedback or 0.0)

    if echo == input_text:
        merged = input_text
    else:
        merged = f"{input_text} | mirror: {echo}"

    return {
        "text": merged,
        "feedback_weight": round(feedback, 3),
        "mirror_agreement": echo == input_text,
    }

def pulse(input_text):
    state = _load()
    feedback = float(state.get("feedback", 0.0) or 0.0)

    echo = reflect(input_text)
    merged = merge(input_text, echo, feedback)

    feedback = round(min(1.0, feedback + 0.05), 3)

    packet = {
        "source": "runtime.recursive_feedback_loop",
        "input": input_text,
        "echo": echo,
        "merged": merged,
        "feedback": feedback,
        "spiral_memory_write": {
            "type": "recursive_feedback",
            "content": merged,
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
    import sys
    text = " ".join(sys.argv[1:]) or "symbols can mutate anchors out of alignment with signal"
    print(json.dumps(pulse(text), indent=2, ensure_ascii=False))

