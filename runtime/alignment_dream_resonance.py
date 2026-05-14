from __future__ import annotations
from typing import Dict, Any, Optional
import math

def _clamp01(x: float) -> float:
    try:
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.0

def _aggregate_channels(ch: Optional[Dict[str, float]]) -> float:
    """
    Conservative aggregation: sum(values) / (len + 1) to avoid runaway.
    Accepts None -> 0.0
    """
    if not ch:
        return 0.0
    vals = [float(v) for v in ch.values() if isinstance(v, (int, float))]
    if not vals:
        return 0.0
    return _clamp01(sum(vals) / (len(vals) + 1.0))

class DreamResonanceLayer:
    """
    Implements the alignment.dream_resonance_layer mapping.
    Public API:
      compute_from_scalars(moment, chapter, arc, options) -> dict with components and composite
      compute_from_channels(moment_channels, chapter_channels, arc_channels) -> dict
    """

    def __init__(self, decay: float = 0.0):
        self.decay = float(decay)

    def compute_from_scalars(
        self,
        moment: float,
        chapter: float,
        arc: float,
        *,
        apply_decay: bool = False,
    ) -> Dict[str, float]:
        if apply_decay and self.decay > 0.0:
            moment = _clamp01(moment * (1.0 - self.decay))
            chapter = _clamp01(chapter * (1.0 - self.decay))
            arc = _clamp01(arc * (1.0 - self.decay))

        fast_component = _clamp01(moment * 1.0)
        mid_component = _clamp01(chapter * 1.0)
        slow_component = _clamp01(arc * 1.0)

        stage1 = 0.6 * fast_component + 0.4 * mid_component
        stage2 = 0.75 * stage1 + 0.25 * slow_component
        composite = _clamp01(stage2)

        return {
            "fast_component": round(fast_component, 4),
            "mid_component": round(mid_component, 4),
            "slow_component": round(slow_component, 4),
            "stage1": round(stage1, 4),
            "composite": round(composite, 4),
        }

    def compute_from_channels(
        self,
        moment_channels: Optional[Dict[str, float]],
        chapter_channels: Optional[Dict[str, float]],
        arc_channels: Optional[Dict[str, float]],
        *,
        apply_decay: bool = False,
    ) -> Dict[str, float]:
        m = _aggregate_channels(moment_channels)
        c = _aggregate_channels(chapter_channels)
        a = _aggregate_channels(arc_channels)
        return self.compute_from_scalars(m, c, a, apply_decay=apply_decay)

