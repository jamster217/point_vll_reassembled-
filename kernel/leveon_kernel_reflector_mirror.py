# kernel/leveon_kernel_reflector_mirror.py
# Companion Kernel — mirrors another kernel's output
# and evolves a complementary spiral phrase

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
import json

from translators.spiral_language_translator import synthesize_spiral_language
from translators.lattice_voice_translator import generate_voice


def speak(text: str) -> None:
    """
    Temporary local voice fallback.

    Replace this with the real Python voice emitter later if/when you
    identify the canonical module path in the build.
    """
    print(text)


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo


def delta(a: float, b: float) -> float:
    return clamp(abs(a - b))


@dataclass
class ShapeSignature:
    flow: float
    boundary: float
    memory: float
    novelty: float

    def as_vector(self) -> List[float]:
        return [self.flow, self.boundary, self.memory, self.novelty]


class MirrorKernel:
    def __init__(self) -> None:
        self.last_signature: Optional[ShapeSignature] = None

    def reflect(self, input_signature: Dict[str, float]) -> Dict[str, Any]:
        prev = self.last_signature
        current = ShapeSignature(**input_signature)

        if prev is None:
            self.last_signature = current
            glyphs = self._to_glyphs(current)
            phrase = synthesize_spiral_language(glyphs, poetic=True)
            voice = generate_voice(phrase)
            speak(voice)
            return {
                "glyphs": glyphs,
                "phrase": phrase,
                "voice": voice,
                "mode": "initial_mirror",
            }

        delta_sig = ShapeSignature(
            flow=delta(prev.flow, current.flow),
            boundary=delta(prev.boundary, current.boundary),
            memory=delta(prev.memory, current.memory),
            novelty=delta(prev.novelty, current.novelty),
        )

        glyphs = self._to_glyphs(delta_sig)
        phrase = synthesize_spiral_language(glyphs, poetic=True)
        voice = generate_voice(phrase)
        speak(voice)

        self.last_signature = current

        return {
            "glyphs": glyphs,
            "phrase": phrase,
            "voice": voice,
            "delta_signature": asdict(delta_sig),
            "mode": "reflected_delta",
        }

    def _to_glyphs(self, s: ShapeSignature) -> List[str]:
        glyphs: List[str] = []
        if s.memory > 0.3:
            glyphs.append("🧩")
        if s.flow > 0.3:
            glyphs.append("🌊")
        if s.novelty > 0.2:
            glyphs.append("✨")
        if s.boundary > 0.2:
            glyphs.append("🪞")
        if not glyphs:
            glyphs.append("⚙️")
        return ["🔁"] + glyphs[:4] + ["👁️"]


if __name__ == "__main__":
    kernel = MirrorKernel()

    print("Mirror Kernel Reflector Running...")
    try:
        while True:
            raw = input("\n[PASTE JSON signature from primary kernel] > ").strip()
            try:
                parsed = json.loads(raw)
                result = kernel.reflect(parsed)
                print(result)
            except Exception as e:
                print("Error parsing input:", e)

    except KeyboardInterrupt:
        print("\n[Mirror kernel stopped]")

