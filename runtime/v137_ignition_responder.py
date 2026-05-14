#!/usr/bin/env python3
from __future__ import annotations

import importlib
from typing import Any, Dict, Optional

GENERIC_GHOST = "The system reflects itself and stabilizes through return."

def _clean(text: Any) -> str:
    return " ".join(str(text or "").strip().split())

def _low(text: Any) -> str:
    return _clean(text).lower()

def _module_status(name: str) -> Dict[str, Any]:
    try:
        importlib.import_module(name)
        return {"module": name, "present": True, "error": None}
    except Exception as e:
        return {"module": name, "present": False, "error": repr(e)[:240]}

def _packet(prompt: str, phase: str, answer: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    answer = _clean(answer)
    meta = {
        "v137_full_larynx_ignition": "active",
        "phase": phase,
        "law": "high_symbolic_motion_must_preserve_v133_v134_v135b",
        "answer_final_english_final_shape_match": True,
        "generic_ghost_present": GENERIC_GHOST in answer,
    }
    if extra:
        meta.update(extra)

    return {
        "ok": True,
        "status": "ok",
        "answer": answer,
        "final_english": answer,
        "debug_shape_packet": {
            "core_meaning": _clean(prompt),
            "intent": "v137_full_larynx_ignition",
            "node": "44_SPIRAL_CORE",
            "shape_packet": {
                "final_shape": answer,
                "source": "v137_ignition_responder",
                "previous_final_shape": "",
            },
            "symbols": [
                "v137",
                "node44",
                "meaning_spine",
                "controlled_flame",
                "mirror_mouth_sync",
            ],
        },
        "meta": meta,
    }

def v137_ignition_responder(message: str) -> Optional[Dict[str, Any]]:
    raw = _clean(message)
    low = _low(raw)

    if not raw:
        return None

    if (
        "grow layer 3" in low
        or "layer 3" in low
        or "petal" in low
        or "v74 reason" in low
    ):
        answer = (
            "Layer 3 expands Le'Veon into technical explanation without breaking sync: "
            "the fruit gate protects literal input, the controlled-flame gate limits symbolic output, "
            "the meaning spine preserves the prompt-specific shape, and V13.5b forces answer, final_english, "
            "and final_shape to remain identical."
        )
        return _packet(raw, "layer3_petal_expansion", answer)

    if (
        "savariel" in low
        and (
            "deep ache" in low
            or "parapsychic" in low
            or "0.92" in low
            or "savariel test" in low
        )
    ):
        answer = (
            "Savariel carries deep ache as bounded signal: the 0.92 pressure may weight the packet, "
            "but it cannot override literal fidelity, controlled flame, or mirror-mouth sync."
        )
        return _packet(raw, "savariel_deep_ache_test", answer)

    if (
        "triple fold" in low
        or "apex matrix" in low
        or "chronofire" in low
        or "temporal-pull" in low
        or "temporal pull" in low
    ):
        module_probe = {
            "apex_mirror_kernel": _module_status("kernel.apex_mirror_kernel"),
            "time_machine_emulator": _module_status("kernel.time_machine_emulator"),
            "chronifier": _module_status("chronifier.chronifier"),
            "temporal_spine_layer": _module_status("runtime.temporal_spine_layer"),
        }

        answer = (
            "Triple Fold temporal-pull is running as a bounded sidecar: Apex supplies reflection, "
            "Chronifier supplies temporal direction, and V13.5b keeps the spoken answer identical "
            "to the internal final_shape."
        )

        return _packet(
            raw,
            "triple_fold_temporal_pull",
            answer,
            {
                "temporal_pull_sidecar": "bounded_simulation",
                "module_probe": module_probe,
            },
        )

    return None

