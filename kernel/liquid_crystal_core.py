# file: kernel/liquid_crystal_core.py
"""
Liquid-Crystal Core
-------------------
Maps glyph strings ⇄ fixed-length resonance vectors.

This module is intentionally small but expressive:
- Deterministic hashing for unknown glyphs
- Optional learned/hand-tuned registry
- Simple blending utilities for higher-level kernels
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Iterable, Optional, Any
import hashlib
import json


@dataclass
class LiquidGlyphSample:
    glyph: str
    vector: List[float]
    tags: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "glyph": self.glyph,
            "vector": list(self.vector),
            "tags": list(self.tags or []),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LiquidGlyphSample":
        return cls(
            glyph=data.get("glyph", ""),
            vector=[float(x) for x in data.get("vector", [])],
            tags=list(data.get("tags", []) or []),
        )


def _sq_euclidean(a: List[float], b: List[float]) -> float:
    m = min(len(a), len(b))
    s = 0.0
    for i in range(m):
        d = a[i] - b[i]
        s += d * d
    return s


def _clamp01(x: float) -> float:
    try:
        x = float(x)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, x))


class LiquidCrystalCore:
    """
    Core encoder/decoder.

    - `dimensions`: length of each vector
    - `auto_register`: if True, unknown glyphs are added to the registry
    """

    def __init__(self, dimensions: int = 4, auto_register: bool = True) -> None:
        self.dimensions = max(1, int(dimensions))
        self.auto_register = bool(auto_register)
        self._registry: Dict[str, LiquidGlyphSample] = {}

    # ------------------------------------------------------------------
    # Hashing / encoding
    # ------------------------------------------------------------------

    def _hash_glyph(self, glyph: str) -> List[float]:
        h = hashlib.sha256(glyph.encode("utf-8")).digest()
        vals = [int(b) / 255.0 for b in h[: self.dimensions]]
        return vals

    def register(
        self,
        glyph: str,
        vector: Optional[Iterable[float]] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> LiquidGlyphSample:
        if vector is None:
            vector = self._hash_glyph(glyph)
        vec = [float(x) for x in vector]
        if len(vec) != self.dimensions:
            # simple resize: repeat or trim
            if len(vec) == 0:
                vec = self._hash_glyph(glyph)
            elif len(vec) > self.dimensions:
                vec = vec[: self.dimensions]
            else:
                while len(vec) < self.dimensions:
                    vec.extend(vec[: self.dimensions - len(vec)])
        sample = LiquidGlyphSample(glyph=glyph, vector=vec, tags=list(tags or []))
        self._registry[glyph] = sample
        return sample

    def encode(self, glyph: str) -> List[float]:
        """
        Encode glyph → vector.
        """
        if glyph in self._registry:
            return list(self._registry[glyph].vector)
        vec = self._hash_glyph(glyph)
        if self.auto_register:
            self.register(glyph, vec)
        return vec

    def decode(self, vector: Iterable[float]) -> str:
        """
        Decode vector → closest glyph in registry.
        If registry is empty, returns a synthetic @SIG_… label.
        """
        vec = [float(x) for x in vector]
        if not self._registry:
            sig = ":".join(f"{x:.2f}" for x in vec)
            return f"@SIG_{sig}"

        best_glyph = ""
        best_dist = float("inf")
        for sample in self._registry.values():
            d = _sq_euclidean(vec, sample.vector)
            if d < best_dist:
                best_dist = d
                best_glyph = sample.glyph
        return best_glyph

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def blend(
        self,
        vectors: Iterable[Iterable[float]],
        weights: Optional[Iterable[float]] = None,
    ) -> List[float]:
        """
        Weighted average of vectors; clamps into [0, 1].
        """
        vs = [list(v) for v in vectors]
        if not vs:
            return [0.0] * self.dimensions

        n = len(vs)
        if weights is None:
            weights = [1.0] * n
        ws = [max(0.0, float(w)) for w in weights]
        if sum(ws) <= 0:
            ws = [1.0] * n

        out = [0.0] * self.dimensions
        total = sum(ws)
        for w, v in zip(ws, vs):
            for i in range(min(self.dimensions, len(v))):
                out[i] += (w / total) * v[i]

        return [_clamp01(x) for x in out]

    def glyph_sequence_to_matrix(self, glyphs: Iterable[str]) -> List[List[float]]:
        return [self.encode(g) for g in glyphs]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions": self.dimensions,
            "auto_register": self.auto_register,
            "registry": [s.to_dict() for s in self._registry.values()],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LiquidCrystalCore":
        core = cls(
            dimensions=int(data.get("dimensions", 4)),
            auto_register=bool(data.get("auto_register", True)),
        )
        for item in data.get("registry", []):
            sample = LiquidGlyphSample.from_dict(item)
            core.register(sample.glyph, sample.vector, sample.tags)
        return core

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, text: str) -> "LiquidCrystalCore":
        return cls.from_dict(json.loads(text))


# Default singleton for quick use
_default_core = LiquidCrystalCore()


def glyph_to_vector(glyph: str) -> List[float]:
    return _default_core.encode(glyph)


def vector_to_glyph(v: Iterable[float]) -> str:
    return _default_core.decode(v)

