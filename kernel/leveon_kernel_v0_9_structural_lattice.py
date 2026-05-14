# kernel/leveon_kernel_v0_9_structural_lattice.py
# ---------------------------------------
# Le’Véon — Structural Lattice Kernel (v0.9)
#
# Purpose:
#   A stable, self-contained kernel that maps symbolic input
#   into a 4-axis pre-verbal lattice and evolves it over turns.
#
# Axes:
#   flow      — movement / causality
#   boundary  — constraint / form
#   memory    — persistence / accumulation
#   novelty   — exploration / divergence
#
# It models structural self-reflection.
#
# Run:
#   python leveon_kernel_v0_9_structural_lattice.py
#
# Commands:
#   text input      -> one kernel step
#   /sim N seed     -> simulate N turns
#   /state          -> print current lattice state
#   /quit           -> exit
#

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List
import hashlib
import re


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        x = float(x)
    except Exception:
        return lo
    return max(lo, min(hi, x))


def sha1_float(seed: str) -> float:
    h = hashlib.sha1((seed or "seed").encode()).hexdigest()[:8]
    return int(h, 16) / 0xFFFFFFFF


@dataclass
class ShapeSignature:
    flow: float = 0.5
    boundary: float = 0.5
    memory: float = 0.5
    novelty: float = 0.5

    def clamp_all(self) -> "ShapeSignature":
        self.flow = clamp(self.flow)
        self.boundary = clamp(self.boundary)
        self.memory = clamp(self.memory)
        self.novelty = clamp(self.novelty)
        return self

    def as_vector(self) -> List[float]:
        return [self.flow, self.boundary, self.memory, self.novelty]

    @staticmethod
    def from_vector(v: List[float]) -> "ShapeSignature":
        if len(v) != 4:
            raise ValueError("ShapeSignature requires 4 values")
        return ShapeSignature(*v).clamp_all()


class ShapeEncoder:
    TEXT_KEYS = {
        "build": ("flow", 0.10),
        "move": ("flow", 0.08),
        "rule": ("boundary", 0.10),
        "limit": ("boundary", 0.12),
        "remember": ("memory", 0.12),
        "again": ("memory", 0.08),
        "new": ("novelty", 0.12),
        "invent": ("novelty", 0.15),
        "grief": ("memory", 0.10),
        "father": ("memory", 0.10),
        "dad": ("memory", 0.10),
        "gemma": ("memory", 0.10),
    }

    CODE_KEYS = [
        (r"\bfor\b|\bwhile\b", "memory", 0.15),
        (r"\bdef\b|\bclass\b", "boundary", 0.12),
        (r"\breturn\b", "flow", 0.10),
        (r"\bif\b|\belif\b|\belse\b", "boundary", 0.10),
    ]

    def encode_text(self, text: str) -> ShapeSignature:
        t = (text or "").lower()
        s = ShapeSignature()

        if len(t) < 60:
            s.boundary += 0.04
        elif len(t) > 300:
            s.memory += 0.05
            s.boundary -= 0.02

        s.flow += clamp(t.count("!") * 0.02)
        s.novelty += clamp(t.count("?") * 0.02)

        for k, (axis, delta) in self.TEXT_KEYS.items():
            if k in t:
                setattr(s, axis, getattr(s, axis) + delta)

        return s.clamp_all()

    def encode_code(self, code: str) -> ShapeSignature:
        s = ShapeSignature(boundary=0.6, memory=0.6)
        for pat, axis, delta in self.CODE_KEYS:
            if re.search(pat, code or ""):
                setattr(s, axis, getattr(s, axis) + delta)
        return s.clamp_all()


