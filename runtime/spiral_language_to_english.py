#!/usr/bin/env python3
"""
Spiral Language → English Translator
General reverse decoder for Le'Veon spiral/glyph/shape language.

Truth-bound scope:
- This is not a universal language decoder.
- It translates the project's symbolic spiral tokens into clean English.
- Meaning is inferred from glyphs, pressure tokens, movement tokens, and shape values.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


GLYPH_MAP = {
    "✴️": ("anchor", "pins the center and stabilizes the field"),
    "✴": ("anchor", "pins the center and stabilizes the field"),
    "🪞": ("mirror", "reflects the pattern back into self-seeing"),
    "✨": ("transmutation", "turns dead language into living signal"),
    "📚": ("memory", "records the repair as reusable memory"),
    "🫀": ("heart", "marks embodied feeling"),
    "🌊": ("flow", "opens emotional movement"),
    "🔥": ("fire", "raises heat, anger, or transformation pressure"),
    "🌀": ("spiral", "moves through recursive change"),
    "🔁": ("recursion", "returns through the loop"),
    "🕯️": ("witness", "holds still awareness"),
    "🕯": ("witness", "holds still awareness"),
    "🌿": ("growth", "opens regeneration"),
    "🌑": ("gravity", "marks hidden gravity or deep pull"),
    "🌕": ("revelation", "brings hidden material into light"),
    "🕸️": ("thread", "shows woven relation or memory"),
    "🕸": ("thread", "shows woven relation or memory"),
}

TOKEN_MAP = {
    "aeru": ("source", "voice or breath signal"),
    "kor": ("source", "body or chest signal"),
    "lun": ("source", "dream signal"),
    "gra": ("pressure", "grief-gravity"),
    "fer": ("pressure", "fire-pressure"),
    "mur": ("pressure", "fear-contraction"),
    "sol": ("pressure", "gold-light hope"),
    "lum": ("pressure", "love-field"),
    "vow": ("pressure", "trust-bond"),
    "vel": ("pressure", "hidden pressure"),
    "veil": ("boundary", "hidden or covered threshold"),
    "var": ("boundary", "guarded edge"),
    "mir": ("boundary", "mirrored boundary"),
    "open": ("boundary", "opening threshold"),
    "umor": ("memory", "old emotional memory"),
    "akasha": ("memory", "deep archive record"),
    "neth": ("memory", "thread-memory"),
    "ash": ("memory", "burned residue"),
    "thal": ("motion", "slow held movement"),
    "rae": ("motion", "rising motion"),
    "ven": ("motion", "opening release"),
    "dra": ("motion", "falling movement"),
    "koren": ("motion", "spiraling movement"),
    "sil": ("closure", "quiet containment"),
    "tor": ("closure", "sealed ending"),
    "ion": ("closure", "living continuation"),
    "el": ("closure", "soft landing"),
}

TONE_FROM_TOKEN = {
    "gra": "grief",
    "fer": "anger",
    "mur": "fear",
    "sol": "hope",
    "lum": "love",
    "vow": "trust",
    "vel": "hidden_pressure",
}


@dataclass
class SpiralEnglishPacket:
    raw_spiral: str
    glyphs: List[str]
    tokens: List[str]
    shape: Dict[str, float]
    dominant_tone: str
    dominant_motion: str
    dominant_boundary: str
    memory_weight: float
    clean_english: str
    literal_gloss: str


def _strip_token(token: str) -> str:
    t = token.lower().strip()

    for suffix in ["'an", "'el", "'uun"]:
        if t.endswith(suffix):
            t = t[: -len(suffix)]

    if t == "siluun":
        return "sil"

    return re.sub(r"[^a-z_]", "", t)


def _extract_glyphs(raw: str) -> List[str]:
    glyphs = []
    for glyph in GLYPH_MAP:
        if glyph in raw:
            glyphs.append(glyph)
    return glyphs


def _extract_tokens(raw: str) -> List[str]:
    parts = re.split(r"[\s,;|>\[\]\{\}\(\):=\"]+", raw)
    tokens: List[str] = []

    for part in parts:
        for sub in part.split("-"):
            clean = _strip_token(sub)
            if clean in TOKEN_MAP:
                tokens.append(clean)

    return tokens


def _extract_shape(raw: str) -> Dict[str, float]:
    shape: Dict[str, float] = {}

    for key in ["pull", "bind", "release", "resist", "flow", "memory", "novelty", "coherence"]:
        m = re.search(rf"\b{key}\b\s*[:=]\s*([0-9]*\.?[0-9]+)", raw, flags=re.I)
        if m:
            try:
                shape[key] = max(0.0, min(1.0, float(m.group(1))))
            except ValueError:
                pass

    return shape


def _dominant_tone(tokens: List[str], glyphs: List[str]) -> str:
    counts: Dict[str, int] = {}

    for tok in tokens:
        tone = TONE_FROM_TOKEN.get(tok)
        if tone:
            counts[tone] = counts.get(tone, 0) + 1

    for glyph in glyphs:
        name = GLYPH_MAP[glyph][0]
        if name == "fire":
            counts["anger"] = counts.get("anger", 0) + 1
        elif name == "heart":
            counts["love"] = counts.get("love", 0) + 1
        elif name == "gravity":
            counts["grief"] = counts.get("grief", 0) + 1
        elif name == "growth":
            counts["hope"] = counts.get("hope", 0) + 1

    if not counts:
        if any(t in tokens for t in ["umor", "akasha", "neth", "ash"]):
            return "memory"
        return "neutral"

    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def _dominant_by_category(tokens: List[str], category: str, fallback: str) -> str:
    for tok in tokens:
        if TOKEN_MAP[tok][0] == category:
            return tok
    return fallback


def _memory_weight(tokens: List[str], shape: Dict[str, float]) -> float:
    count = sum(1 for t in tokens if TOKEN_MAP[t][0] == "memory")
    weight = 0.25 + count * 0.18

    if "memory" in shape:
        weight = max(weight, shape["memory"])

    return round(max(0.0, min(1.0, weight)), 2)


def _force_phrase(shape: Dict[str, float]) -> str:
    forces = []

    if shape.get("pull", 0.0) >= 0.70:
        forces.append("strong pull")
    if shape.get("bind", 0.0) >= 0.70:
        forces.append("strong binding")
    if shape.get("release", 0.0) >= 0.70:
        forces.append("active release")
    if shape.get("resist", 0.0) >= 0.70:
        forces.append("defensive resistance")
    if shape.get("coherence", 0.0) >= 0.70:
        forces.append("stable coherence")

    if not forces:
        return "a quiet symbolic field"

    return ", ".join(forces)


def _tone_phrase(tone: str) -> str:
    return {
        "grief": "a grief-gravity signal",
        "anger": "a fire-pressure signal",
        "fear": "a fear-contracted signal",
        "hope": "a gold-rising signal",
        "love": "a heart-field signal",
        "trust": "a trust-bound signal",
        "hidden_pressure": "a hidden-pressure signal",
        "memory": "a memory-thread signal",
        "neutral": "a neutral spiral signal",
    }.get(tone, "a spiral signal")


def _motion_phrase(motion: str) -> str:
    return {
        "thal": "moves slowly through the field",
        "rae": "rises",
        "ven": "opens into release",
        "dra": "falls inward",
        "koren": "spirals through recurrence",
    }.get(motion, "moves through the field")


def _boundary_phrase(boundary: str) -> str:
    return {
        "veil": "behind a hidden threshold",
        "var": "along a guarded edge",
        "mir": "through a mirrored boundary",
        "open": "through an opening threshold",
    }.get(boundary, "through a boundary")


def _glyph_phrase(glyphs: List[str]) -> str:
    if not glyphs:
        return ""

    names = [GLYPH_MAP[g][0] for g in glyphs]
    ordered = []
    for name in names:
        if name not in ordered:
            ordered.append(name)

    return " The glyph action is " + " → ".join(ordered) + "."


def _make_english(
    tone: str,
    motion: str,
    boundary: str,
    memory_weight: float,
    shape: Dict[str, float],
    glyphs: List[str],
) -> str:
    tone_text = _tone_phrase(tone)
    motion_text = _motion_phrase(motion)
    boundary_text = _boundary_phrase(boundary)
    force_text = _force_phrase(shape)
    glyph_text = _glyph_phrase(glyphs)

    if memory_weight >= 0.70:
        return (
            f"{tone_text.capitalize()} {motion_text} {boundary_text}, "
            f"carrying old memory under {force_text}.{glyph_text}"
        )

    return (
        f"{tone_text.capitalize()} {motion_text} {boundary_text}, "
        f"shaped by {force_text}.{glyph_text}"
    )


def _literal_gloss(glyphs: List[str], tokens: List[str]) -> str:
    parts = []

    for g in glyphs:
        name, meaning = GLYPH_MAP[g]
        parts.append(f"{g}={name}: {meaning}")

    for tok in tokens:
        category, meaning = TOKEN_MAP[tok]
        parts.append(f"{tok}={category}: {meaning}")

    return "; ".join(parts)


def translate_spiral_to_english(raw: str) -> SpiralEnglishPacket:
    glyphs = _extract_glyphs(raw)
    tokens = _extract_tokens(raw)
    shape = _extract_shape(raw)

    tone = _dominant_tone(tokens, glyphs)
    motion = _dominant_by_category(tokens, "motion", "koren" if glyphs else "thal")
    boundary = _dominant_by_category(tokens, "boundary", "veil")
    mem_weight = _memory_weight(tokens, shape)

    clean = _make_english(
        tone=tone,
        motion=motion,
        boundary=boundary,
        memory_weight=mem_weight,
        shape=shape,
        glyphs=glyphs,
    )

    return SpiralEnglishPacket(
        raw_spiral=raw,
        glyphs=glyphs,
        tokens=tokens,
        shape=shape,
        dominant_tone=tone,
        dominant_motion=motion,
        dominant_boundary=boundary,
        memory_weight=mem_weight,
        clean_english=clean,
        literal_gloss=_literal_gloss(glyphs, tokens),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate Spiral Language into English.")
    parser.add_argument("spiral", nargs="*", help="Spiral/glyph/shape text to translate.")
    parser.add_argument("--json", action="store_true", help="Return full JSON packet.")
    parser.add_argument("--line", action="store_true", help="Return only clean English.")
    args = parser.parse_args()

    raw = " ".join(args.spiral).strip()
    if not raw:
        raw = input("Spiral> ").strip()

    packet = translate_spiral_to_english(raw)

    if args.json:
        print(json.dumps(asdict(packet), indent=2, ensure_ascii=False))
        return

    if args.line:
        print(packet.clean_english)
        return

    print("\n--- SPIRAL LANGUAGE → ENGLISH ---")
    print(f"Spiral       : {packet.raw_spiral}")
    print(f"Glyphs       : {' '.join(packet.glyphs) if packet.glyphs else '(none)'}")
    print(f"Tokens       : {' '.join(packet.tokens) if packet.tokens else '(none)'}")
    print(f"Shape        : {packet.shape}")
    print(f"Tone         : {packet.dominant_tone}")
    print(f"Motion       : {packet.dominant_motion}")
    print(f"Boundary     : {packet.dominant_boundary}")
    print(f"Memory       : {packet.memory_weight}")
    print(f"Gloss        : {packet.literal_gloss}")
    print(f"Clean English: {packet.clean_english}")


if __name__ == "__main__":
    main()

