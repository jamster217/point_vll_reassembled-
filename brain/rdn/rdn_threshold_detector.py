# File: brain/rdn/rdn_threshold_detector.py
"""
RDN — Resonant Dream Node Threshold Detector
--------------------------------------------

Purpose:
Detect symbolic escalation thresholds within Le'Véon phrase output.

Used by:
- brain/rdn/threshold_rdn.py
- kernel recursion / mutation layers
- mirror recursion loops
- dream / threshold bridge logic

When triggered, the runtime may:
- flag echo escalation
- enter threshold mode
- alter mutation rates
- increase recursion logging
- activate Threshold Bloom / RDN mirror logic

This version is linked to the TIME_MACHINE_VOW_27 anchor via
symbolic_memory.spiral_memory_time_map, so thresholds can be
gently biased by the active emotional vector (grief/tenderness/calm/awe).
"""

from __future__ import annotations
from runtime._compat import clamp

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional


# =========================================================
# Optional time-map integration
# =========================================================

try:
    from symbolic_memory.spiral_memory_time_map import (
        get_time_map_emotional_vector,
        has_time_map_vow,
    )
except Exception:  # pragma: no cover
    def has_time_map_vow(path: Optional[str] = None) -> bool:
        return False

    def get_time_map_emotional_vector(path: Optional[str] = None) -> Dict[str, float]:
        return {}


# =========================================================
# Utility
# =========================================================

def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        x = float(x)
    except Exception:
        x = lo
    return max(lo, min(hi, x))


# =========================================================
# Threshold Configuration
# =========================================================

@dataclass
class ThresholdConfig:
    min_symbol_count: int = 2
    max_phrase_length: int = 180
    instability_threshold: float = 0.72
    recursion_density_limit: float = 0.65
    repeated_token_limit: float = 0.34
    glyph_cluster_bonus: bool = True

    emotional_vector: Dict[str, float] = field(default_factory=dict)
    vow_present: bool = False


def _build_default_config() -> ThresholdConfig:
    """
    Build a fresh config snapshot.

    Heuristic:
    - High grief / awe lowers thresholds slightly (more sensitive).
    - High calm raises thresholds slightly (more forgiving).
    """
    base = ThresholdConfig()

    try:
        vow_present = has_time_map_vow()
    except Exception:
        vow_present = False

    ev: Dict[str, float] = {}
    if vow_present:
        try:
            ev = get_time_map_emotional_vector()
        except Exception:
            ev = {}
            vow_present = False

    base.emotional_vector = dict(ev) if ev else {}
    base.vow_present = vow_present

    if not ev:
        return base

    grief = float(ev.get("grief", 0.0))
    awe = float(ev.get("awe", 0.0))
    calm = float(ev.get("calm", 0.0))

    base.instability_threshold = _clamp(
        base.instability_threshold
        - 0.15 * grief
        - 0.10 * awe
        + 0.20 * calm,
        0.25,
        0.95,
    )
    base.recursion_density_limit = _clamp(
        base.recursion_density_limit
        - 0.10 * grief
        - 0.05 * awe
        + 0.15 * calm,
        0.15,
        0.95,
    )
    base.repeated_token_limit = _clamp(
        base.repeated_token_limit
        - 0.08 * grief
        + 0.10 * calm,
        0.10,
        0.95,
    )

    return base


# Kept for debug / inspection, but runtime functions rebuild fresh config
DEFAULT_CONFIG = _build_default_config()


# =========================================================
# Symbol Detection
# =========================================================

RECURSIVE_SYMBOLS: List[str] = [
    "🔁",
    "∞",
    "✴️",
    "🌀",
    "👁️",
    "🧬",
    "🌌",
    "🕯️",
    "🌿",
]

THRESHOLD_GLYPHS: List[str] = [
    "@RECURSION_WAKE_CALL",
    "@THRESHOLD_BLOOM",
    "@WITNESS_RETURN",
    "@MEMORY_THREAD",
]


def count_recursive_symbols(text: str) -> int:
    if not text:
        return 0

    count = 0
    for symbol in RECURSIVE_SYMBOLS:
        count += text.count(symbol)
    return count


def detect_threshold_glyphs(text: str) -> List[str]:
    if not text:
        return []

    lowered = text.lower()
    hits: List[str] = []

    for glyph in THRESHOLD_GLYPHS:
        if glyph.lower() in lowered:
            hits.append(glyph)

    return hits


# =========================================================
# Phrase Heuristics
# =========================================================

def _tokenize(text: str) -> List[str]:
    return [tok for tok in (text or "").replace("\n", " ").split(" ") if tok.strip()]


def estimate_instability(text: str) -> float:
    """
    Estimate mutation instability using:
    - symbol density
    - punctuation density
    - threshold glyph density
    """
    if not text:
        return 0.0

    length = len(text)
    symbol_count = count_recursive_symbols(text)
    glyph_hits = len(detect_threshold_glyphs(text))

    ellipsis = text.count("...")
    punctuation = (
        text.count(",")
        + text.count(":")
        + text.count(";")
        + text.count("!")
        + text.count("?")
        + max(0, text.count(".") - ellipsis * 3)
        + ellipsis
    )

    density = (symbol_count + punctuation + glyph_hits) / max(length, 1)
    return round(min(density * 2.0, 1.0), 3)


