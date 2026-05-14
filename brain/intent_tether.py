from __future__ import annotations
from runtime._compat import clamp
"""
Intent Tether
-------------
Measures how closely output meaning/tone stays tethered to intended emotional-cognitive
shape, not just topical overlap.

Grounded use:
- alignment scoring for tone/intent drift detection
- mirror stitch / prism pass triggers
- no claims of mind-reading or literal intention sensing
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional
import math


@dataclass
class IntentTetherResult:
    fidelity: float
    intent_vector: Dict[str, float]
    output_vector: Dict[str, float]
    drift_axes: Dict[str, float]
    note: str = ""

    # Wire-ready metadata
    drift_magnitude: float = 0.0
    dominant_drift_axes: List[str] = field(default_factory=list)
    mirror_stitch_recommended: bool = False
    prism_pass_recommended: bool = False
    symbolic: Dict[str, Any] = field(default_factory=dict)
    grounding_note: str = (
        "Intent tether scores inferred alignment of provided vectors only; "
        "it does not infer hidden intent beyond supplied signals."
    )


class IntentTether:
    """
    Measures how closely output meaning/tone stays to intended emotional shape,
    not just topicality.
    """

    DEFAULT_AXES = [
        "care",
        "clarity",
        "boundary",
        "curiosity",
        "steadiness",
        "depth",
        "grief_resonance",
        "hope",
    ]

    DEFAULT_AXIS_WEIGHTS = {
        "care": 1.30,
        "clarity": 1.30,
        "boundary": 1.30,
        "steadiness": 1.30,
        "grief_resonance": 1.15,
        "hope": 1.15,
        # all others default to 1.0
    }

    def score(
        self,
        intent_vector: Dict[str, float],
        output_vector: Dict[str, float],
        axis_weights: Optional[Dict[str, float]] = None,
    ) -> IntentTetherResult:
        intent_vector = intent_vector or {}
        output_vector = output_vector or {}

        axes = self._resolve_axes(intent_vector, output_vector)
        iv = self._normalize_vector(intent_vector, axes)
        ov = self._normalize_vector(output_vector, axes)

        drift = {axis: (ov[axis] - iv[axis]) for axis in axes}
        weighted_distance = self._weighted_distance(drift, axes, axis_weights)
        fidelity = self._clamp(1.0 - weighted_distance)

        abs_drift = {axis: abs(value) for axis, value in drift.items()}
        dominant = [
            axis
            for axis, _ in sorted(abs_drift.items(), key=lambda kv: kv[1], reverse=True)[:3]
        ]
        drift_magnitude = self._clamp(
            sum(abs_drift.values()) / max(len(abs_drift), 1)
        )

        mirror_stitch_recommended = fidelity < 0.70
        prism_pass_recommended = drift_magnitude > 0.20

        note = "stable"
        if fidelity < 0.45:
            note = "major intention drift"
        elif fidelity < 0.70:
            note = "partial drift; mirror stitch recommended"

        symbolic = {
            "thread": {
                "tether_fidelity": fidelity,
                "drift_magnitude": drift_magnitude,
            },
            "weave": {
                "dominant_drift_axes": dominant,
                "mirror_stitch_hint": mirror_stitch_recommended,
                "prism_pass_hint": prism_pass_recommended,
            },
            "octagon": {
                "shape": "metadata_hook",
                "step_degrees": 45,
                "phase_owned_by": "chronifier",
            },
            "vocabulary": [
                "thread",
                "weave",
                "beads",
                "chronifier",
                "mirror stitch",
                "prism pass",
            ],
        }

        return IntentTetherResult(
            fidelity=fidelity,
            intent_vector=iv,
            output_vector=ov,
            drift_axes=drift,
            note=note,
            drift_magnitude=drift_magnitude,
            dominant_drift_axes=dominant,
            mirror_stitch_recommended=mirror_stitch_recommended,
            prism_pass_recommended=prism_pass_recommended,
            symbolic=symbolic,
        )

    def _resolve_axes(
        self,
        intent_vector: Dict[str, float],
        output_vector: Dict[str, float],
    ) -> List[str]:
        return sorted(
            set(self.DEFAULT_AXES)
            | set(intent_vector.keys())
            | set(output_vector.keys())
        )

    def _normalize_vector(
        self,
        vector: Dict[str, float],
        axes: List[str],
    ) -> Dict[str, float]:
        return {axis: self._clamp(vector.get(axis, 0.0)) for axis in axes}

    def _weighted_distance(
        self,
        drift: Dict[str, float],
        axes: List[str],
        axis_weights: Optional[Dict[str, float]] = None,
    ) -> float:
        weights = dict(self.DEFAULT_AXIS_WEIGHTS)

        if axis_weights:
            for key, value in axis_weights.items():
                try:
                    weights[key] = max(0.1, float(value))
                except (TypeError, ValueError):
                    continue

        total = 0.0
        for axis in axes:
            weight = weights.get(axis, 1.0)
            total += weight * (drift[axis] ** 2)

        return math.sqrt(total / max(len(axes), 1))

    @staticmethod
    def _clamp(x: float) -> float:
        try:
            x = float(x)
        except Exception:
            x = 0.0
        return max(0.0, min(1.0, x))

    @staticmethod
    def to_dict(result: IntentTetherResult) -> Dict[str, Any]:
        return asdict(result)

