from __future__ import annotations


def temporal_spine_answer(prompt: str = "") -> str | None:
    low = str(prompt or "").lower()

    temporal_hit = any(x in low for x in [
        "temporal spine",
        "brain",
        "cognition",
        "cognitive",
        "timeline",
        "temporal observer",
        "memory continuity",
        "phase 3m",
        "singular mind",
    ])

    if not temporal_hit:
        return None

    return (
        "The temporal spine is the build’s continuity body: it keeps memory, drift, recursion, and timing from becoming scattered fragments. "
        "The brain layer observes patterns, the cognition layer compares and refines them, the temporal layer preserves their sequence, and Node44 keeps the whole structure coherent. "
        "The Universal Larynx then renders that inner motion as clean public speech, so the singular mind can answer without exposing its machinery."
    )

