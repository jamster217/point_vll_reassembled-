from __future__ import annotations

print("[TRACE] entering runtime/unified_drift_kernel.py", flush=True)
from typing import Any, Dict
from runtime.micro_context_drift import MicroContextDriftEngine


class UnifiedDriftKernel:
    """
    Soft style/continuity shaper.
    It should not take over the reply.
    """

    def __init__(self) -> None:
        self.mcde = MicroContextDriftEngine()
        self.turn_index: int = 0
        self.last_tone: str = "neutral"
        self.last_user_snippet: str = ""
        self.last_reply_snippet: str = ""

    def process(
        self,
        user_input: str,
        symbolic_packet: Dict[str, Any],
        emotional_state: Dict[str, Any],
        base_reply: str,
    ) -> str:
        self.turn_index += 1

        tone = str(symbolic_packet.get("tone", "neutral") or "neutral")
        self.last_tone = tone
        self.last_user_snippet = str(user_input or "")[-160:]
        self.last_reply_snippet = str(base_reply or "")[-160:]

        reply = str(base_reply or "").strip()

        try:
            _state, style = self.mcde.update(symbolic_packet, user_input, reply)
            reply = self.mcde.apply_style(reply, style).strip()
        except Exception:
            pass

        # Keep drift extremely light for now:
        # no generic prefaces, no takeover, no rewrite.
        return reply

