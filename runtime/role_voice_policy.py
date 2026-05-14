#!/usr/bin/env python3
"""
Le'Veon Role Voice Policy
Uses Crystal Family Role to shape the final local Savariel voice.
"""

from __future__ import annotations

from typing import Any, Dict


def apply_role_voice(prompt: str, base_voice: str, role_info: Dict[str, Any]) -> str:
    role = str(role_info.get("role", "unknown"))
    family = str(role_info.get("family", "unknown"))
    turns = int(role_info.get("turns", 0) or 0)

    base_voice = (base_voice or "").strip()

    if role == "stable_diagnostic":
        addition = (
            f" The family {family} is stable enough to compare across turns. "
            "Use it as a measuring instrument: change one phrase, run again, and watch whether the same signature returns."
        )
    elif role == "transformative_opener":
        addition = (
            f" The family {family} opens the field rather than merely naming it. "
            "The signal is not only recognition; it is release moving through the same structure."
        )
    elif role == "seed_pattern":
        addition = (
            f" The family {family} has only begun to form. "
            "Seed it with varied prompts before trusting its role."
        )
    elif role == "emerging_pattern":
        addition = (
            f" The family {family} is still unstable. "
            "Do not lock it yet; test it through paraphrase."
        )
    else:
        addition = (
            " The family role is not yet clear. "
            "Record more turns before treating this as a known pattern."
        )

    # Avoid double-appending if rerun or imported strangely.
    if addition.strip() in base_voice:
        return base_voice

    return base_voice + addition


if __name__ == "__main__":
    demo = {
        "family": "build_path",
        "role": "stable_diagnostic",
        "turns": 4,
    }
    print(apply_role_voice("demo", "The next repair is clearer routing.", demo))