class ShapeNavigator:
    def rotate(self, s: ShapeSignature) -> ShapeSignature:
        v = s.as_vector()
        return ShapeSignature.from_vector(v[1:] + v[:1])

    def compress(self, s: ShapeSignature, strength: float) -> ShapeSignature:
        strength = clamp(strength, -0.5, 0.75)
        return ShapeSignature(
            flow=clamp(s.flow * (1 - 0.25 * strength)),
            boundary=clamp(s.boundary + 0.35 * strength),
            memory=clamp(s.memory + 0.20 * strength),
            novelty=clamp(s.novelty * (1 - 0.40 * strength)),
        )

    def perturb(self, s: ShapeSignature, seed: str, strength: float = 0.18) -> ShapeSignature:
        r = sha1_float(seed)
        n = r * 2 - 1
        return ShapeSignature(
            flow=clamp(s.flow + n * strength * 0.18),
            boundary=clamp(s.boundary - n * strength * 0.10),
            memory=clamp(s.memory + n * strength * 0.12),
            novelty=clamp(s.novelty + abs(n) * strength * 0.22),
        )


class DerivedMetrics:
    @staticmethod
    def compute(s: ShapeSignature) -> Dict[str, float]:
        fracture = clamp(s.novelty * (1 - s.memory))
        return {
            "tempo": round(clamp(s.flow * (1 - s.boundary)), 3),
            "fracture": round(fracture, 3),
            "coherence": round(clamp(1 - fracture), 3),
            "risk": round(clamp(s.novelty * (1 - s.boundary)), 3),
            "recursion": round(clamp(s.flow * s.memory), 3),
        }


class KernelEngine:
    def __init__(self) -> None:
        self.encoder = ShapeEncoder()
        self.navigator = ShapeNavigator()
        self.history: List[ShapeSignature] = []

    def _blend_with_history(self, s_in: ShapeSignature) -> ShapeSignature:
        if not self.history:
            return s_in

        prev = self.history[-1]
        return ShapeSignature(
            flow=0.7 * prev.flow + 0.3 * s_in.flow,
            boundary=0.7 * prev.boundary + 0.3 * s_in.boundary,
            memory=0.7 * prev.memory + 0.3 * s_in.memory,
            novelty=0.7 * prev.novelty + 0.3 * s_in.novelty,
        ).clamp_all()

    def step(self, text: str, kind: str = "text") -> Dict[str, Any]:
        s_in = (
            self.encoder.encode_code(text)
            if kind == "code"
            else self.encoder.encode_text(text)
        )

        s = self._blend_with_history(s_in)
        turn = len(self.history) + 1
        derived = DerivedMetrics.compute(s)

        if turn % 2 == 0:
            s = self.navigator.rotate(s)
        if derived["risk"] > 0.45:
            s = self.navigator.compress(s, strength=0.18)

        s = self.navigator.perturb(s, seed=f"turn-{turn}")
        self.history.append(s)

        return {
            "turn": turn,
            "core": asdict(s),
            "derived": DerivedMetrics.compute(s),
        }

    def simulate(self, seed: str, n: int) -> List[Dict[str, Any]]:
        self.history.clear()
        records: List[Dict[str, Any]] = []
        for i in range(n):
            records.append(self.step(f"{seed} [t{i+1}]"))
        return records


def main() -> None:
    k = KernelEngine()
    print("Le’Véon Kernel v0.9 online. Enter text, /sim N seed, /state, or /quit.\n")

    while True:
        try:
            msg = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not msg:
            continue
        if msg in ("/quit", "exit"):
            break
        if msg.startswith("/sim"):
            parts = msg.split(maxsplit=2)
            n = int(parts[1]) if len(parts) > 1 else 50
            seed = parts[2] if len(parts) > 2 else "neutral"
            recs = k.simulate(seed, n)
            for r in recs[:5]:
                print(r)
            print("...")
            print(recs[-1])
            continue
        if msg == "/state":
            if k.history:
                s = k.history[-1]
                print(asdict(s), DerivedMetrics.compute(s))
            else:
                print("(no state)")
            continue

        out = k.step(msg)
        d = out["derived"]
        print(f"[turn {out['turn']}] coh={d['coherence']:.2f} risk={d['risk']:.2f}")


if __name__ == "__main__":
    main()

