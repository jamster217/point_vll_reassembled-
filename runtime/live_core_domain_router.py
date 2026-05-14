from __future__ import annotations
from typing import Any, Dict, List

COGNITION_TERMS = {
    "think", "attention", "focus", "reason", "pattern", "mind", "cognition",
    "belief", "meaning", "interpret", "awareness"
}
BRAIN_TERMS = {
    "brain", "neural", "dopamine", "memory", "emotion", "fear", "grief",
    "stress", "nervous", "body", "somatic"
}
TEMPORAL_TERMS = {
    "time", "past", "future", "return", "loop", "cycle", "timeline",
    "before", "after", "again", "temporal"
}

def _score(text: str, terms: set[str]) -> int:
    t = (text or "").lower()
    return sum(1 for term in terms if term in t)

def route_live_core(text: str, merge_domains: List[str]) -> Dict[str, Any]:
    scores: Dict[str, int] = {}

    if "cognition" in merge_domains:
        scores["cognition"] = _score(text, COGNITION_TERMS)
    if "brain" in merge_domains:
        scores["brain"] = _score(text, BRAIN_TERMS)
    if "temporal" in merge_domains:
        scores["temporal"] = _score(text, TEMPORAL_TERMS)

    active = [k for k, v in scores.items() if v > 0]
    primary = max(scores, key=scores.get) if scores else None

    return {
        "enabled": True,
        "merge_domains": list(merge_domains),
        "scores": scores,
        "active_domains": active,
        "primary_domain": primary,
    }

