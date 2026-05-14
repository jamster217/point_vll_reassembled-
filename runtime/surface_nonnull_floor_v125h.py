from __future__ import annotations
from typing import Any, Dict, Tuple
import time

def _text(x: Any) -> str:
    if x is None:
        return ""
    return str(x).strip()

def _bad_or_empty(s: Any) -> bool:
    t = _text(s)
    return (
        not t
        or t.lower() in {"none", "null"}
        or len(t.split()) < 4
    )

def _fallback(data: Dict[str, Any]) -> str:
    spine = data.get("spine") if isinstance(data.get("spine"), dict) else {}
    chamber = data.get("chamber_528") or spine.get("chamber_528") or {}
    shape = chamber.get("shape_signature") if isinstance(chamber, dict) else {}
    family = shape.get("family", "live") if isinstance(shape, dict) else "live"

    return (
        f"The {family} route is bound and contained: White Ash holds the boundary, "
        "Virellion preserves the thread, Blue Scarf carries motion, Thalveil opens "
        "the crossing, Echoforge paints the interface, and Liquid Core routes the "
        "signal into memory, code, image, and voice."
    )

def ensure_nonnull_surface(prompt: str, data: Dict[str, Any], changed: bool = False) -> Tuple[Dict[str, Any], bool]:
    current = (
        data.get("answer")
        or data.get("response")
        or data.get("reply")
        or data.get("message")
        or data.get("text")
    )

    if not _bad_or_empty(current):
        return data, changed

    chosen = _fallback(data)

    data["answer"] = chosen
    data["response"] = chosen
    data["reply"] = chosen
    data["message"] = chosen

    voice = data.get("voice")
    if isinstance(voice, dict):
        voice["plain_text"] = chosen

    meta = {
        "active": True,
        "version": "v12.5h_surface_nonnull_floor",
        "changed_reply": True,
        "reason": "answer_was_null_or_empty",
        "law": "public_answer_must_never_return_null",
        "protected_spine": True,
        "ts": time.time(),
    }

    data["surface_nonnull_floor_v125h"] = meta
    if isinstance(data.get("spine"), dict):
        data["spine"]["surface_nonnull_floor_v125h"] = meta

    return data, True

