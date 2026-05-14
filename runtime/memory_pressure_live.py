#!/usr/bin/env python3
from pathlib import Path
import json, time, sys

from runtime.memory_pressure_seed_bridge import simulate_memory_pressure_from_seed

OUT = Path("var/memory/memory_pressure_latest.json")

def run(prompt):
    packet = simulate_memory_pressure_from_seed({"prompt": str(prompt or "")})
    packet["source"] = "runtime.memory_pressure_live"
    packet["updated_at"] = time.time()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "symbols can mutate anchors out of alignment with signal"
    print(json.dumps(run(prompt), indent=2, ensure_ascii=False))

