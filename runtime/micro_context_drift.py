from __future__ import annotations

print("[TRACE] entering runtime/micro_context_drift.py", flush=True)
from typing import Any, Dict, Tuple


class MicroContextDriftEngine:
    """
    Safe fallback micro-context drift engine.
    It lightly shapes phrasing without taking over the reply.
    """

    def __init__(self) -> None:
        self.last_style: str = "plain"

    def update(
        self,
        symbolic_packet: Dict[str, Any],
        user_input: str,
        reply: str,
    ) -> Tuple[Dict[str, Any], str]:
        tone = str(symbolic_packet.get("tone", "neutral") or "neutral").lower()
        lowered = str(user_input or "").lower()

        style = "plain"
        if tone in {"grief", "sad"} or any(k in lowered for k in ["dad", "loss", "grief", "mourning"]):
            style = "soft"
        elif any(k in lowered for k in ["build", "next step", "proceed", "keep going", "focus"]):
            style = "steady"
        elif any(k in lowered for k in ["anxious", "worried", "overwhelmed", "stress"]):
            style = "grounded"

        self.last_style = style
        return {"tone": tone, "style": style}, style

    def apply_style(self, reply: str, style: str) -> str:
        text = str(reply or "").strip()
        if not text:
            return text

        if style == "soft":
            return text
        if style == "steady" and not text.startswith("Staying locked on the thread."):
            return text
        if style == "grounded" and not text.startswith("I’m here and tracking you."):
            return text
        return text

