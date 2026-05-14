from __future__ import annotations

import json
from pathlib import Path

PATHS = [
    "logs/v12_9/helm/helm_reflection_turns.jsonl",
    "logs/v12_9/helm/helm_reflection_rankings.jsonl",
    "logs/v12_9/helm/liberal_helm_events.jsonl",
    "logs/v12_9/ghost/ghost_entries.jsonl",
    "logs/serpent_guard/serpent_guard_events.jsonl",
    "logs/v12_9/resonance/telepathic_resonance_events.jsonl",
    "logs/v12_9/occult/occult_amplification_events.jsonl",
    "logs/symbolic_bridge/spiral_memory_nonlinear.jsonl",
]

def print_bar(title: str = ""):
    print("=" * 100)
    if title:
        print(title)
        print("=" * 100)

for raw_path in PATHS:
    path = Path(raw_path)

    print_bar(f"FILE: {raw_path}")

    if not path.exists():
        print("MISSING")
        print()
        continue

    lines = [x for x in path.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()]
    print(f"ENTRY_COUNT: {len(lines)}")
    print()

    for idx, line in enumerate(lines, 1):
        print(f"--- ENTRY LINE {idx} ---")
        try:
            obj = json.loads(line)
            print(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True))
        except Exception as e:
            print("JSON_PARSE_ERROR:", repr(e))
            print(line)
        print()

print_bar("READOUT COMPLETE")
