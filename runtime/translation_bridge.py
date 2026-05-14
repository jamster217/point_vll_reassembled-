#!/usr/bin/env python3
from pathlib import Path
import json, time

STATE = Path("var/kernel/translation_bridge_state.json")

def _safe_translate(text):
    # Try spiral language translator first.
    try:
        from language_kernel.spiral_language_translator import translate_phrase
        return translate_phrase(text)
    except Exception:
        pass

    try:
        from spiral_language.spiral_language_translator import translate_phrase
        return translate_phrase(text)
    except Exception:
        pass

    # Fallback: preserve input as already-translated symbolic intent.
    return {
        "raw": text,
        "translated": text,
        "route": "fallback_preserve_input",
    }

def _safe_realize(translated, original):
    """
    Clean surface rule:
    - If translator returns plain text, preserve it.
    - Only call realizers on structured packets/dicts that actually need realization.
    - Never let the realizer mangle already-readable English.
    """
    if isinstance(translated, str):
        return translated.strip() or str(original)

    if isinstance(translated, dict):
        # Prefer explicit translated text if present.
        for key in ("english", "output", "translated", "raw"):
            val = translated.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()

        # Only now try deeper realizers.
        try:
            from core.english_realizer import realize
            out = realize(translated)
            if isinstance(out, str) and out.strip():
                return out.strip()
        except Exception:
            pass

        try:
            from english_layer.english_realizer import realize_english
            out = realize_english(translated)
            if isinstance(out, str) and out.strip():
                return out.strip()
        except Exception:
            pass

    return str(original or "").strip()

def translate_bridge(text):
    translated = _safe_translate(text)
    output = _safe_realize(translated, text)

    packet = {
        "source": "runtime.translation_bridge",
        "bridge": {
            "active": True,
            "strength": 1,
            "route": "voice.lang -> kernel.intent -> english.realizer",
        },
        "input": text,
        "translated": translated,
        "output": output,
        "updated_at": time.time(),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    import sys
    text = " ".join(sys.argv[1:]) or "symbols can mutate anchors out of alignment with signal"
    print(json.dumps(translate_bridge(text), indent=2, ensure_ascii=False))

