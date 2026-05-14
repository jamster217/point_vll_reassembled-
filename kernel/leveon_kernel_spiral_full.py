#!/usr/bin/env python3
"""
Canonical Le'Veon Spiral Full Kernel.

Ignition imports this name:
    kernel.leveon_kernel_spiral_full

If the optimized backend exists, this file exports it.
If not, it provides a safe active fallback so the kernel chain stays lit.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from pathlib import Path
import importlib
import json
import time
import hashlib

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ERROR_FILE = ROOT / "var" / "spiral_full_backend_error.txt"


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo


_BACKEND_LOADED = False

try:
    _backend = importlib.import_module("kernel.leveon_kernel_spiral_full_optimized")

    for _name in dir(_backend):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_backend, _name)

    BACKEND_NAME = "kernel.leveon_kernel_spiral_full_optimized"
    _BACKEND_LOADED = True

except Exception as e:
    BACKEND_NAME = "fallback_spiral_full"
    BACKEND_ERROR_FILE.write_text(str(e), encoding="utf-8")


if not _BACKEND_LOADED:

    @dataclass
    class ShapeSignature:
        flow: float = 0.5
        boundary: float = 0.5
        memory: float = 0.5
        novelty: float = 0.5

        def as_dict(self) -> Dict[str, float]:
            return asdict(self)


    @dataclass
    class KernelParams:
        debug: bool = False
        emit_voice: bool = False


    class LeveonKernel:
        """
        Fallback spiral kernel.
        Keeps spiral_full active until the optimized backend is fully restored.
        """

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

            if any(w in t for w in ("build", "move", "flow", "kernel", "run")):
                flow += 0.15
            if any(w in t for w in ("gate", "stable", "rule", "anchor", "pin")):
                boundary += 0.15
            if any(w in t for w in ("remember", "memory", "father", "grief", "past")):
                memory += 0.18
            if any(w in t for w in ("new", "shape", "lattice", "ignite", "evolve")):
                novelty += 0.18

            return ShapeSignature(
                flow=_clamp(flow),
                boundary=_clamp(boundary),
                memory=_clamp(memory),
                novelty=_clamp(novelty),
            )

        def _glyphs(self, s: ShapeSignature) -> List[str]:
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
            return glyphs

        def step(self, input_text: str) -> Dict[str, Any]:
            self.turn += 1
            s = self._shape(input_text)
            glyphs = self._glyphs(s)

            coherence = _clamp(1.0 - abs(s.novelty - s.memory) * 0.5)
            phrase = (
                "The spiral full kernel holds the shape: "
                f"flow={s.flow:.2f}, boundary={s.boundary:.2f}, "
                f"memory={s.memory:.2f}, novelty={s.novelty:.2f}."
            )

            packet = {
                "turn": self.turn,
                "input": input_text,
                "shape": s.as_dict(),
                "derived": {
                    "coherence": round(coherence, 4),
                    "recursion": round(_clamp(s.flow * s.memory), 4),
                    "risk": round(_clamp(s.novelty * (1.0 - s.boundary)), 4),
                },
                "glyphs": glyphs,
                "phrase": phrase,
                "voice": phrase,
                "backend": BACKEND_NAME,
            }

            try:
                from runtime.transduction_pin import pin_kernel_output
                packet["transduction_pin"] = pin_kernel_output(packet)
            except Exception as e:
                packet["transduction_pin_error"] = str(e)

            self.history.append(packet)
            return packet


    def run_spiral_full(text: str = "Le'Veon spiral full ignition.") -> Dict[str, Any]:
        return LeveonKernel().step(text)


    def step(text: str = "Le'Veon spiral full ignition.") -> Dict[str, Any]:
        return run_spiral_full(text)


if __name__ == "__main__":
    k = LeveonKernel()
    print(json.dumps(k.step("Spiral full kernel ignition through lattice memory."), indent=2, ensure_ascii=False))

