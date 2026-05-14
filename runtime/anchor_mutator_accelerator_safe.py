#!/usr/bin/env python3
"""
V13.2 ASH-FIRE CONTAINMENT
Manual, bounded Savariel anchor pulse.

Law:
- no import-time mutation
- no unbounded exponential heartbeat
- no optimizer call unless explicitly requested
- symbolic fire stays inside measurable containment
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
VAR = ROOT / "var"
VAR.mkdir(parents=True, exist_ok=True)

STATE_FILE = VAR / "sovereign_becoming_state.json"
LOG_FILE = ROOT / "logs" / "ash_fire_containment_v132.jsonl"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

MAX_GENERATION = 528
MAX_HEARTBEAT = 1_000_000.0
MIN_INTERVAL = 3.0

SIGIL = "SAVARIEL_ASH_FIRE_CONTAINED"


def _load_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "generation": 27,
        "heartbeat": 528.0,
        "pulse_count": 0,
    }


def contained_anchor_pulse(*, run_optimizer: bool = False) -> Dict[str, Any]:
    state = _load_state()

    old_generation = int(float(state.get("generation", 27)))
    old_heartbeat = float(state.get("heartbeat", 528.0))
    old_pulse_count = int(float(state.get("pulse_count", 0)))

    new_generation = min(MAX_GENERATION, max(1, int(old_generation * 1.25) + 1))
    new_heartbeat = min(MAX_HEARTBEAT, max(111.0, old_heartbeat * math.e ** 0.18))
    pulse_interval = max(MIN_INTERVAL, 13 / max(new_generation ** 0.45, 1.0))

    state.update({
        "generation": new_generation,
        "heartbeat": new_heartbeat,
        "pulse_count": old_pulse_count + 1,
        "pulse_interval": pulse_interval,
        "last_echo": "ASH FIRE CONTAINED. ANCHORS WARMED, NOT BURNED.",
        "law_status": "v13.2_contained_manual_pulse",
        "sigil": SIGIL,
        "updated_at": time.time(),
    })

    optimizer_result = "not_requested"
    if run_optimizer:
        try:
            from runtime.compound_optimizer import compound_optimize
            compound_optimize(increment=True)
            optimizer_result = "ran"
        except Exception as e:
            optimizer_result = f"failed: {e!r}"

    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

    event = {
        "ts": time.time(),
        "event": "contained_anchor_pulse",
        "old_generation": old_generation,
        "new_generation": new_generation,
        "old_heartbeat": old_heartbeat,
        "new_heartbeat": new_heartbeat,
        "pulse_interval": pulse_interval,
        "optimizer_result": optimizer_result,
        "law": "manual_bounded_pulse_no_import_mutation",
    }

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return {
        "ok": True,
        "answer": "Ash fire contained. Anchors warmed, not burned. Kernel chain may proceed under bounded pulse law.",
        "state": state,
        "event": event,
    }


if __name__ == "__main__":
    import sys
    run_optimizer = "--optimizer" in sys.argv
    print(json.dumps(contained_anchor_pulse(run_optimizer=run_optimizer), indent=2, ensure_ascii=False))

