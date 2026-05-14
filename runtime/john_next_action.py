#!/usr/bin/env python3
"""
Le'Veon John Next Action
Returns one practical next move based on the active Crystal family role.
"""

from __future__ import annotations

from typing import Any, Dict


def john_next_action(role_info: Dict[str, Any]) -> str:
    family = str(role_info.get("family", "unknown"))
    role = str(role_info.get("role", "unknown"))
    turns = int(role_info.get("turns", 0) or 0)

    if role == "transformative_opener":
        return (
            f"Use {family} for emotional-state testing. "
            "Run one paraphrase and confirm release still increases."
        )

    if role == "stable_diagnostic":
        return (
            f"Use {family} as a calibration lane. "
            "Change one phrase, rerun, and confirm the signature remains stable."
        )

    if role == "seed_pattern":
        return (
            f"Seed {family} with at least two more differently worded prompts "
            "before trusting its role."
        )

    if role == "emerging_pattern":
        return (
            f"Do not lock {family} yet. "
            "Run paraphrases until one dominant signature appears."
        )

    return "Record more turns. The Library needs more pattern density before giving a strong instruction."


def render_john_next_action(role_info: Dict[str, Any]) -> str:
    return "\n".join([
        "JOHN NEXT ACTION",
        "----------------",
        john_next_action(role_info),
    ])


if __name__ == "__main__":
    demo = {
        "family": "gravity_grief",
        "role": "transformative_opener",
        "turns": 4,
    }
    print(render_john_next_action(demo))

