from __future__ import annotations

import re
from typing import Any, Dict

from runtime.performance_routing_oracle import choose_algorithm


def estimate_prompt_density(
    prompt: str,
    previous_reply: str = "",
    tone: str = "",
    mirror_mode: str = "",
) -> Dict[str, Any]:
    """
    Estimate symbolic/input density for routing.

    This is intentionally lightweight for Termux:
    - word count
    - character count
    - symbolic marker count
    - newline count
    - prior-reply carryover
    """
    prompt = str(prompt or "")
    previous_reply = str(previous_reply or "")

    words = re.findall(r"\b[\w'-]+\b", prompt)
    chars = len(prompt)
    lines = prompt.count("\n") + 1 if prompt else 0

    symbolic_markers = [
        "node", "spiral", "sigil", "field", "glyph", "lattice",
        "oracle", "route", "benchmark", "performance", "algorithm",
        "witness", "bloom", "core", "92162077"
    ]

    low = prompt.lower()
    marker_hits = sum(low.count(m) for m in symbolic_markers)

    # N is not raw word count only. It is an estimated symbolic load.
    estimated_n = (
        len(words)
        + int(chars / 12)
        + marker_hits * 8
        + lines * 2
        + int(len(previous_reply) / 40)
    )

    return {
        "estimated_n": max(1, int(estimated_n)),
        "word_count": len(words),
        "char_count": chars,
        "line_count": lines,
        "symbolic_marker_hits": marker_hits,
        "tone": tone,
        "mirror_mode": mirror_mode,
    }


def route_prompt_load(
    prompt: str,
    previous_reply: str = "",
    tone: str = "",
    mirror_mode: str = "",
) -> Dict[str, Any]:
    density = estimate_prompt_density(
        prompt=prompt,
        previous_reply=previous_reply,
        tone=tone,
        mirror_mode=mirror_mode,
    )

    route = choose_algorithm(density["estimated_n"])

    return {
        "density": density,
        "selected_algorithm": route["selected_algorithm"],
        "verification_needed": route["verification_needed"],
        "reason": route["reason"],
        "route": route,
    }

