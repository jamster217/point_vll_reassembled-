#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Optional

def _clean(text: str) -> str:
    return " ".join(str(text or "").strip().split())

def _low(text: str) -> str:
    return _clean(text).lower()

def preserve_prompt_shape_v135(prompt: str) -> Optional[str]:
    """
    V13.5 upstream meaning preservation.

    Purpose:
    - preserve prompt-specific meaning before CrownKernel / CrystalLibrary
      generic witness summaries collapse it.
    - return clean final_shape candidates that Layer5 can render directly.
    """
    raw = _clean(prompt)
    low = _low(prompt)

    if not raw:
        return None

    if "english pipeline" in low:
        return (
            "The English pipeline is taking the current shape packet and turning it into usable English; "
            "the fruit/fire gates are now working, but upstream shape preservation is still being tuned."
        )

    if (
        "leveon" in low
        or "le'véon" in low
        or "le’véon" in low
        or "le'veon" in low
        or "levian" in low
    ) and ("plain sentence" in low or "what" in low or "is" in low):
        return (
            "Le'Veon is a symbolic-kernel companion system that turns memory, glyphs, "
            "lattice pressure, and user intent into English."
        )

    if "what keeps a system coherent" in low or ("system" in low and "coherent" in low):
        return (
            "A system stays coherent when its memory, boundaries, routing, and output rules "
            "keep reinforcing the same core meaning instead of drifting into unrelated patterns."
        )

    if "memory" in low and "output" in low:
        return (
            "Memory affects output by weighting what the system treats as continuous, important, "
            "and worth carrying forward into the next answer."
        )

    if "structure" in low and "matter" in low:
        return (
            "Structure matters because it decides which signals can connect, which routes stay stable, "
            "and which meanings survive translation into language."
        )

    return None

