#!/usr/bin/env python3
from pathlib import Path
import json, time

STATE = Path("var/apex/apex_mirror_brain_state.json")

def _safe_get(packet, path, default=None):
    cur = packet if isinstance(packet, dict) else {}
    for part in path.split("."):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(part, default)
    return cur

def observe(intake_packet=None, symbolic_packet=None, memory_packet=None, kernel_packet=None):
    intake_packet = intake_packet or {}
    symbolic_packet = symbolic_packet or {}
    memory_packet = memory_packet or {}
    kernel_packet = kernel_packet or {}

    apex_brain_packet = {
        "brain_mode": "evolving_reflective",
        "symbolic_bias": symbolic_packet.get("dominant_symbols", []),
        "continuity_weight": memory_packet.get("continuity_weight", 0.0),
        "kernel_alignment": kernel_packet.get("turn_path", None),
        "constraints": {
            "destructive_rewrite": 0,
            "direct_memory_write": 0,
            "unsafe_self_modify": 0
        },
        "input_hint": intake_packet.get("raw_text") or intake_packet.get("input"),
        "updated_at": time.time(),
        "source": "runtime.apex_mirror_brain"
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(apex_brain_packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return apex_brain_packet

if __name__ == "__main__":
    sample = observe(
        intake_packet={"raw_text": "symbols can mutate anchors out of alignment with signal"},
        symbolic_packet={"dominant_symbols": ["anchor", "signal", "mutation"]},
        memory_packet={"continuity_weight": 0.25},
        kernel_packet={"turn_path": "mirror->symbolic->kernel"}
    )
    print(json.dumps(sample, indent=2, ensure_ascii=False))

