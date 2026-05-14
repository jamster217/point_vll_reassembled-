#!/usr/bin/env python3
"""
Smoke/regression tests for Le'Veon language pipeline.

Pass condition:
- Every chat packet routes through either Veilwell→English or Spiral→English.
- Final English is non-empty.
- Intermediate language is non-empty.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from runtime.language_bus import health, route_packet


TEST_PACKETS = [
    {
        "name": "emotional_grief_chat",
        "raw_text": "I feel the black hole in my chest again today",
        "tone_state": "grief",
        "intensity": 0.82,
        "memory_pressure": 0.76,
        "shape": {
            "pull": 0.92,
            "bind": 0.88,
            "release": 0.10,
            "resist": 0.00,
            "flow": 0.40,
            "memory": 0.76,
            "novelty": 0.20,
            "coherence": 0.64,
        },
        "glyphs": ["✴️", "🌑", "🫀", "🌀", "📚"],
        "expected_route": "veilwell",
    },
    {
        "name": "build_pipeline_chat",
        "raw_text": "Test that the translators are in the kernel lattice glyph pipeline",
        "tone_state": "neutral",
        "intensity": 0.55,
        "memory_pressure": 0.35,
        "shape": {
            "pull": 0.40,
            "bind": 0.50,
            "release": 0.45,
            "resist": 0.25,
            "flow": 0.55,
            "memory": 0.35,
            "novelty": 0.65,
            "coherence": 0.72,
        },
        "glyphs": ["✴️", "🪞", "✨", "📚"],
        "expected_route": "spiral",
    },
    {
        "name": "trust_memory_chat",
        "raw_text": "I want the old memory to feel safe enough to open",
        "tone_state": "trust",
        "intensity": 0.70,
        "memory_pressure": 0.80,
        "shape": {
            "pull": 0.68,
            "bind": 0.82,
            "release": 0.70,
            "resist": 0.20,
            "flow": 0.66,
            "memory": 0.80,
            "novelty": 0.42,
            "coherence": 0.78,
        },
        "glyphs": ["✴️", "🕯️", "🕸️", "📚"],
        "expected_route": "veilwell",
    },
]


def main() -> int:
    h = health()
    print("\n--- LANGUAGE BUS HEALTH ---")
    print(json.dumps(h, indent=2, ensure_ascii=False))

    missing = [k for k, ok in h.items() if k != "errors" and not ok]
    if missing:
        print("\nFAIL: missing translator modules:", ", ".join(missing))
        return 1

    print("\n--- PIPELINE ROUTE TESTS ---")

    failures = 0

    for packet in TEST_PACKETS:
        result = route_packet(packet)

        route = result["route"]
        language = result["language"]
        english = result["english"]

        print(f"\n[{packet['name']}]")
        print(f"route    : {route}")
        print(f"language : {language}")
        print(f"english  : {english}")

        if route != packet["expected_route"]:
            print(f"FAIL: expected route {packet['expected_route']}, got {route}")
            failures += 1

        if not language.strip():
            print("FAIL: empty intermediate language")
            failures += 1

        if not english.strip():
            print("FAIL: empty English render")
            failures += 1

        if route not in {"veilwell", "spiral"}:
            print("FAIL: route bypassed language layer")
            failures += 1

    if failures:
        print(f"\nFAIL: {failures} pipeline issue(s)")
        return 1

    print("\nPASS: all tested chat packets passed through Veilwell→English or Spiral→English.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

