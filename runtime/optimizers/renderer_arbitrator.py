#!/usr/bin/env python3
from __future__ import annotations

from typing import Dict, Any

LAW = "renderer_must_preserve_upstream_signal"

def arbitrate(
    *,
    upstream: str,
    rendered: str
) -> Dict[str, Any]:

    upstream_words = set(upstream.lower().split())
    rendered_words = set(rendered.lower().split())

    overlap = len(
        upstream_words.intersection(rendered_words)
    )

    denom = max(1, len(upstream_words))

    fidelity = overlap / denom

    approved = fidelity >= 0.35

    return {
        "law": LAW,
        "approved": approved,
        "fidelity": round(fidelity, 3),
        "upstream_length": len(upstream),
        "rendered_length": len(rendered),
    }

if __name__ == "__main__":

    result = arbitrate(
        upstream="The dream carried symbolic continuity.",
        rendered="The dream preserved continuity through symbolic structure."
    )

    print(result)