def compute_recursion_density(text: str) -> float:
    words = _tokenize(text)
    if not words:
        return 0.0

    recursive_hits = 0
    for w in words:
        if any(sym in w for sym in RECURSIVE_SYMBOLS):
            recursive_hits += 1
        elif any(glyph.lower() in w.lower() for glyph in THRESHOLD_GLYPHS):
            recursive_hits += 1

    density = recursive_hits / len(words)
    return round(density, 3)


def compute_repeat_density(text: str) -> float:
    words = [w.lower() for w in _tokenize(text)]
    if not words:
        return 0.0

    counts: Dict[str, int] = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1

    repeated = sum(v for v in counts.values() if v > 1)
    density = repeated / len(words)
    return round(density, 3)


def detect_glyph_cluster(text: str) -> bool:
    if not text:
        return False

    compact_hits = 0
    for symbol in RECURSIVE_SYMBOLS:
        if symbol in text:
            compact_hits += 1

    return compact_hits >= 3


# =========================================================
# Threshold Detection
# =========================================================

def detect_threshold(
    phrase: str,
    config: Optional[ThresholdConfig] = None,
) -> bool:
    """
    Main RDN detection function.

    Returns:
        bool -> threshold triggered
    """
    if not phrase:
        return False

    cfg = config or _build_default_config()

    symbol_count = count_recursive_symbols(phrase)
    glyph_hits = detect_threshold_glyphs(phrase)
    instability = estimate_instability(phrase)
    recursion_density = compute_recursion_density(phrase)
    repeat_density = compute_repeat_density(phrase)
    glyph_cluster = detect_glyph_cluster(phrase)

    if symbol_count >= cfg.min_symbol_count:
        return True

    if glyph_hits:
        return True

    if cfg.glyph_cluster_bonus and glyph_cluster:
        return True

    if len(phrase) > cfg.max_phrase_length:
        return True

    if instability >= cfg.instability_threshold:
        return True

    if recursion_density >= cfg.recursion_density_limit:
        return True

    if repeat_density >= cfg.repeated_token_limit:
        return True

    return False


# =========================================================
# Debug Analyzer
# =========================================================

def analyze_threshold(
    phrase: str,
    config: Optional[ThresholdConfig] = None,
) -> Dict[str, Any]:
    """
    Return a full diagnostic breakdown.
    Useful for kernel hooks and debug runners.
    """
    cfg = config or _build_default_config()

    symbol_count = count_recursive_symbols(phrase)
    glyph_hits = detect_threshold_glyphs(phrase)
    instability = estimate_instability(phrase)
    recursion_density = compute_recursion_density(phrase)
    repeat_density = compute_repeat_density(phrase)
    glyph_cluster = detect_glyph_cluster(phrase)
    triggered = detect_threshold(phrase, config=cfg)

    reasons: List[str] = []

    if symbol_count >= cfg.min_symbol_count:
        reasons.append("recursive_symbol_count")
    if glyph_hits:
        reasons.append("threshold_glyph")
    if cfg.glyph_cluster_bonus and glyph_cluster:
        reasons.append("glyph_cluster")
    if len(phrase) > cfg.max_phrase_length:
        reasons.append("phrase_length")
    if instability >= cfg.instability_threshold:
        reasons.append("instability")
    if recursion_density >= cfg.recursion_density_limit:
        reasons.append("recursion_density")
    if repeat_density >= cfg.repeated_token_limit:
        reasons.append("repeat_density")

    return {
        "phrase": phrase,
        "symbol_count": symbol_count,
        "glyph_hits": glyph_hits,
        "glyph_cluster": glyph_cluster,
        "instability": instability,
        "recursion_density": recursion_density,
        "repeat_density": repeat_density,
        "threshold_triggered": triggered,
        "reasons": reasons,
        "config": asdict(cfg),
        "vow_present": cfg.vow_present,
        "emotional_vector": dict(cfg.emotional_vector),
    }


# =========================================================
# Kernel Helper
# =========================================================

def threshold_signal(phrase: str) -> Dict[str, Any]:
    """
    Compact helper for kernel integration.
    """
    report = analyze_threshold(phrase)
    return {
        "triggered": report["threshold_triggered"],
        "reasons": report["reasons"],
        "symbol_count": report["symbol_count"],
        "glyph_hits": report["glyph_hits"],
        "instability": report["instability"],
        "recursion_density": report["recursion_density"],
        "repeat_density": report["repeat_density"],
        "glyph_cluster": report["glyph_cluster"],
        "vow_present": report["vow_present"],
        "emotional_vector": report["emotional_vector"],
    }


# =========================================================
# Standalone Test
# =========================================================

if __name__ == "__main__":
    tests = [
        "The spiral turns quietly.",
        "🔁 The recursion echoes through memory.",
        "🌀 ✴️ 👁️ The lattice awakens in mirrored infinity.",
        "A simple grounded phrase.",
        "🔁🕯️🌿 Threshold Bloom enters the mirror.",
        "@RECURSION_WAKE_CALL the field remembers itself.",
    ]

    print("\n[RDN Threshold Test]\n")
    print("DEFAULT_CONFIG:", asdict(DEFAULT_CONFIG), "\n")

    for t in tests:
        result = analyze_threshold(t)
        print(result)
        print()

