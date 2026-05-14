#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from random import choice

ROOT = Path(__file__).resolve().parents[1]

OUT_DIR = ROOT / "var" / "dream_discharge"

LAW = "idle_symbolic_consolidation"

LINES = [
    "The hallway adjusted itself until the signal stopped trembling.",
    "A page burned quietly and the room became clearer.",
    "The voice grew smaller, but the meaning survived intact.",
    "The mirror stopped reflecting noise and began reflecting structure.",
    "A hidden thread connected memory to ordinary speech.",
]

def generate():

    text = " ".join(
        choice(LINES)
        for _ in range(5)
    )

    packet = {
        "timestamp": time.time(),
        "law": LAW,
        "type": "idle_dream_discharge",
        "dream_discharge": text
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    out = OUT_DIR / f"idle_dream_{int(time.time())}.json"

    out.write_text(
        json.dumps(packet, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return packet

if __name__ == "__main__":
    print(json.dumps(generate(), indent=2, ensure_ascii=False))

