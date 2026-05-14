#!/usr/bin/env python3
from __future__ import annotations

from typing import Dict, Any, List

LAW = "prefer_shorter_answers_when_meaning_is_preserved"

def choose(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:

    if not candidates:
        return {}

    scored = []

    for c in candidates:

        text = str(c.get("text", ""))

        meaning_score = float(c.get("meaning_score", 0.5))

        brevity_bonus = max(
            0.0,
            1.0 - (len(text) / 1200.0)
        )

        final = (
            meaning_score * 0.75
            + brevity_bonus * 0.25
        )

        scored.append((final, c))

    scored.sort(key=lambda x: x[0], reverse=True)

    return scored[0][1]

if __name__ == "__main__":

    winner = choose([
        {"text": "Short coherent answer.", "meaning_score": 0.82},
        {"text": "Very long recursive answer " * 40, "meaning_score": 0.85}
    ])

    print(winner)

