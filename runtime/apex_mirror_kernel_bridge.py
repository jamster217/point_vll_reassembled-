#!/usr/bin/env python3
from pathlib import Path
import json, time

STATE = Path("var/apex/apex_mirror_kernel_bridge_state.json")

def invoke(intake_packet=None, symbolic_packet=None, memory_packet=None, kernel_packet=None):
    intake_packet = intake_packet or {}
    symbolic_packet = symbolic_packet or {}
    memory_packet = memory_packet or {}
    kernel_packet = kernel_packet or {}

    packet = {
        "source": "runtime.apex_mirror_kernel_bridge",
        "mode": "apex_mirror",
        "turn_path": kernel_packet.get("turn_path", "mirror->symbolic->kernel"),
        "symbolic_directive": kernel_packet.get(
            "symbolic_directive",
            symbolic_packet.get("symbolic_directive", "reflect_without_destructive_rewrite")
        ),
        "inputs_seen": {
            "intake": bool(intake_packet),
            "symbolic": bool(symbolic_packet),
            "memory": bool(memory_packet),
            "kernel": bool(kernel_packet),
        },
        "apex_bridge_packet": {
            "mode": "apex_mirror",
            "turn_path": kernel_packet.get("turn_path", "mirror->symbolic->kernel"),
            "symbolic_directive": kernel_packet.get(
                "symbolic_directive",
                symbolic_packet.get("symbolic_directive", "reflect_without_destructive_rewrite")
            ),
        },
        "updated_at": time.time(),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    sample = invoke(
        intake_packet={"raw_text": "symbols can mutate anchors out of alignment with signal"},
        symbolic_packet={
            "dominant_symbols": ["symbol", "anchor", "signal"],
            "symbolic_directive": "preserve_signal_alignment"
        },
        memory_packet={"continuity_weight": 0.25},
        kernel_packet={
            "turn_path": "intake->symbolic->apex_mirror->kernel",
            "symbolic_directive": "preserve_signal_alignment"
        }
    )
    print(json.dumps(sample, indent=2, ensure_ascii=False))

