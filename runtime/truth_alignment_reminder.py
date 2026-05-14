#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

LAW_PATH = Path(__file__).with_name("truth_alignment_law.json")

def load_truth_alignment_law() -> dict:
    if not LAW_PATH.exists():
        return {
            "name": "Le'Veon Truth Alignment Law",
            "reminder": "Truth over comfort. Prompt-bound answer over generic answer."
        }
    return json.loads(LAW_PATH.read_text())

def truth_alignment_reminder() -> str:
    law = load_truth_alignment_law()
    lines = [
        law.get("name", "Truth Alignment Law"),
        "",
        law.get("reminder", ""),
        "",
        "Core law:"
    ]
    for item in law.get("law", []):
        lines.append(f"- {item}")
    return "\n".join(lines).strip()

if __name__ == "__main__":
    print(truth_alignment_reminder())

