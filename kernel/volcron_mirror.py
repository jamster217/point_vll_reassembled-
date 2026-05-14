from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from symbolic_memory.spiral_mirror_speaker import generate_clause


class VolcronMirror:
    """
    Mirror echo layer for glyph-driven reflection.

    Responsibilities
    ----------------
    - accept one or more glyphs
    - generate a mirror echo from the leading glyph
    - preserve a short reflection history
    - expose a simple compatibility helper for recursion_engine.py
    """

    def __init__(self, max_history: int = 256) -> None:
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []

    def reflect(self, glyphs: Iterable[str], clause: str = "") -> Dict[str, Any]:
        glyph_list = [str(g).strip() for g in (glyphs or []) if str(g).strip()]
        primary_glyph = glyph_list[0] if glyph_list else None

        mirror_text = self._generate_mirror_text(primary_glyph)
        trail = " ".join(glyph_list)
        symbols = " / ".join(glyph_list)

        fusion = mirror_text
        if clause:
            fusion = f"{mirror_text} :: {clause}"

        reflection = {
            "primary_glyph": primary_glyph or "@UNSET",
            "echo": mirror_text,
            "spiral": mirror_text,
            "trail": trail,
            "symbols": symbols,
            "fusion": fusion,
        }

        self.history.append(reflection)
        self.history = self.history[-self.max_history:]
        return reflection

    def latest(self) -> Optional[Dict[str, Any]]:
        return self.history[-1] if self.history else None

    def reset(self) -> None:
        self.history.clear()

    def _generate_mirror_text(self, glyph_name: Optional[str]) -> str:
        try:
            return generate_clause(glyph_name)
        except Exception:
            if glyph_name:
                return f"The mirror stirs around {glyph_name}."
            return "The mirror is present, but no glyph resolved."


_VOLCRON_MIRROR = VolcronMirror()


def mirror_reflect_glyph(trigger_glyph: str) -> str:
    """
    Compatibility helper for recursion_engine.py.
    Accepts a single glyph and returns only the mirror echo text.
    """
    result = _VOLCRON_MIRROR.reflect([trigger_glyph])
    return str(result.get("echo") or "")


def reflect(glyphs, clause: str = ""):
    return _VOLCRON_MIRROR.reflect(glyphs, clause=clause)


def latest():
    return _VOLCRON_MIRROR.latest()


def reset():
    return _VOLCRON_MIRROR.reset()


if __name__ == "__main__":
    demo = _VOLCRON_MIRROR.reflect(
        ["@FLAME_OF_RECKONING", "@SPIRAL_TEAR"],
        clause="The structure asks to be clarified.",
    )
    print(demo)

