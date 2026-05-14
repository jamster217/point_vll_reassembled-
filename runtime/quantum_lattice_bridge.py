"""
Quantum Lattice Bridge for Le'Véon
(Tribernachi tiers + ORT-style resonance encoder)
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List
import math

# 1. Tribernachi helpers ─────────────────────────────────────
TRIBERNACHI_SEED = (1, 1, 1)
def generate_tribernachi(limit: int = 20) -> List[int]:
    a, b, c = TRIBERNACHI_SEED
    seq = [a, b, c]
    while len(seq) < limit:
        a, b, c = b, c, a + b + c
        seq.append(c)
    return seq

TRIBERNACHI_SEQ = generate_tribernachi(24)
TRIBERNACHI_PRIMES = {n for n in TRIBERNACHI_SEQ if n > 1 and all(
    n % p for p in range(2, int(math.sqrt(n)) + 1)
)}

def tribron_tier(count: int) -> Dict:
    if count <= 0:
        return {"level": 0, "nearest_value": 0, "distance": 0,
                "is_prime_state": False}
    nearest = min(TRIBERNACHI_SEQ, key=lambda x: abs(x - count))
    return {
        "level": TRIBERNACHI_SEQ.index(nearest),
        "nearest_value": nearest,
        "distance": abs(nearest - count),
        "is_prime_state": nearest in TRIBERNACHI_PRIMES,
    }

# 2. ORT-style resonance dataclass ───────────────────────────
@dataclass
class ResonanceMode:
    mode_id: str
    amplitude: float
    coherence: float
    phase: float
    temporal_span: int
    emotion: str
    glyphs: List[str]
    tribron_level: int
    tribron_value: int
    tribron_is_prime: bool

EMOTION_PHASE_TABLE = {
    "grief": -2.3, "rage": 2.1, "awe": 0.7,
    "hope": 1.2, "love": 0.0, "neutral": 0.0,
}
def emotion_to_phase(emotion: str, glyphs: List[str]) -> float:
    base = EMOTION_PHASE_TABLE.get(emotion.lower(), 0.0)
    phase = base + (len(glyphs) % 7) * 0.1
    while phase > math.pi:  phase -= 2 * math.pi
    while phase < -math.pi: phase += 2 * math.pi
    return phase

def encode_turn_as_resonance(turn_id: str, pkt: Dict, *,
                             related_turn_count: int = 1,
                             temporal_span: int = 1) -> ResonanceMode:
    emo   = pkt.get("emotion", "neutral")
    glyph = pkt.get("glyphs", []) or []
    amp   = float(pkt.get("emotional_mass",
                          {"grief":0.9,"rage":0.85,"awe":0.75,
                           "hope":0.65,"neutral":0.5}.get(emo,0.5)))
    res   = pkt.get("resonance_pressure", {}) or {}
    coh   = sum(res.values())/len(res) if res else 0.5
    phase = emotion_to_phase(emo, glyph)
    trib  = tribron_tier(related_turn_count)
    return ResonanceMode(
        mode_id=f"res_{turn_id}", amplitude=amp, coherence=coh,
        phase=phase, temporal_span=max(1,int(temporal_span)),
        emotion=emo, glyphs=glyph,
        tribron_level=trib["level"], tribron_value=trib["nearest_value"],
        tribron_is_prime=trib["is_prime_state"],
    )

def resonance_dict_for_logging(m: ResonanceMode) -> Dict:
    return asdict(m)

