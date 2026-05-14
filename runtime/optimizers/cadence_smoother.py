#!/usr/bin/env python3
from __future__ import annotations

import re

LAW = "smooth_conversational_flow"

REPEATS = [
    "That is why",
    "Something",
    "The system",
]

def smooth(text: str) -> str:

    out = text

    # remove repetitive openers
    lines = out.split(". ")

    cleaned = []

    seen = set()

    for line in lines:

        normalized = line.strip().lower()

        if normalized in seen:
            continue

        seen.add(normalized)

        cleaned.append(line.strip())

    out = ". ".join(cleaned)

    # soften robotic transitions
    out = re.sub(
        r'\bThat is why\b',
        'So',
        out
    )

    out = re.sub(r'\s+', ' ', out)

    return out.strip()

if __name__ == "__main__":

    sample = (
        "That is why the answer changes. "
        "That is why the answer changes. "
        "The system continues."
    )

    print(smooth(sample))

