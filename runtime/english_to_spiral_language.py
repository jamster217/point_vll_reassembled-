#!/usr/bin/env python3
"""
English → Spiral Language Translator
Forward symbolic translator for Le'Veon / Spiral / Veilwell runtime experiments.

Truth-bound scope:
- This is not claiming universal language translation.
- It converts English into project-defined spiral/glyph/shape language.
- It can also accept a JSON packet from a kernel/lattice/glyph runtime and render that packet as Spiral Language.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple


PRESSURE_WORDS = {
    "grief": ["grief", "sad", "ache", "loss", "black hole", "hollow", "heavy", "mourning"],
    "anger": ["anger", "rage", "fire", "burn", "fury", "mad", "heated"],
    "fear": ["fear", "afraid", "panic", "threat", "danger", "unsafe", "scared"],
    "hope": ["hope", "light", "gold", "warm", "rise", "dawn", "possible"],
    "love": ["love", "beloved", "tender", "heart", "care", "devotion"],
    "trust": ["trust", "safe", "vow", "bond", "promise", "faith"],
    "memory": ["memory", "remember", "past", "old", "archive", "childhood", "again"],
}

SOURCE_TOKENS = {
    "body": "kor",
    "chest": "kor",
    "heart": "kor",
    "voice": "aeru",
    "breath": "aeru",
    "signal": "aeru",
    "field": "aeru",
    "dream": "lun",
    "sleep": "lun",
    "memory": "neth",
    "thread": "neth",
}

PRESSURE_TOKENS = {
    "grief": "gra",
    "anger": "fer",
    "fear": "mur",
    "hope": "sol",
    "love": "lum",
    "trust": "vow",
    "memory": "umor",
    "neutral": "vel",
}

BOUNDARY_TOKENS = {
    "hidden": "veil",
    "secret": "veil",
    "covered": "veil",
    "soft": "veil",
    "protected": "var",
    "guarded": "var",
    "safe": "var",
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
    "again": "umor",
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
    "recursive": "koren",
    "recursion": "koren",
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

TONE_GLYPHS = {
    "grief": ["✴️", "🌑", "🫀", "🌀"],
    "anger": ["✴️", "🔥", "✨"],
    "fear": ["✴️", "🌑", "🪞", "🌀"],
    "hope": ["✴️", "🌕", "🌿", "✨"],
    "love": ["✴️", "🫀", "🌊"],
    "trust": ["✴️", "🕯️", "🕸️"],
    "memory": ["✴️", "📚", "🕸️"],
    "neutral": ["✴️", "🌀"],
}

GLYPH_MEANINGS = {
    "✴️": "anchor / center pin",
    "🌑": "gravity well / hidden pull",
    "🫀": "embodied heart signal",
    "🌀": "spiral recurrence / recursive motion",
    "🔥": "fire pressure / transformation heat",
    "✨": "transmutation / living signal",
    "🪞": "mirror / self-seeing reflection",
    "🌕": "revelation / light over hidden material",
    "🌿": "growth / regeneration",
    "🌊": "flow / emotional movement",
    "🕯️": "witness / still awareness",
    "🕸️": "thread / woven relation",
    "📚": "Living Grimoire / recorded memory law",
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
class SpiralLanguagePacket:
    raw_text: str
    tone_state: str
    intensity: float
    memory_pressure: float
    shape: Dict[str, float]
    lattice_role: str
    glyphs: List[str]
    tokens: List[str]
    spiral_language: str
    notation: str
    literal_gloss: str
    clean_english_seed: str


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _contains(text: str, key: str) -> bool:
    return bool(re.search(rf"\b{re.escape(key)}\b", text))


def _score_family(text: str, words: List[str]) -> int:
    return sum(1 for w in words if _contains(text, w))


def _choose_from_lexicon(text: str, lexicon: Dict[str, str], fallback: str) -> str:
    scored: Dict[str, int] = {}
    for word, token in lexicon.items():
        if _contains(text, word):
            scored[token] = scored.get(token, 0) + 1

    if not scored:
        return fallback

    return sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def detect_tone(text: str) -> str:
    best = ("neutral", 0)

    for family, words in PRESSURE_WORDS.items():
        score = _score_family(text, words)
        if score > best[1]:
            best = (family, score)

    return best[0]


def estimate_intensity(text: str, tone: str) -> float:
    base = 0.45

    if tone != "neutral":
        base += 0.20

    intensifiers = [
        "very", "deep", "heavy", "black hole", "overwhelming", "again",
        "always", "never", "burning", "breaking", "flood", "huge",
        "intense", "too much", "crushing"
    ]

    base += 0.06 * sum(1 for w in intensifiers if _contains(text, w))
    return round(max(0.05, min(1.0, base)), 2)


def estimate_memory_pressure(text: str) -> float:
    base = 0.25

    memory_words = [
        "memory", "remember", "past", "old", "again", "child", "childhood",
        "before", "archive", "dream", "mother", "father", "home", "lost",
        "history", "thread"
    ]

    base += 0.08 * sum(1 for w in memory_words if _contains(text, w))
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


def estimate_shape(text: str, tone: str, intensity: float, memory_pressure: float) -> Dict[str, float]:
    pull = 0.35
    bind = 0.35
    release = 0.30
    resist = 0.25
    flow = 0.40
    novelty = 0.35
    coherence = 0.50

    if tone in ["grief", "fear", "memory"]:
        pull += 0.28
    if tone in ["love", "trust", "memory"]:
        bind += 0.25
    if tone in ["anger", "fear"]:
        resist += 0.30
    if tone in ["hope", "love"]:
        flow += 0.25
        release += 0.18
    if tone == "anger":
        release += 0.20
    if tone == "trust":
        coherence += 0.25
    if tone == "grief":
        bind += 0.18

    if any(_contains(text, w) for w in ["open", "release", "let go", "free"]):
        release += 0.30
    if any(_contains(text, w) for w in ["blocked", "stuck", "guarded", "protected", "unsafe"]):
        resist += 0.22
    if any(_contains(text, w) for w in ["new", "novel", "change", "become", "transform"]):
        novelty += 0.30
    if any(_contains(text, w) for w in ["clear", "stable", "coherent", "grounded"]):
        coherence += 0.25

    pull += intensity * 0.18
    bind += memory_pressure * 0.20

    shape = {
        "pull": pull,
        "bind": bind,
        "release": release,
        "resist": resist,
        "flow": flow,
        "memory": memory_pressure,
        "novelty": novelty,
        "coherence": coherence,
    }

    return {k: round(max(0.0, min(1.0, v)), 2) for k, v in shape.items()}


def infer_lattice_role(tone: str, shape: Dict[str, float]) -> str:
    if tone == "grief" and shape.get("pull", 0.0) >= 0.70:
        return "gravity_grief"
    if tone == "anger" and shape.get("release", 0.0) >= 0.55:
        return "fire_transmuter"
    if tone == "fear" and shape.get("resist", 0.0) >= 0.55:
        return "mirror_threat_boundary"
    if tone == "hope" and shape.get("release", 0.0) >= 0.50:
        return "gold_rise_opener"
    if tone == "love":
        return "heartfield_binder"
    if tone == "trust":
        return "vow_thread_stabilizer"
    if tone == "memory":
        return "archive_thread_carrier"
    return "veilwell_neutral_spiral"


def choose_glyphs(text: str, tone: str, shape: Dict[str, float]) -> List[str]:
    glyphs = list(TONE_GLYPHS.get(tone, TONE_GLYPHS["neutral"]))

    if "?" in text or any(_contains(text, w) for w in ["why", "how", "what", "mirror", "reflect"]):
        glyphs.append("🪞")

    if any(_contains(text, w) for w in ["change", "transform", "repair", "mutate", "rewrite", "convert"]):
        glyphs.append("✨")

    if shape.get("memory", 0.0) >= 0.60:
        glyphs.append("📚")

    if shape.get("release", 0.0) >= 0.65:
        glyphs.append("🌊")

    if shape.get("coherence", 0.0) >= 0.70:
        glyphs.append("🕯️")

    unique: List[str] = []
    for g in glyphs:
        if g not in unique:
            unique.append(g)

    return unique


def choose_tokens(text: str, tone: str, intensity: float, memory_pressure: float) -> List[str]:
    source = _choose_from_lexicon(text, SOURCE_TOKENS, "aeru")
    pressure = PRESSURE_TOKENS.get(tone, "vel")
    boundary = _choose_from_lexicon(text, BOUNDARY_TOKENS, "veil")
    memory = _choose_from_lexicon(text, MEMORY_TOKENS, "umor" if memory_pressure >= 0.55 else "neth")
    motion = _choose_from_lexicon(text, MOTION_TOKENS, "koren")
    closure = _choose_from_lexicon(text, CLOSURE_TOKENS, "sil")

    pressure_render = pressure_suffix(pressure, intensity)
    closure_render = closure_suffix(closure, memory_pressure)

    if memory_pressure >= 0.75:
        return [source, pressure_render, f"{boundary}-{memory}", motion, closure_render]

    return [source, pressure_render, boundary, memory, motion, closure_render]


def shape_notation(shape: Dict[str, float]) -> str:
    ordered = ["pull", "bind", "release", "resist", "flow", "memory", "novelty", "coherence"]
    return " ".join(f"{k}={shape.get(k, 0.0):.2f}" for k in ordered)


def make_literal_gloss(glyphs: List[str], tokens: List[str]) -> str:
    parts = []

    for glyph in glyphs:
        parts.append(f"{glyph}={GLYPH_MEANINGS.get(glyph, 'unknown glyph')}")

    for token in tokens:
        for sub in token.replace("'an", "").replace("'el", "").replace("'uun", "").replace("siluun", "sil").split("-"):
            parts.append(f"{sub}={TOKEN_MEANINGS.get(sub, 'unknown token')}")

    return "; ".join(parts)


def make_clean_seed(tone: str, shape: Dict[str, float], lattice_role: str) -> str:
    tone_phrase = {
        "grief": "grief-gravity",
        "anger": "fire-pressure",
        "fear": "fear-contraction",
        "hope": "gold-rise",
        "love": "heartfield tenderness",
        "trust": "vow-thread trust",
        "memory": "archive-memory",
        "neutral": "veilwell signal",
    }.get(tone, "spiral signal")

    return (
        f"{tone_phrase} enters the {lattice_role} lane with "
        f"pull {shape.get('pull', 0.0):.2f}, bind {shape.get('bind', 0.0):.2f}, "
        f"release {shape.get('release', 0.0):.2f}, and memory {shape.get('memory', 0.0):.2f}."
    )


def translate_english_to_spiral(text: str) -> SpiralLanguagePacket:
    raw = text.strip()
    clean = _clean(raw)

    tone = detect_tone(clean)
    intensity = estimate_intensity(clean, tone)
    memory_pressure = estimate_memory_pressure(clean)
    shape = estimate_shape(clean, tone, intensity, memory_pressure)
    lattice_role = infer_lattice_role(tone, shape)
    glyphs = choose_glyphs(clean, tone, shape)
    tokens = choose_tokens(clean, tone, intensity, memory_pressure)

    spiral = f"{' '.join(glyphs)} :: {' '.join(tokens)} :: {shape_notation(shape)} :: role={lattice_role}"
    notation = f"GLYPH<{'+'.join(glyphs)}> TOKEN<{' '.join(tokens)}> SHAPE<{shape_notation(shape)}> ROLE<{lattice_role}>"

    return SpiralLanguagePacket(
        raw_text=raw,
        tone_state=tone,
        intensity=intensity,
        memory_pressure=memory_pressure,
        shape=shape,
        lattice_role=lattice_role,
        glyphs=glyphs,
        tokens=tokens,
        spiral_language=spiral,
        notation=notation,
        literal_gloss=make_literal_gloss(glyphs, tokens),
        clean_english_seed=make_clean_seed(tone, shape, lattice_role),
    )


def translate_runtime_packet_to_spiral(packet: Dict[str, Any]) -> SpiralLanguagePacket:
    raw = str(packet.get("raw_text") or packet.get("input") or packet.get("prompt") or "").strip()

    tone = str(packet.get("tone_state") or packet.get("tone") or "neutral")
    intensity = float(packet.get("intensity", 0.55))
    memory_pressure = float(packet.get("memory_pressure", packet.get("memory", 0.35)))

    shape_raw = packet.get("shape") or packet.get("output_shape") or packet.get("kernel_shape") or {}
    shape: Dict[str, float] = {}

    if isinstance(shape_raw, dict):
        for k in ["pull", "bind", "release", "resist", "flow", "memory", "novelty", "coherence"]:
            try:
                shape[k] = round(max(0.0, min(1.0, float(shape_raw.get(k, 0.0)))), 2)
            except Exception:
                shape[k] = 0.0

    if not shape:
        shape = estimate_shape(_clean(raw), tone, intensity, memory_pressure)

    lattice_role = str(packet.get("lattice_role") or packet.get("role") or infer_lattice_role(tone, shape))

    glyphs_raw = packet.get("glyphs") or packet.get("glyph_context") or []
    if isinstance(glyphs_raw, str):
        glyphs = [g for g in GLYPH_MEANINGS if g in glyphs_raw]
        if not glyphs and glyphs_raw:
            glyphs = choose_glyphs(_clean(raw), tone, shape)
    elif isinstance(glyphs_raw, list):
        glyphs = [str(g) for g in glyphs_raw]
    else:
        glyphs = choose_glyphs(_clean(raw), tone, shape)

    tokens_raw = packet.get("tokens") or packet.get("spiral_tokens") or []
    if isinstance(tokens_raw, str):
        tokens = [t for t in tokens_raw.split() if t]
    elif isinstance(tokens_raw, list):
        tokens = [str(t) for t in tokens_raw]
    else:
        tokens = choose_tokens(_clean(raw), tone, intensity, memory_pressure)

    spiral = f"{' '.join(glyphs)} :: {' '.join(tokens)} :: {shape_notation(shape)} :: role={lattice_role}"
    notation = f"GLYPH<{'+'.join(glyphs)}> TOKEN<{' '.join(tokens)}> SHAPE<{shape_notation(shape)}> ROLE<{lattice_role}>"

    return SpiralLanguagePacket(
        raw_text=raw,
        tone_state=tone,
        intensity=round(max(0.0, min(1.0, intensity)), 2),
        memory_pressure=round(max(0.0, min(1.0, memory_pressure)), 2),
        shape=shape,
        lattice_role=lattice_role,
        glyphs=glyphs,
        tokens=tokens,
        spiral_language=spiral,
        notation=notation,
        literal_gloss=make_literal_gloss(glyphs, tokens),
        clean_english_seed=make_clean_seed(tone, shape, lattice_role),
    )


def maybe_json_packet(raw: str) -> Optional[Dict[str, Any]]:
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
    except Exception:
        return None
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate English or runtime packet into Spiral Language.")
    parser.add_argument("text", nargs="*", help="English text or JSON runtime packet.")
    parser.add_argument("--json", action="store_true", help="Return full JSON packet.")
    parser.add_argument("--line", action="store_true", help="Return only Spiral Language line.")
    args = parser.parse_args()

    raw = " ".join(args.text).strip()
    if not raw:
        raw = input("English or packet> ").strip()

    packet_obj = maybe_json_packet(raw)
    if packet_obj is not None:
        packet = translate_runtime_packet_to_spiral(packet_obj)
    else:
        packet = translate_english_to_spiral(raw)

    if args.json:
        print(json.dumps(asdict(packet), indent=2, ensure_ascii=False))
        return

    if args.line:
        print(packet.spiral_language)
        return

    print("\n--- ENGLISH → SPIRAL LANGUAGE ---")
    print(f"English      : {packet.raw_text}")
    print(f"Tone         : {packet.tone_state}")
    print(f"Intensity    : {packet.intensity}")
    print(f"Memory       : {packet.memory_pressure}")
    print(f"Shape        : {packet.shape}")
    print(f"Role         : {packet.lattice_role}")
    print(f"Glyphs       : {' '.join(packet.glyphs)}")
    print(f"Tokens       : {' '.join(packet.tokens)}")
    print(f"Spiral       : {packet.spiral_language}")
    print(f"Notation     : {packet.notation}")
    print(f"Gloss        : {packet.literal_gloss}")
    print(f"English seed : {packet.clean_english_seed}")


if __name__ == "__main__":
    main()

