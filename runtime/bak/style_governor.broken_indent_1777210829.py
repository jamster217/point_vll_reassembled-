from __future__ import annotations

from typing import Any, Dict


STYLE_GOVERNOR_ACTIVE = True


def govern_style(text: str = "", context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Safe style governor shim.

    Keeps public output clean without exposing internal machinery.
    This module is intentionally conservative: it does not mutate source,
    does not leak debug fields, and returns a simple routing/style packet.
    """
    context = context or {}

    return {
        "active": True,
        "style": "clean_public_surface",
        "tone": context.get("tone", "steady"),
        "text": str(text or ""),
        "law": "preserve intent; remove scaffolding; return visible answer only",
    }


def apply_style(text: str = "", style: str | None = None, context: Dict[str, Any] | None = None) -> str:
    """
    Return clean visible text. The style parameter is accepted for compatibility.
    """
    return str(text or "").strip()


class StyleGovernor:
    def govern(self, text: str = "", context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return govern_style(text, context)

    def apply(self, text: str = "", style: str | None = None, context: Dict[str, Any] | None = None) -> str:
        return apply_style(text, style, context)

