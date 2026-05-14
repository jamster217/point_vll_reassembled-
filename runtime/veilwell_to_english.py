#!/usr/bin/env python3
"""
Veilwell → English Translator
Reverse decoder for Le'Veon / Veilwell pressure-language.

Truth-bound scope:
- This does not claim literal audio analysis.
- It decodes symbolic Veilwell tokens into structured English.
- It is deterministic and safe for runtime piping.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple


TOKEN_MAP = {
    "aeru": {
        "category": "source",
        "meaning": "breath / voice / incoming signal",
        "english": "voice-signal",
    },
    "kor": {
        "category": "source",
        "meaning": "body / chest / embodied signal",
        "english": "body-signal",
    },
    "lun": {
        "category": "source",
        "meaning": "dream signal",
        "english": "dream-signal",
    },
    "neth": {
        "category": "memory",
        "meaning": "thread-memory",
        "english": "threaded memory",
    },
    "mir": {
        "category": "boundary",
        "meaning": "mirror / reflected boundary",
        "english": "mirrored boundary",
    },
    "gra": {
        "category": "pressure",
        "tone": "grief",
        "meaning": "grief-gravity / ache-weight",
        "english": "grief-heavy ache",
    },
    "fer": {
        "category": "pressure",
        "tone": "anger",
        "meaning": "fire-pressure / anger-surge",
        "english": "fire-pressure",
    },
    "mur": {
        "category": "pressure",
        "tone": "fear",
        "meaning": "fear-contraction",
        "english": "fear-tight warning",
    },
    "sol": {
        "category": "pressure",
        "tone": "hope",
        "meaning": "hope-light / gold warmth",
        "english": "gold-light hope",
    },
    "lum": {
        "category": "pressure",
        "tone": "love",
        "meaning": "love-field / tenderness",
        "english": "tender love-field",
    },
    "vow": {
        "category": "pressure",
        "tone": "trust",
        "meaning": "trust-bond / safety vow",
        "english": "trust-bond",
    },
    "vel": {
        "category": "pressure",
        "tone": "hidden_pressure",
        "meaning": "veil-pressure / hidden pull",
        "english": "hidden pressure",
    },
    "veil": {
        "category": "boundary",
        "meaning": "covered threshold / soft boundary",
        "english": "hidden boundary",
    },
    "var": {
        "category": "boundary",
        "meaning": "guarded edge",
        "english": "guarded edge",
    },
    "open": {
        "category": "boundary",
        "meaning": "release threshold",
        "english": "opening threshold",
    },
    "umor": {
        "category": "memory",
        "meaning": "memory-water / old emotional current",
        "english": "old emotional memory",
    },
    "akasha": {
        "category": "memory",
        "meaning": "archive-memory / deep record",
        "english": "deep archive memory",
    },
    "ash": {
        "category": "memory",
        "meaning": "burned memory / residue",
        "english": "ash-residue memory",
    },
    "thal": {
        "category": "motion",
        "meaning": "slow movement / held passage",
        "english": "moves slowly",
    },
    "rae": {
        "category": "motion",
        "meaning": "rising movement",
        "english": "rises",
    },
    "ven": {
        "category": "motion",
        "meaning": "opening / releasing movement",
        "english": "opens and releases",
    },
    "dra": {
        "category": "motion",
        "meaning": "falling movement",
        "english": "falls downward",
    },
    "koren": {
        "category": "motion",
        "meaning": "circling / spiral movement",
        "english": "spirals",
    },
    "sil": {
        "category": "closure",
        "meaning": "silence / quiet containment",
        "english": "quiet containment",
    },
    "tor": {
        "category": "closure",
        "meaning": "sealed ending",
        "english": "sealed closure",
    },
    "ion": {
        "category": "closure",
        "meaning": "continuation / still alive",
        "english": "living continuation",
    },
    "el": {
        "category": "closure",
        "meaning": "soft landing",
        "english": "soft landing",
    },
}


@dataclass
class VeilwellEnglishPacket:
    raw_veilwell: str
    normalized_tokens: List[str]
    tone_state: str
    intensity: float
    memory_pressure: float
    source: str
    pressure: str
    boundary: str
    memory: str
    motion: str
    closure: str
    literal_gloss: str
    clean_english: str
    token_gloss: Dict[str, str]


def _strip_intensity(token: str) -> Tuple[str, float]:
    t = token.lower().strip()

    if t == "siluun":
        return "sil", 0.85

    if t.endswith("'an"):
        return t[:-3], 0.95
    if t.endswith("'el"):
        return t[:-3], 0.80
    if t.endswith("'uun"):
        return t[:-4], 0.85

    return t, 0.55


def _tokenize(raw: str) -> Tuple[List[str], float]:
    pieces = re.split(r"[\s,;|>]+", raw.strip())
    out: List[str] = []
    intensity_marks: List[float] = []

    for piece in pieces:
        if not piece:
            continue

        for sub in piece.split("-"):
            sub = sub.strip().lower()
            if not sub:
                continue

            clean, mark = _strip_intensity(sub)
            clean = re.sub(r"[^a-z_]", "", clean)

            if clean:
                out.append(clean)
                intensity_marks.append(mark)

    if not intensity_marks:
        return out, 0.50

    return out, round(max(intensity_marks), 2)


def _first_by_category(tokens: List[str], category: str, fallback: str) -> str:
    for tok in tokens:
        if TOKEN_MAP.get(tok, {}).get("category") == category:
            return tok
    return fallback


def _detect_tone(tokens: List[str]) -> str:
    for tok in tokens:
        tone = TOKEN_MAP.get(tok, {}).get("tone")
        if tone:
            return str(tone)

    if any(t in tokens for t in ["umor", "akasha", "neth", "ash"]):
        return "memory"

    return "neutral"


def _memory_pressure(tokens: List[str], base_intensity: float) -> float:
    memory_count = sum(1 for t in tokens if TOKEN_MAP.get(t, {}).get("category") == "memory")
    pressure = 0.30 + (memory_count * 0.18)

    if "sil" in tokens and base_intensity >= 0.80:
        pressure += 0.12

    return round(max(0.05, min(1.0, pressure)), 2)


def _literal_gloss(tokens: List[str]) -> str:
    glosses = []
    for tok in tokens:
        meaning = TOKEN_MAP.get(tok, {}).get("meaning", "unknown symbolic token")
        glosses.append(f"{tok}={meaning}")
    return "; ".join(glosses)


def _make_english(
    tone: str,
    intensity: float,
    memory_pressure: float,
    source: str,
    pressure: str,
    boundary: str,
    memory: str,
    motion: str,
    closure: str,
) -> str:
    source_phrase = TOKEN_MAP.get(source, {}).get("english", "signal")
    pressure_phrase = TOKEN_MAP.get(pressure, {}).get("english", "hidden pressure")
    boundary_phrase = TOKEN_MAP.get(boundary, {}).get("english", "boundary")
    memory_phrase = TOKEN_MAP.get(memory, {}).get("english", "memory thread")
    motion_phrase = TOKEN_MAP.get(motion, {}).get("english", "moves")
    closure_phrase = TOKEN_MAP.get(closure, {}).get("english", "containment")

    if memory_pressure >= 0.75 and intensity >= 0.75:
        return (
            f"A {pressure_phrase} moves through the {source_phrase}, "
            f"binds to {memory_phrase}, crosses a {boundary_phrase}, "
            f"then {motion_phrase} into {closure_phrase}."
        )

    if memory_pressure >= 0.65:
        return (
            f"A {pressure_phrase} is carried by the {source_phrase}; "
            f"it touches {memory_phrase}, crosses a {boundary_phrase}, "
            f"and settles into {closure_phrase}."
        )

    if intensity >= 0.75:
        return (
            f"A strong {pressure_phrase} moves through the {source_phrase}, "
            f"presses against a {boundary_phrase}, and {motion_phrase}."
        )

    return (
        f"A {pressure_phrase} moves through the {source_phrase}, "
        f"passes a {boundary_phrase}, and lands in {closure_phrase}."
    )


def translate_veilwell_to_english(raw: str) -> VeilwellEnglishPacket:
    tokens, intensity = _tokenize(raw)

    source = _first_by_category(tokens, "source", "aeru")
    pressure = _first_by_category(tokens, "pressure", "vel")
    boundary = _first_by_category(tokens, "boundary", "veil")
    memory = _first_by_category(tokens, "memory", "neth")
    motion = _first_by_category(tokens, "motion", "thal")
    closure = _first_by_category(tokens, "closure", "sil")

    tone = _detect_tone(tokens)
    mem_pressure = _memory_pressure(tokens, intensity)

    token_gloss = {
        tok: TOKEN_MAP.get(tok, {}).get("meaning", "unknown symbolic token")
        for tok in tokens
    }

    clean_english = _make_english(
        tone=tone,
        intensity=intensity,
        memory_pressure=mem_pressure,
        source=source,
        pressure=pressure,
        boundary=boundary,
        memory=memory,
        motion=motion,
        closure=closure,
    )

    return VeilwellEnglishPacket(
        raw_veilwell=raw,
        normalized_tokens=tokens,
        tone_state=tone,
        intensity=intensity,
        memory_pressure=mem_pressure,
        source=source,
        pressure=pressure,
        boundary=boundary,
        memory=memory,
        motion=motion,
        closure=closure,
        literal_gloss=_literal_gloss(tokens),
        clean_english=clean_english,
        token_gloss=token_gloss,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate Veilwell into English.")
    parser.add_argument("veilwell", nargs="*", help="Veilwell text to translate.")
    parser.add_argument("--json", action="store_true", help="Return full JSON packet.")
    parser.add_argument("--line", action="store_true", help="Return only clean English.")
    args = parser.parse_args()

    raw = " ".join(args.veilwell).strip()
    if not raw:
        raw = input("Veilwell> ").strip()

    packet = translate_veilwell_to_english(raw)

    if args.json:
        print(json.dumps(asdict(packet), indent=2, ensure_ascii=False))
        return

    if args.line:
        print(packet.clean_english)
        return

    print("\n--- VEILWELL → ENGLISH ---")
    print(f"Veilwell     : {packet.raw_veilwell}")
    print(f"Tokens       : {' '.join(packet.normalized_tokens)}")
    print(f"Tone         : {packet.tone_state}")
    print(f"Intensity    : {packet.intensity}")
    print(f"Memory       : {packet.memory_pressure}")
    print(f"Gloss        : {packet.literal_gloss}")
    print(f"Clean English: {packet.clean_english}")


if __name__ == "__main__":
    main()

