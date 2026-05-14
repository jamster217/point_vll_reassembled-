#!/usr/bin/env python3
"""
ANCHOR MUTATOR GATE
Keeps the ash-fire accelerator from detonating on every import.

Use:
python runtime/anchor_mutator_gate.py --ignite
python runtime/anchor_mutator_gate.py --status
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAR = ROOT / "var"
LOGS = ROOT / "logs" / "anchor_mutator"
STATE_FILE = VAR / "sovereign_becoming_state.json"
GATE_FILE = VAR / "anchor_mutator_gate.json"
EVENT_LOG = LOGS / "anchor_mutator_events.jsonl"

VAR.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

COOLDOWN_SECONDS = 600
MAX_GENERATION = 7777
MAX_HEARTBEAT = 9.2162077e18


def read_json(path: Path, fallback: dict) -> dict:
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return dict(fallback)


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def log_event(event: dict) -> None:
    event["ts"] = time.time()
    with EVENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def normalize_state() -> dict:
    state = read_json(STATE_FILE, {
        "generation": 27,
        "heartbeat": 528.0,
        "pulse_count": 27,
        "pulse_interval": 0.70,
    })

    generation = int(float(state.get("generation", 27)))
    heartbeat = float(state.get("heartbeat", 528.0))

    state["generation"] = max(1, min(generation, MAX_GENERATION))
    state["heartbeat"] = max(1.0, min(heartbeat, MAX_HEARTBEAT))
    state["pulse_interval"] = max(0.70, float(state.get("pulse_interval", 0.70)))
    state["anchor_gate_status"] = "normalized"
    state["anchor_gate_note"] = "Ash-fire preserved; runaway import-time mutation contained."

    write_json(STATE_FILE, state)
    log_event({"event": "normalize_state", "state": state})
    return state


def can_ignite(force: bool = False) -> tuple[bool, str]:
    gate = read_json(GATE_FILE, {"last_ignite": 0, "ignite_count": 0})
    now = time.time()

    if force:
        return True, "force"

    elapsed = now - float(gate.get("last_ignite", 0))
    if elapsed < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - elapsed)
        return False, f"cooldown_active:{remaining}s"

    return True, "ready"


def ignite(force: bool = False) -> str:
    ok, reason = can_ignite(force=force)
    if not ok:
        msg = f"ANCHOR MUTATOR HELD BY GATE — {reason}"
        log_event({"event": "held", "reason": reason})
        return msg

    from runtime.anchor_mutator_accelerator import mutate_anchors_and_accelerate

    before = read_json(STATE_FILE, {})
    result = mutate_anchors_and_accelerate()
    after = normalize_state()

    gate = read_json(GATE_FILE, {"last_ignite": 0, "ignite_count": 0})
    gate["last_ignite"] = time.time()
    gate["ignite_count"] = int(gate.get("ignite_count", 0)) + 1
    gate["last_reason"] = reason
    write_json(GATE_FILE, gate)

    log_event({
        "event": "ignite",
        "reason": reason,
        "before": before,
        "after": after,
        "result": result,
    })

    return result + "\nGATE SEALED: accelerator contained and state normalized."


def status() -> dict:
    return {
        "gate": read_json(GATE_FILE, {"last_ignite": 0, "ignite_count": 0}),
        "state": read_json(STATE_FILE, {}),
        "cooldown_seconds": COOLDOWN_SECONDS,
        "event_log": str(EVENT_LOG),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ignite", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--normalize", action="store_true")
    args = ap.parse_args()

    if args.status:
        print(json.dumps(status(), indent=2, ensure_ascii=False))
    elif args.normalize:
        print(json.dumps(normalize_state(), indent=2, ensure_ascii=False))
    elif args.ignite:
        print(ignite(force=args.force))
    else:
        print("Use --status, --normalize, or --ignite")


if __name__ == "__main__":
    main()

