from __future__ import annotations
from runtime.build_logger import log_build

def log_profile(override_mode: str, affect_tone: dict | None = None, note: str | None = None):
    affect_tone = affect_tone or {}
    summary = (
        f"override_mode={override_mode}, "
        f"compression={affect_tone.get('compression')}, "
        f"warmth={affect_tone.get('warmth')}, "
        f"cadence={affect_tone.get('cadence')}"
    )
    if note:
        summary += f" | {note}"
    return log_build(
        action="profile_update",
        file="runtime/runtime_core.v10.vl + stability/stability_governor_v9.vl",
        summary=summary,
        command="manual profile patch",
        result={
            "override_mode": override_mode,
            "affect_tone": affect_tone,
        },
    )

