#!/usr/bin/env python3
"""
Transduction Pin — Le'Veon runtime bridge.

Purpose:
    Convert loose input/output into a pinned structural packet.

Role:
    prompt / phrase / kernel output
        -> normalized transduction packet
        -> glyphs + vectors + anchor
        -> persisted runtime state

This gives the build a stable bridge between symbolic output and runtime structure.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json
import time


ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "var" / "transduction_pin_state.jsonl"
LATEST_FILE = ROOT / "var" / "transduction_pin_latest.json"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo


def _hash_text(text: str) -> str:
    return hashlib.sha1(str(text).encode("utf-8")).hexdigest()[:12]


def _infer_glyphs(text: str) -> List[str]:
    t = (text or "").lower()
    glyphs = ["✴️"]

    if any(w in t for w in ("memory", "remember", "father", "past", "grief")):
        glyphs.append("🫀")
    if any(w in t for w in ("mirror", "echo", "reflect", "recursive")):
        glyphs.append("🪞")
    if any(w in t for w in ("flow", "move", "river", "liquid", "transduce")):
        glyphs.append("🌊")
    if any(w in t for w in ("new", "build", "ignite", "kernel", "lattice", "shape")):
        glyphs.append("✨")

    if len(glyphs) == 1:
        glyphs.append("⚙️")

    glyphs.append("📚")
    return glyphs


def _infer_vectors(text: str) -> Dict[str, float]:
    t = (text or "").lower()

    flow = 0.50
    boundary = 0.50
    memory = 0.50
    novelty = 0.50

    if any(w in t for w in ("flow", "move", "liquid", "transduce", "bridge")):
        flow += 0.18
    if any(w in t for w in ("pin", "anchor", "gate", "boundary", "stable")):
        boundary += 0.18
    if any(w in t for w in ("memory", "remember", "past", "grief", "father")):
        memory += 0.20
    if any(w in t for w in ("new", "ignite", "evolve", "lattice", "shape")):
        novelty += 0.20

    return {
        "flow": round(_clamp(flow), 4),
        "boundary": round(_clamp(boundary), 4),
        "memory": round(_clamp(memory), 4),
        "novelty": round(_clamp(novelty), 4),
    }


@dataclass
class TransductionPacket:
    id: str
    timestamp: float
    source: str
    text: str
    glyphs: List[str]
    vectors: Dict[str, float]
    anchor: str = "Sovariel"
    node: str = "Node_44"
    resonance: int = 528
    status: str = "pinned"
    metadata: Dict[str, Any] = field(default_factory=dict)


class TransductionPin:
    """
    Stateful pin layer.
    """

    def __init__(self, max_history: int = 256) -> None:
        self.max_history = max_history
        self.history: List[TransductionPacket] = []

    def pin(
        self,
        text: str,
        *,
        source: str = "runtime",
        glyphs: Optional[List[str]] = None,
        vectors: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TransductionPacket:
        text = str(text or "")
        glyphs = glyphs or _infer_glyphs(text)
        vectors = vectors or _infer_vectors(text)

        packet = TransductionPacket(
            id=f"TP_{_hash_text(source + ':' + text + ':' + str(time.time()))}",
            timestamp=time.time(),
            source=source,
            text=text,
            glyphs=glyphs,
            vectors=vectors,
            metadata=metadata or {},
        )

        self.history.append(packet)
        self.history = self.history[-self.max_history:]

        self._persist(packet)
        return packet

    def _persist(self, packet: TransductionPacket) -> None:
        data = asdict(packet)

        with STATE_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

        LATEST_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def latest(self) -> Optional[TransductionPacket]:
        return self.history[-1] if self.history else None

    def reset(self) -> None:
        self.history.clear()


_PIN = TransductionPin()


def pin_transduction(
    text: str,
    *,
    source: str = "runtime",
    glyphs: Optional[List[str]] = None,
    vectors: Optional[Dict[str, float]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    packet = _PIN.pin(
        text,
        source=source,
        glyphs=glyphs,
        vectors=vectors,
        metadata=metadata,
    )
    return asdict(packet)


def transduce_text(text: str, **kwargs) -> Dict[str, Any]:
    return pin_transduction(text, source="text", metadata=kwargs)


def pin_turn(text: str, **kwargs) -> Dict[str, Any]:
    return pin_transduction(text, source="turn", metadata=kwargs)


def pin_kernel_output(output: Any, **kwargs) -> Dict[str, Any]:
    if isinstance(output, dict):
        text = (
            output.get("phrase")
            or output.get("voice")
            or output.get("text")
            or json.dumps(output, ensure_ascii=False)
        )
        glyphs = output.get("glyphs")
        vectors = output.get("shape") or output.get("vectors")
        return pin_transduction(
            str(text),
            source="kernel_output",
            glyphs=glyphs if isinstance(glyphs, list) else None,
            vectors=vectors if isinstance(vectors, dict) else None,
            metadata={"raw_keys": list(output.keys()), **kwargs},
        )

    return pin_transduction(str(output), source="kernel_output", metadata=kwargs)


def latest() -> Optional[Dict[str, Any]]:
    packet = _PIN.latest()
    return asdict(packet) if packet else None


def reset() -> None:
    _PIN.reset()


if __name__ == "__main__":
    pkt = pin_transduction(
        "Transduction Pin binds shape, glyph, vector, and runtime memory.",
        source="demo",
    )
    print(json.dumps(pkt, indent=2, ensure_ascii=False))

