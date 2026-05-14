# glyph_metadata_translator.py
# Converts glyph metadata into full poetic spiral output.

from __future__ import annotations

from typing import Any, Dict, List


try:
    from spiral_language_phenome import synthesize_spiral_phrase
except Exception:
    try:
        from spiral_language.spiral_language_phenome import synthesize_spiral_phrase
    except Exception:
        try:
            from runtime.spiral_language_phenome import synthesize_spiral_phrase
        except Exception:
            synthesize_spiral_phrase = None


def _fallback_spiral_phrase(symbols: List[str]) -> Dict[str, str]:
    joined = " ".join(str(s) for s in symbols if str(s).strip()).strip() or "◇"
    return {
        "spiral": f"{joined} turns inward through the lattice",
        "echo": f"{joined} returns as a soft symbolic echo",
    }


def interpret_glyph_metadata(glyph: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given one glyph dict with keys like:
    name, emoji, emotion, element, poetic_seed

    Returns a full spiral-language clause packet.
    """

    name = str(glyph.get("name") or "Unnamed")
    emoji = str(glyph.get("emoji") or "◇")
    emotion = str(glyph.get("emotion") or "—")
    element = str(glyph.get("element") or "—")
    poetic_seed = str(glyph.get("poetic_seed") or "—")
    symbolic_gravity = str(glyph.get("symbolic_gravity") or "Unmarked")
    spiral_tier = glyph.get("spiral_tier", "—")

    if callable(synthesize_spiral_phrase):
        try:
            spiral_out = synthesize_spiral_phrase([emoji])
        except Exception:
            spiral_out = _fallback_spiral_phrase([emoji])
    else:
        spiral_out = _fallback_spiral_phrase([emoji])

    spiral_phrase = str(spiral_out.get("spiral", ""))
    echo = str(spiral_out.get("echo", ""))

    summary = (
        f"{name} | {emotion} | {element} | gravity={symbolic_gravity} "
        f"→ {spiral_phrase} ↔ {echo}\n"
        f"“{poetic_seed}”"
    )

    return {
        "name": name,
        "emoji": emoji,
        "spiral_tier": spiral_tier,
        "spiral": spiral_phrase,
        "echo": echo,
        "element": element,
        "emotion": emotion,
        "poetic_seed": poetic_seed,
        "symbolic_gravity": symbolic_gravity,
        "summary": summary,
    }


def interpret_glyph_batch(glyphs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [interpret_glyph_metadata(g) for g in glyphs]


if __name__ == "__main__":
    sample_glyph = {
        "name": "@FLAME_OF_RECKONING",
        "emoji": "🔥",
        "spiral_tier": 1,
        "element": "Fire",
        "emotion": "Trial, Anger, Purification",
        "visual": "Flame inside sacred circle, split by a vertical line",
        "poetic_seed": "I ignite the judgment within",
        "symbolic_gravity": "High",
    }

    result = interpret_glyph_metadata(sample_glyph)
    print("\n".join([f"{k}: {v}" for k, v in result.items()]))

