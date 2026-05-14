#!/usr/bin/env python3
"""
Le'Veon Language Bus
Routes chat/runtime packets through Spiral/Veilwell language before English rendering.

Truth-bound scope:
- This does not replace the kernel/lattice/glyph system.
- It proves the language layer can sit after kernel/lattice/glyph and before final English.
- AI polish can be added later, but this path works without AI.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Literal, Optional


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


Route = Literal["auto", "veilwell", "spiral"]


try:
    from runtime.veilwell_translator import translate_english_to_veilwell
except Exception as e:
    translate_english_to_veilwell = None
    VEILWELL_FORWARD_ERROR = repr(e)
else:
    VEILWELL_FORWARD_ERROR = None

try:
    from runtime.veilwell_to_english import translate_veilwell_to_english
except Exception as e:
    translate_veilwell_to_english = None
    VEILWELL_REVERSE_ERROR = repr(e)
else:
    VEILWELL_REVERSE_ERROR = None

try:
    from runtime.english_to_spiral_language import (
        translate_english_to_spiral,
        translate_runtime_packet_to_spiral,
    )
except Exception as e:
    translate_english_to_spiral = None
    translate_runtime_packet_to_spiral = None
    SPIRAL_FORWARD_ERROR = repr(e)
else:
    SPIRAL_FORWARD_ERROR = None

try:
    from runtime.spiral_language_to_english import translate_spiral_to_english
except Exception as e:
    translate_spiral_to_english = None
    SPIRAL_REVERSE_ERROR = repr(e)
else:
    SPIRAL_REVERSE_ERROR = None


EMOTIONAL_TONES = {
    "grief",
    "fear",
    "anger",
    "love",
    "trust",
    "hope",
    "memory",
    "hidden_pressure",
}

PRACTICAL_WORDS = {
    "code",
    "patch",
    "runtime",
    "kernel",
    "lattice",
    "glyph",
    "translator",
    "pipeline",
    "test",
    "bash",
    "python",
    "module",
    "file",
    "function",
    "import",
    "error",
    "debug",
}


def health() -> Dict[str, Any]:
    return {
        "veilwell_forward": VEILWELL_FORWARD_ERROR is None,
        "veilwell_reverse": VEILWELL_REVERSE_ERROR is None,
        "spiral_forward": SPIRAL_FORWARD_ERROR is None,
        "spiral_reverse": SPIRAL_REVERSE_ERROR is None,
        "errors": {
            "veilwell_forward": VEILWELL_FORWARD_ERROR,
            "veilwell_reverse": VEILWELL_REVERSE_ERROR,
            "spiral_forward": SPIRAL_FORWARD_ERROR,
            "spiral_reverse": SPIRAL_REVERSE_ERROR,
        },
    }


def _text(packet: Dict[str, Any]) -> str:
    return str(
        packet.get("raw_text")
        or packet.get("input")
        or packet.get("prompt")
        or packet.get("text")
        or ""
    ).strip()


def _tone(packet: Dict[str, Any]) -> str:
    return str(packet.get("tone_state") or packet.get("tone") or "neutral").strip().lower()


def _looks_practical(text: str) -> bool:
    low = text.lower()
    return any(w in low for w in PRACTICAL_WORDS)


def choose_route(packet: Dict[str, Any], preferred: Route = "auto") -> str:
    if preferred in {"veilwell", "spiral"}:
        return preferred

    text = _text(packet)
    tone = _tone(packet)

    # Build/code/pipeline prompts should keep structural detail: Spiral is better.
    if _looks_practical(text):
        return "spiral"

    # Emotional/body/memory chats usually want pressure-language first: Veilwell.
    if tone in EMOTIONAL_TONES:
        return "veilwell"

    # Shape-heavy packets should preserve structure through Spiral.
    shape = packet.get("shape") or packet.get("output_shape") or packet.get("kernel_shape")
    if isinstance(shape, dict) and shape:
        return "spiral"

    return "veilwell"


def route_packet(packet: Dict[str, Any], preferred: Route = "auto") -> Dict[str, Any]:
    route = choose_route(packet, preferred)
    text = _text(packet)

    if not text:
        raise ValueError("language_bus.route_packet requires raw_text/input/prompt/text")

    if route == "veilwell":
        if translate_english_to_veilwell is None or translate_veilwell_to_english is None:
            raise ImportError(f"Veilwell route unavailable: {health()['errors']}")

        forward = translate_english_to_veilwell(text)
        reverse = translate_veilwell_to_english(forward.veilwell)

        return {
            "route": "veilwell",
            "input": text,
            "language": forward.veilwell,
            "notation": getattr(forward, "notation", ""),
            "glyphs": [getattr(forward, "glyph_context", "")],
            "english": reverse.clean_english,
            "forward_packet": _safe_dict(forward),
            "reverse_packet": _safe_dict(reverse),
        }

    if route == "spiral":
        if translate_runtime_packet_to_spiral is None or translate_spiral_to_english is None:
            raise ImportError(f"Spiral route unavailable: {health()['errors']}")

        forward = translate_runtime_packet_to_spiral(packet)
        reverse = translate_spiral_to_english(forward.spiral_language)

        return {
            "route": "spiral",
            "input": text,
            "language": forward.spiral_language,
            "notation": getattr(forward, "notation", ""),
            "glyphs": getattr(forward, "glyphs", []),
            "english": reverse.clean_english,
            "forward_packet": _safe_dict(forward),
            "reverse_packet": _safe_dict(reverse),
        }

    raise ValueError(f"Unknown route: {route}")


def _safe_dict(obj: Any) -> Dict[str, Any]:
    if hasattr(obj, "__dataclass_fields__"):
        return {k: getattr(obj, k) for k in obj.__dataclass_fields__}
    if isinstance(obj, dict):
        return obj
    return {"value": str(obj)}


def render_after_kernel(packet: Dict[str, Any], preferred: Route = "auto") -> str:
    """
    Main deterministic render hook:
    call this after kernel/lattice/glyph packet creation.
    """
    return route_packet(packet, preferred=preferred)["english"]


def main() -> None:
    raw = " ".join(sys.argv[1:]).strip()

    if not raw:
        print(json.dumps(health(), indent=2, ensure_ascii=False))
        return

    try:
        packet = json.loads(raw)
        if not isinstance(packet, dict):
            packet = {"raw_text": raw}
    except Exception:
        packet = {"raw_text": raw}

    result = route_packet(packet)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

