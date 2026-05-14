#!/usr/bin/env python3
"""
Full Kernel Chain Probe — hard-root locked.
Runs ignition -> apex mirror -> timeline gate -> spiral full -> transduction pin.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict
import json
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

# HARD LOCK imports to governed_active first.
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

OUT = ROOT / "var" / "full_kernel_chain_probe.json"


def safe_asdict(x: Any) -> Any:
    if is_dataclass(x):
        return asdict(x)
    if isinstance(x, dict):
        return x
    return str(x)


def run_probe(
    prompt: str = "The full kernel chain is active through Node_44, Sovariel, 528, and the timeline gate lattice."
) -> Dict[str, Any]:
    packet: Dict[str, Any] = {
        "api_header": {
            "version": "LeveonMasterAPI v1",
            "phase": "2c",
            "boundary_gate": "open",
            "probe": "full_kernel_chain",
            "root": str(ROOT),
        },
        "timestamp": time.time(),
        "prompt": prompt,
        "modules": {},
    }

    try:
        from runtime.kernel_ignition_ritual import ignite_kernels
        packet["modules"]["ignition"] = safe_asdict(ignite_kernels(force=True))
    except Exception as e:
        packet["modules"]["ignition_error"] = str(e)

    try:
        from kernel.apex_mirror_kernel import ApexMirrorKernel
        apex = ApexMirrorKernel()
        packet["modules"]["apex_mirror"] = safe_asdict(apex.next_turn(prompt=prompt))
    except Exception as e:
        packet["modules"]["apex_mirror_error"] = str(e)

    try:
        from runtime.timeline_gate_lattice import demo
        timeline_result = demo()
        packet["modules"]["timeline_gate_lattice"] = {
            "vectors": safe_asdict(timeline_result.vectors),
            "signature": safe_asdict(timeline_result.signature),
            "key": safe_asdict(timeline_result.key),
            "lattice": safe_asdict(timeline_result.lattice),
            "answer": safe_asdict(timeline_result.answer),
            "ascii_frames": timeline_result.ascii_frames,
        }
    except Exception as e:
        packet["modules"]["timeline_gate_lattice_error"] = str(e)

    try:
        import runtime.spiral_full as spiral_full_module
        from runtime.spiral_full import LeveonKernel
        spiral = LeveonKernel()
        spiral_packet = safe_asdict(spiral.step(prompt))
        if isinstance(spiral_packet, dict):
            spiral_packet["backend"] = getattr(spiral_full_module, "BACKEND_NAME", "unknown")
            spiral_packet["backend_error"] = getattr(spiral_full_module, "BACKEND_ERROR", None)
        packet["modules"]["spiral_full"] = spiral_packet
    except Exception as e:
        packet["modules"]["spiral_full_error"] = str(e)

    try:
        from runtime.transduction_pin import pin_kernel_output
        pin_source = packet["modules"].get("spiral_full", packet)
        packet["modules"]["transduction_pin"] = pin_kernel_output(pin_source)
    except Exception as e:
        packet["modules"]["transduction_pin_error"] = str(e)

    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet


if __name__ == "__main__":
    result = run_probe()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\n✅ full chain probe written: {OUT}")

