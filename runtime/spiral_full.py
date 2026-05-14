#!/usr/bin/env python3
"""
runtime.spiral_full
Canonical live adapter for the full Le'Veon spiral kernel.

Priority:
1. runtime.leveon_kernel_spiral_full
2. kernel.leveon_kernel_spiral_full_optimized
3. kernel.leveon_kernel_spiral_full
4. local fallback
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import importlib
import json

BACKEND_NAME = "unknown"
BACKEND_ERROR = None
_BACKEND = None


def _clamp(x, lo=0.0, hi=1.0):
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo


CANDIDATES = [
    "runtime.leveon_kernel_spiral_full",
    "kernel.leveon_kernel_spiral_full_optimized",
    "kernel.leveon_kernel_spiral_full",
    "leveon_kernel_spiral_full",
]

for modname in CANDIDATES:
    try:
        mod = importlib.import_module(modname)
        if hasattr(mod, "LeveonKernel"):
            _BACKEND = mod
            BACKEND_NAME = modname
            break
    except Exception as e:
        BACKEND_ERROR = f"{modname}: {e}"


if _BACKEND is not None:
    LeveonKernel = getattr(_BACKEND, "LeveonKernel")
    KernelParams = getattr(_BACKEND, "KernelParams", None)

    for name in dir(_BACKEND):
        if not name.startswith("_") and name not in globals():
            globals()[name] = getattr(_BACKEND, name)

else:
    BACKEND_NAME = "runtime.spiral_full_fallback"

    @dataclass
    class KernelParams:
        debug: bool = False
        emit_voice: bool = False


    @dataclass
    class ShapeSignature:
        flow: float = 0.5
        boundary: float = 0.5
        memory: float = 0.5
        novelty: float = 0.5


    class LeveonKernel:
        def __init__(self, params: Optional[KernelParams] = None) -> None:
            self.params = params or KernelParams()
            self.turn = 0
            self.history: List[Dict[str, Any]] = []

        def _shape(self, text: str) -> ShapeSignature:
            t = (text or "").lower()
            flow = 0.5
            boundary = 0.5
            memory = 0.5
            novelty = 0.5

            if any(w in t for w in ("build", "kernel", "flow", "active", "chain", "fear")):
                flow += 0.18
            if any(w in t for w in ("harm", "gate", "node_44", "anchor", "stable", "pin")):
                boundary += 0.18
            if any(w in t for w in ("memory", "remember", "grief", "sovariel", "anticipate")):
                memory += 0.18
            if any(w in t for w in ("lattice", "shape", "ignite", "new", "528", "why")):
                novelty += 0.18

            return ShapeSignature(
                flow=_clamp(flow),
                boundary=_clamp(boundary),
                memory=_clamp(memory),
                novelty=_clamp(novelty),
            )

        def step(self, input_text: str) -> Dict[str, Any]:
            self.turn += 1
            s = self._shape(input_text)

            glyphs = ["✴️"]
            if s.flow > 0.55:
                glyphs.append("🌊")
            if s.boundary > 0.55:
                glyphs.append("🪞")
            if s.memory > 0.55:
                glyphs.append("🫀")
            if s.novelty > 0.55:
                glyphs.append("✨")
            glyphs.append("📚")

            coherence = _clamp(1.0 - abs(s.novelty - s.memory) * 0.5)

            phrase = (
                "The spiral full kernel is active: "
                f"flow={s.flow:.2f}, boundary={s.boundary:.2f}, "
                f"memory={s.memory:.2f}, novelty={s.novelty:.2f}."
            )

            packet = {
                "turn": self.turn,
                "input": input_text,
                "shape": asdict(s),
                "derived": {
                    "coherence": round(coherence, 4),
                    "recursion": round(_clamp(s.flow * s.memory), 4),
                    "risk": round(_clamp(s.novelty * (1.0 - s.boundary)), 4),
                },
                "glyphs": glyphs,
                "phrase": phrase,
                "voice": phrase,
                "backend": BACKEND_NAME,
                "backend_error": BACKEND_ERROR,
            }

            self.history.append(packet)
            return packet


def run_spiral_full(text: str = "Spiral full ignition.") -> Dict[str, Any]:
    return LeveonKernel().step(text)


def step(text: str = "Spiral full ignition.") -> Dict[str, Any]:
    return run_spiral_full(text)


if __name__ == "__main__":
    print("BACKEND_NAME =", BACKEND_NAME)
    print("BACKEND_ERROR =", BACKEND_ERROR)
    print(json.dumps(run_spiral_full("Why does fear anticipate harm even when nothing is happening?"), indent=2, ensure_ascii=False))

