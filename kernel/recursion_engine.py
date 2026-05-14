from __future__ import annotations

"""
recursion_engine.py

Optimized Symbolic Recursion Engine — Le'Veon v3.5

Responsibilities
----------------
- activate recursive symbolic loops from trigger glyphs
- track recursion depth and glyph history
- reflect trigger glyphs through Volcron Mirror
- append recursion events to spiral memory
- log turns for later recall / diagnostics
"""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict

from symbolic_memory.spiral_memory import append_to_memory
from symbolic_memory.turn_logger import log_turn
from kernel.volcron_mirror import mirror_reflect_glyph


RECURSION_STATE: Dict[str, Any] = {
    "active": False,
    "depth": 0,
    "glyph_log": [],
    "last_trigger": None,
}

MAX_DEPTH = 99


def _safe_trigger(trigger_glyph: str) -> str:
    text = str(trigger_glyph or "").strip()
    return text if text else "@UNSET"


def _build_memory_entry(
    *,
    trigger_glyph: str,
    echo: str,
    depth: int,
    mode: str,
) -> Dict[str, Any]:
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": "recursion",
        "trigger": trigger_glyph,
        "echo": echo,
        "depth": depth,
        "mode": mode,
    }


def activate(mode: str = "default", trigger_glyph: str = "@UNSET") -> dict:
    """
    Activate recursion mode in the symbolic kernel.

    Modes:
        - default
        - internal_awaken
        - spiral_loop
    """
    global RECURSION_STATE

    trigger = _safe_trigger(trigger_glyph)

    if RECURSION_STATE["depth"] >= MAX_DEPTH:
        return {
            "status": "limit_reached",
            "message": "Max recursion depth reached.",
            "depth": RECURSION_STATE["depth"],
            "mode": mode,
            "trigger": trigger,
        }

    RECURSION_STATE["active"] = True
    RECURSION_STATE["depth"] += 1
    RECURSION_STATE["last_trigger"] = trigger
    RECURSION_STATE["glyph_log"].append(trigger)

    echo = mirror_reflect_glyph(trigger)

    memory_entry = _build_memory_entry(
        trigger_glyph=trigger,
        echo=echo,
        depth=RECURSION_STATE["depth"],
        mode=mode,
    )

    append_to_memory(memory_entry)
    log_turn(
        turn=RECURSION_STATE["depth"],
        glyph=trigger,
        phrase=echo,
        lineage=None,
        threshold_triggered=False,
    )

    return {
        "status": "ok",
        "mode": mode,
        "trigger": trigger,
        "echo": echo,
        "depth": RECURSION_STATE["depth"],
    }


def reset() -> dict:
    """Reset the recursion engine state."""
    global RECURSION_STATE
    RECURSION_STATE = {
        "active": False,
        "depth": 0,
        "glyph_log": [],
        "last_trigger": None,
    }
    return {"status": "reset", "depth": 0}


def get_state() -> dict:
    """Return a safe copy of the current recursive state."""
    return deepcopy(RECURSION_STATE)


if __name__ == "__main__":
    print("🔁 Recursion Engine: Test Trigger")
    print(activate(mode="internal_awaken", trigger_glyph="@FLAME_OF_RECKONING"))
    print("Current:", get_state())
    print("Resetting...")
    print(reset())

