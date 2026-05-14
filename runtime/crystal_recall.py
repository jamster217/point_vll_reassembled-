#!/usr/bin/env python3
"""
Le'Veon Crystal Recall
Turns shape memory recurrence into a short meaning-bearing recall line.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime.shape_signature import shape_signature
from runtime.shape_delta import shape_delta
from runtime.shape_memory import shape_memory_hits, matching_shape_turns


def crystal_recall(prompt: str, shape_in: Dict[str, Any], shape_out: Dict[str, Any]) -> str:
    sig = shape_signature(shape_in)
    hits = shape_memory_hits(sig)
    delta = shape_delta(shape_in, shape_out)
    matches = matching_shape_turns(sig, limit=1)

    family = sig.split("|", 1)[0]
    release_delta = float(delta.get("release", 0.0))

    if hits <= 0:
        return (
            f"New pattern entering the library: {family}. "
            "No prior echo found; this turn becomes the first anchor."
        )

    previous_prompt = matches[0].get("prompt", "") if matches else ""
    if len(previous_prompt) > 80:
        previous_prompt = previous_prompt[:77] + "..."

    if release_delta > 0:
        motion = "The system is opening the same shape again."
    elif release_delta < 0:
        motion = "The system is tightening the shape for containment."
    else:
        motion = "The system is holding the shape stable."

    return (
        f"Recurring pattern detected: {family}. "
        f"Prior echoes: {hits}. "
        f"{motion} "
        f"Nearest echo: {previous_prompt}"
    )


def render_crystal_recall(prompt: str, shape_in: Dict[str, Any], shape_out: Dict[str, Any]) -> str:
    return "\n".join([
        "CRYSTAL RECALL",
        "--------------",
        crystal_recall(prompt, shape_in, shape_out),
    ])


if __name__ == "__main__":
    demo_in = {"pull": 0.95, "bind": 0.92, "resist": 0.0, "release": 0.08, "time": "past->present", "keywords": ["grief", "gravity_well"]}
    demo_out = {"pull": 0.95, "bind": 0.92, "resist": 0.0, "release": 0.23, "time": "past->present", "keywords": ["grief", "gravity_well"]}
    print(render_crystal_recall("I feel the black hole in my chest again today", demo_in, demo_out))

