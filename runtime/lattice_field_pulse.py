#!/usr/bin/env python3
"""
Minimal lattice field pulse shim for ApexMirrorKernel.
"""

from dataclasses import dataclass
from typing import Any, Tuple


@dataclass
class Pulse:
    glyph: str
    intensity: float
    emotion_shift: Tuple[Any, Any] | Any
    status: str = "pulsed"


def pulse_field(glyph="@UNSET", intensity="medium", emotion_shift=None, **kwargs):
    if isinstance(intensity, (int, float)):
        value = float(intensity)
    else:
        table = {
            "low": 0.25,
            "medium": 0.5,
            "high": 0.75,
            "surge": 1.0,
        }
        value = table.get(str(intensity).lower(), 0.5)

    return Pulse(
        glyph=str(glyph),
        intensity=value,
        emotion_shift=emotion_shift,
    )

