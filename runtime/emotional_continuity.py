from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


Vector = Dict[str, float]


@dataclass
class ContinuityResult:
    composite: Vector
    weights: List[float]
    used: int


def apply_decay_filter(vectors: List[Vector], decay: float = 0.9, max_turns: int = 5) -> ContinuityResult:
    if not vectors:
        return ContinuityResult(composite={}, weights=[], used=0)

    vs = vectors[-max_turns:]
    n = len(vs)

    weights = []
    for i in range(n):
        dist = (n - 1 - i)
        weights.append(decay ** dist)

    keys = set()
    for v in vs:
        keys.update(v.keys())

    comp: Vector = {}
    denom = sum(weights) if weights else 1.0

    for k in keys:
        num = 0.0
        for v, w in zip(vs, weights):
            num += float(v.get(k, 0.0)) * w
        comp[k] = num / denom

    return ContinuityResult(composite=comp, weights=weights, used=n)


def blend_into_vector(base: Vector, continuity: Vector, alpha: float = 0.35) -> Vector:
    out = dict(base)
    for k, v in continuity.items():
        out[k] = (1 - alpha) * float(out.get(k, 0.0)) + alpha * float(v)
    return out

