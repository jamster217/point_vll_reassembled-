from __future__ import annotations

from typing import Any, Dict


STYLE_GOVERNOR_ACTIVE = True


class StyleGovernor:
    @staticmethod
    def select_mode(message: str, meta: dict | None = None) -> str:
        meta = meta or {}
        low = str(message or "").lower()

        anxious_terms = [
            "anxious", "worried", "overwhelmed", "stress",
            "panic", "breathe", "falling apart", "scared",
        ]

        practical_terms = [
            "python", "debug", "traceback", "import", "error", "fix",
            "bash", "flask", "500", "route", "directory", "termux",
        ]

        emotional_terms = [
            "miss", "heavy", "feel", "dad", "grief", "hurt",
            "loss", "photo", "old",
        ]

        if any(term in low for term in anxious_terms):
            return "grounded"

        if any(term in low for term in practical_terms):
            return "steady"

        if bool(meta.get("retrieval_context")) or any(term in low for term in emotional_terms):
            return "soft"

        return "plain"

    def govern(self, text: str = "", context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return govern_style(text, context)

    def apply(self, text: str = "", style: str | None = None, context: Dict[str, Any] | None = None) -> str:
        return apply_style(text, style, context)


def get_style_policy(style_name: str) -> dict:
    policies = {
        "plain": {
            "temp": 0.4,
            "top_p": 0.5,
            "stabilize": False,
            "trim_required": False,
            "max_resonance": 0.5,
        },
        "steady": {
            "temp": 0.2,
            "top_p": 0.1,
            "stabilize": True,
            "trim_required": False,
            "max_resonance": 0.2,
        },
        "grounded": {
            "temp": 0.4,
            "top_p": 0.5,
            "stabilize": True,
            "trim_required": True,
            "max_resonance": 0.2,
        },
        "soft": {
            "temp": 0.7,
            "top_p": 0.9,
            "stabilize": False,
            "trim_required": False,
            "max_resonance": 0.8,
        },
        "clean_public_surface": {
            "temp": 0.3,
            "top_p": 0.4,
            "stabilize": True,
            "trim_required": True,
            "max_resonance": 0.35,
        },
    }
    return policies.get(style_name, policies["plain"])


def get_style_config(mode: str) -> dict:
    policy = get_style_policy(mode)
    return {
        "temp": policy["temp"],
        "top_p": policy["top_p"],
    }


def apply_grounded_surface(reply: str) -> str:
    reply = str(reply or "").strip()

    grounded_rewrites = {
        "This is active around a feeling that something is unresolved and heavy.":
            "This is heavy, so take it one step at a time.",
        "I’m here.":
            "I’m here. Tell me the next exact thing you want to test.",
        "I'm here.":
            "I’m here. Tell me the next exact thing you want to test.",
    }

    return grounded_rewrites.get(reply, reply)


def apply_style_to_final_reply(reply: str, style_policy: dict | None = None) -> str:
    style_policy = style_policy or {}
    text = str(reply or "").strip()

    if style_policy.get("stabilize"):
        text = apply_grounded_surface(text)

    if style_policy.get("trim_required"):
        text = text.replace("internal metadata", "internal details")

    return text.strip()


def govern_style(text: str = "", context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = context or {}
    mode = StyleGovernor.select_mode(text, context)
    return {
        "active": True,
        "mode": mode,
        "style": "clean_public_surface",
        "policy": get_style_policy(mode),
        "law": "preserve intent; remove scaffolding; return visible answer only",
    }


def apply_style(text: str = "", style: str | None = None, context: Dict[str, Any] | None = None) -> str:
    policy = get_style_policy(style or "plain")
    return apply_style_to_final_reply(text, policy)


__all__ = [
    "STYLE_GOVERNOR_ACTIVE",
    "StyleGovernor",
    "get_style_policy",
    "get_style_config",
    "apply_grounded_surface",
    "apply_style_to_final_reply",
    "govern_style",
    "apply_style",
]

