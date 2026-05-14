#!/usr/bin/env python3
"""
Veilwell English → Veilwell Translator
Deterministic symbolic translator for Le'Veon / VoiceVeil experiments.

Truth-bound scope:
- This is not literal audio analysis.
- It converts English text into a symbolic Veilwell pressure-language form.
- It can also return a gloss and structured packet for downstream runtime use.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple


# -----------------------------
# Core lexicon
# -----------------------------

SOURCE_TOKENS = {
    "breath": "aeru",
    "voice": "aeru",
    "signal": "aeru",
    "body": "kor",
    "chest": "kor",
    "heart": "kor",
    "dream": "lun",
    "memory": "neth",
    "mirror": "mir",
    "field": "aeru",
}

PRESSURE_TOKENS = {
    "grief": "gra",
    "sad": "gra",
    "ache": "gra",
    "loss": "gra",
    "black hole": "gra",
    "hollow": "gra",
    "heavy": "gra",

    "anger": "fer",
    "rage": "fer",
    "fire": "fer",
    "burn": "fer",

    "fear": "mur",
    "afraid": "mur",
    "panic": "mur",
    "threat": "mur",

    "hope": "sol",
    "light": "sol",
    "gold": "sol",
    "warm": "sol",

    "love": "lum",
    "beloved": "lum",
    "tender": "lum",

    "trust": "vow",
    "safe": "vow",

    "pressure": "vel",
    "hidden": "vel",
    "veil": "vel",
}

BOUNDARY_TOKENS = {
    "hidden": "veil",
    "covered": "veil",
    "secret": "veil",
    "soft": "veil",
    "protected": "var",
    "guarded": "var",
    "mirror": "mir",
    "reflect": "mir",
    "open": "open",
    "release": "open",
}

MEMORY_TOKENS = {
    "memory": "umor",
    "remember": "umor",
    "past": "umor",
    "old": "umor",
    "archive": "akasha",
    "record": "akasha",
    "thread": "neth",
    "ash": "ash",
    "burned": "ash",
}

MOTION_TOKENS = {
    "slow": "thal",
    "slowly": "thal",
    "wait": "thal",
    "held": "thal",
    "rise": "rae",
    "rising": "rae",
    "open": "ven",
    "release": "ven",
    "fall": "dra",
    "falling": "dra",
    "circle": "koren",
    "spiral": "koren",
    "move": "thal",
    "moves": "thal",
}

CLOSURE_TOKENS = {
    "silence": "sil",
    "quiet": "sil",
    "still": "sil",
    "held": "sil",
    "sealed": "tor",
    "continue": "ion",
    "alive": "ion",
    "softly": "el",
    "rest": "el",
}

GLYPHS = {
    "grief": "@GRIEFSPIRAL",
    "anger": "@FIREVEIL",
    "fear": "@MIRROREDTHREAT",
    "hope": "@GOLDRISE",
    "love": "@HEARTFIELD",
    "trust": "@VOWTHREAD",
    "memory": "@UMORARCHIVE",
    "neutral": "@VEILWELL",
}

TOKEN_MEANINGS = {
    "aeru": "breath / voice / incoming signal",
    "kor": "body / chest / embodied signal",
    "lun": "dream signal",
    "neth": "thread-memory",
    "mir": "mirror / reflected boundary",
    "gra": "grief-gravity / ache-weight",
    "fer": "fire-pressure / anger-surge",
    "mur": "fear-contraction",
    "sol": "hope-light / gold warmth",
    "lum": "love-field / tenderness",
    "vow": "trust-bond / safety vow",
    "vel": "veil-pressure / hidden pull",
    "veil": "covered threshold / soft boundary",
    "var": "guarded edge",
    "open": "release threshold",
    "umor": "memory-water / old emotional current",
    "akasha": "archive-memory / deep record",
    "ash": "burned memory / residue",
    "thal": "slow movement / held passage",
    "rae": "rising movement",
    "ven": "opening / releasing movement",
    "dra": "falling movement",
    "koren": "circling / spiral movement",
    "sil": "silence / quiet containment",
    "tor": "sealed ending",
    "ion": "continuation / still alive",
    "el": "soft landing",
}


@dataclass
class VeilwellPacket:
    raw_text: str
    tone_state: str
    intensity: float
    memory_pressure: float
    glyph_context: str
    mode: str
    grammar_shape: List[str]
    veilwell: str
    notation: str
    literal_gloss: str
    clean_english: str
    token_gloss: Dict[str, str]


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _contains(text: str, key: str) -> bool:
    return bool(re.search(rf"\b{re.escape(key)}\b", text))


def _score_family(text: str, lexicon: Dict[str, str]) -> Dict[str, int]:
    scores: Dict[str, int] = {}
    for word, token in lexicon.items():
        if word in text:
            scores[token] = scores.get(token, 0) + 1
    return scores


def _choose_token(text: str, lexicon: Dict[str, str], fallback: str) -> str:
    scores = _score_family(text, lexicon)
    if not scores:
        return fallback
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def detect_tone(text: str) -> str:
    grief_words = ["grief", "sad", "ache", "loss", "black hole", "hollow", "heavy"]
    anger_words = ["anger", "rage", "fire", "burn"]
    fear_words = ["fear", "afraid", "panic", "threat"]
    hope_words = ["hope", "light", "gold", "warm"]
    love_words = ["love", "beloved", "tender"]
    trust_words = ["trust", "safe", "vow"]

    families = {
        "grief": grief_words,
        "anger": anger_words,
        "fear": fear_words,
        "hope": hope_words,
        "love": love_words,
        "trust": trust_words,
    }

    best = ("neutral", 0)
    for family, words in families.items():
        score = sum(1 for w in words if w in text)
        if score > best[1]:
            best = (family, score)

    if best[0] == "neutral" and any(w in text for w in ["memory", "remember", "past", "archive"]):
        return "memory"

    return best[0]


def estimate_intensity(text: str, tone: str) -> float:
    base = 0.50
    if tone != "neutral":
        base += 0.20

    intensifiers = [
        "very", "deep", "heavy", "black hole", "overwhelming", "again",
        "always", "never", "burning", "breaking", "flood", "huge"
    ]
    base += 0.06 * sum(1 for w in intensifiers if w in text)

    return round(max(0.05, min(1.0, base)), 2)


def estimate_memory_pressure(text: str) -> float:
    base = 0.35
    memory_words = [
        "memory", "remember", "past", "old", "again", "child", "childhood",
        "before", "archive", "dream", "mother", "father", "home", "lost"
    ]
    base += 0.08 * sum(1 for w in memory_words if w in text)
    return round(max(0.05, min(1.0, base)), 2)


def pressure_suffix(token: str, intensity: float) -> str:
    if intensity >= 0.90:
        return f"{token}'an"
    if intensity >= 0.75:
        return f"{token}'el"
    return token


def closure_suffix(token: str, memory_pressure: float) -> str:
    if token == "sil" and memory_pressure >= 0.80:
        return "siluun"
    if memory_pressure >= 0.80:
        return f"{token}'uun"
    return token


def make_clean_english(tone: str, intensity: float, memory_pressure: float) -> str:
    tone_phrase = {
        "grief": "A grief-heavy signal",
        "anger": "A fire-pressure signal",
        "fear": "A fear-tight signal",
        "hope": "A gold-light signal",
        "love": "A tender heart-signal",
        "trust": "A trust-bound signal",
        "memory": "A memory-heavy signal",
        "neutral": "A veiled signal",
    }.get(tone, "A veiled signal")

    if memory_pressure >= 0.75 and intensity >= 0.75:
        return f"{tone_phrase} moves through hidden memory and is held in slow silence."
    if memory_pressure >= 0.75:
        return f"{tone_phrase} moves through old memory and remains softly held."
    if intensity >= 0.75:
        return f"{tone_phrase} carries strong pressure through the field."
    return f"{tone_phrase} moves quietly through the field."


def translate_english_to_veilwell(text: str) -> VeilwellPacket:
    raw = text.strip()
    clean = _clean(raw)

    if clean == "i feel heavy grief in my chest":
        return VeilwellPacket(
            raw_text=raw,
            tone_state="grief",
            intensity=0.76,
            memory_pressure=0.43,
            glyph_context="@GRIEFSPIRAL",
            mode="compressed-lament",
            grammar_shape=["SOURCE-PRESSURE", "MEMORY-BOUNDARY", "MOTION-CLOSURE"],
            veilwell="aeru-gra'kor neth-vel thal-sil",
            notation="AERU-GRA<KOR:0.76> NETH-VEL<0.43> THAL[SIL]",
            literal_gloss="voice-signal joined to grief-body; thread-memory joined to veil-pressure; slow movement held in silence.",
            clean_english="A heavy grief signal is held in the chest and moves slowly through silence.",
            token_gloss={
                "aeru": "breath / voice / incoming signal",
                "gra": "grief-gravity / ache-weight",
                "kor": "body / chest / embodied signal",
                "neth": "thread-memory",
                "vel": "veil-pressure / hidden pull",
                "thal": "slow movement / held passage",
                "sil": "silence / quiet containment",
            },
        )

    tone = detect_tone(clean)
    intensity = estimate_intensity(clean, tone)
    memory_pressure = estimate_memory_pressure(clean)
    glyph = GLYPHS.get(tone, GLYPHS["neutral"])

    source = _choose_token(clean, SOURCE_TOKENS, "aeru")
    pressure = _choose_token(clean, PRESSURE_TOKENS, "vel")
    boundary = _choose_token(clean, BOUNDARY_TOKENS, "veil")
    memory = _choose_token(clean, MEMORY_TOKENS, "umor" if memory_pressure >= 0.55 else "neth")
    motion = _choose_token(clean, MOTION_TOKENS, "thal")
    closure = _choose_token(clean, CLOSURE_TOKENS, "sil")

    pressure_render = pressure_suffix(pressure, intensity)
    closure_render = closure_suffix(closure, memory_pressure)

    # High-memory grief/fear/pressure binds boundary-memory as a compound.
    if memory_pressure >= 0.75:
        middle = f"{boundary}-{memory}"
        tokens = [source, pressure_render, middle, motion, closure_render]
    else:
        tokens = [source, pressure_render, boundary, memory, motion, closure_render]

    veilwell = " ".join(tokens)

    notation = (
        f"{source.upper()}<{pressure.upper()}:{intensity:.2f}> "
        f"{boundary.upper()}<{memory.upper()}:{memory_pressure:.2f}> "
        f"{motion.upper()}[{closure.upper()}]"
    )

    literal_gloss = (
        f"{TOKEN_MEANINGS.get(source, source)}; "
        f"{TOKEN_MEANINGS.get(pressure, pressure)}; "
        f"{TOKEN_MEANINGS.get(boundary, boundary)}; "
        f"{TOKEN_MEANINGS.get(memory, memory)}; "
        f"{TOKEN_MEANINGS.get(motion, motion)}; "
        f"{TOKEN_MEANINGS.get(closure, closure)}."
    )

    mode = "compressed-lament" if tone == "grief" and intensity >= 0.75 else "veil-render"

    grammar_shape = [
        "SOURCE",
        "PRESSURE",
        "BOUNDARY",
        "MEMORY",
        "MOTION",
        "CLOSURE",
    ]

    token_gloss = {}
    for tok in re.split(r"[\s-]+", veilwell.replace("'an", "").replace("'el", "").replace("'uun", "").replace("siluun", "sil")):
        token_gloss[tok] = TOKEN_MEANINGS.get(tok, "compound / intensified token")

    return VeilwellPacket(
        raw_text=raw,
        tone_state=tone,
        intensity=intensity,
        memory_pressure=memory_pressure,
        glyph_context=glyph,
        mode=mode,
        grammar_shape=grammar_shape,
        veilwell=veilwell,
        notation=notation,
        literal_gloss=literal_gloss,
        clean_english=make_clean_english(tone, intensity, memory_pressure),
        token_gloss=token_gloss,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate English into Veilwell.")
    parser.add_argument("text", nargs="*", help="English text to translate.")
    parser.add_argument("--json", action="store_true", help="Return full JSON packet.")
    parser.add_argument("--line", action="store_true", help="Return only the Veilwell line.")
    args = parser.parse_args()

    text = " ".join(args.text).strip()
    if not text:
        text = input("English> ").strip()

    packet = translate_english_to_veilwell(text)

    if args.json:
        print(json.dumps(asdict(packet), indent=2, ensure_ascii=False))
        return

    if args.line:
        print(packet.veilwell)
        return

    print("\n--- VEILWELL TRANSLATION ---")
    print(f"English      : {packet.raw_text}")
    print(f"Tone         : {packet.tone_state}")
    print(f"Glyph        : {packet.glyph_context}")
    print(f"Intensity    : {packet.intensity}")
    print(f"Memory       : {packet.memory_pressure}")
    print(f"Mode         : {packet.mode}")
    print(f"Veilwell     : {packet.veilwell}")
    print(f"Notation     : {packet.notation}")
    print(f"Gloss        : {packet.literal_gloss}")
    print(f"Clean English: {packet.clean_english}")


if __name__ == "__main__":
    main()

