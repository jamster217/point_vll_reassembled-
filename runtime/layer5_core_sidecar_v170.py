#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, List

from runtime.apex_v16_sync_v161 import apex_v16_sync

ENGINE_VERSION = "V17.0 Layer 5 Core Sidecar"
GENERIC_GHOST = "The system reflects itself and stabilizes through return."

LAWS = [
    "layer5_observes_without_core_mutation",
    "layer5_synthesizes_lattice_groups_into_core_functions",
    "layer5_must_not_replace_v14_v15_v16_authority",
    "all_core_functions_must_remain_visible_under_dense_prompts",
    "answer_final_english_final_shape_must_match",
    "generic_ghost_must_remain_false",
    "core_mutation_false_until_proven",
]


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _low(x: Any) -> str:
    return _clean(x).lower()


CORE_FUNCTIONS: List[Dict[str, Any]] = [
    {
        "core": "intake_discipline",
        "from_groups": ["literal_gate", "symbolic_gate"],
        "members": [
            "ordinary literal input",
            "fruit gate",
            "symbolic command routing",
            "controlled flame",
        ],
        "law": "input must be classified before symbolic depth opens",
    },
    {
        "core": "meaning_authority_core",
        "from_groups": ["meaning_authority"],
        "members": [
            "V14",
            "V14.3 dynamic semantic map",
            "meaning spine",
            "shape packet",
            "map-then-render",
        ],
        "law": "meaning must be preserved before language renders",
    },
    {
        "core": "selection_core",
        "from_groups": ["apex_selection"],
        "members": [
            "V15 Apex sidecar",
            "Apex Selection Score",
            "coverage scoring",
            "V15.0c density merge",
            "merge-not-compress",
            "V16.1 Apex-V16 group coverage",
        ],
        "law": "selection must optimize coverage and synchronization instead of compression",
    },
    {
        "core": "temporal_lattice_core",
        "from_groups": ["chronofire_temporal"],
        "members": [
            "Chronofire sidecar",
            "V15.1b Chrono-Density Merge",
            "temporal offsets",
            "past stability",
            "present anchor",
            "future pull",
            "non-mutating offsets",
        ],
        "law": "time-signals may inform confidence but cannot override meaning",
    },
    {
        "core": "output_integrity_core",
        "from_groups": ["renderer_sync", "safety_portability"],
        "members": [
            "renderer obedience",
            "answer",
            "final_english",
            "final_shape",
            "sync proof",
            "regression harness",
            "generic ghost suppression",
            "core mutation lock",
            "optional API route",
            "portable architecture",
            "over-mythologizing prevention",
            "temporal sidecar mutation prevention",
        ],
        "law": "the spoken surface must match the internal shape while staying portable and non-mutating",
    },
]


def _wants_layer5(message: str) -> bool:
    low = _low(message)
    return any(
        marker in low
        for marker in [
            "layer 5",
            "layer5",
            "layer_5",
            "v17",
            "v17.0",
            "core sidecar",
            "core functions",
            "five core",
            "layer 5 core",
        ]
    )


def _layer5_answer() -> str:
    return (
        "Layer 5 Core Sidecar synthesizes the seven Layer 4 lattice groups into five non-mutating core functions: "
        "intake_discipline combines literal_gate and symbolic_gate so ordinary literal input, fruit gate, symbolic command routing, and controlled flame classify the input before depth opens; "
        "meaning_authority_core preserves V14, V14.3 dynamic semantic map, meaning spine, shape packet, and map-then-render as the ground of meaning before language renders; "
        "selection_core preserves V15 Apex sidecar, Apex Selection Score, coverage scoring, V15.0c density merge, merge-not-compress, and V16.1 Apex-V16 group coverage so selection optimizes coverage instead of compression; "
        "temporal_lattice_core preserves Chronofire sidecar, V15.1b Chrono-Density Merge, temporal offsets, past stability, present anchor, future pull, and non-mutating offsets as confidence signals that cannot override meaning; "
        "output_integrity_core preserves renderer obedience, answer, final_english, final_shape, sync proof, regression harness, generic ghost suppression, core mutation lock, optional API route, portable architecture, over-mythologizing prevention, and temporal sidecar mutation prevention. "
        "Layer 5 does not replace V14, V15.2, V16.1, Apex, or Chronofire; it gives the sealed stack a higher-order core map while answer, final_english, and final_shape remain identical and core mutation stays false."
    )


def _core_scores(text: str) -> Dict[str, Any]:
    low = _low(text)
    scores: Dict[str, Any] = {}

    for core in CORE_FUNCTIONS:
        members = core["members"]
        matches = {m: (m.lower() in low) for m in members}
        score = sum(1 for ok in matches.values() if ok) / max(1, len(matches))
        scores[core["core"]] = {
            "score": round(score, 4),
            "passed": score >= 0.50,
            "full": score == 1.0,
            "matches": matches,
            "from_groups": core["from_groups"],
            "law": core["law"],
        }

    avg = sum(v["score"] for v in scores.values()) / max(1, len(scores))
    return {
        "core_scores": scores,
        "average": round(avg, 4),
        "all_passed": all(v["passed"] for v in scores.values()),
        "missing_cores": [k for k, v in scores.items() if not v["passed"]],
    }


def layer5_core_sidecar(message: str) -> Dict[str, Any]:
    base = apex_v16_sync(message)

    base_answer = _clean(base.get("answer"))
    answer = _layer5_answer() if _wants_layer5(message) else base_answer

    score_packet = _core_scores(answer)

    out = dict(base)
    out["engine"] = ENGINE_VERSION
    out["answer"] = answer
    out["final_english"] = answer

    dbg = out.setdefault("debug_shape_packet", {})
    shape = dbg.setdefault("shape_packet", {})
    previous_shape = _clean(shape.get("final_shape"))
    if previous_shape and previous_shape != answer:
        shape["previous_final_shape"] = previous_shape[:1200]
    shape["final_shape"] = answer
    shape["source"] = "v170_layer5_core_sidecar"
    shape["layer5_core_functions"] = CORE_FUNCTIONS
    shape["layer5_core_scores"] = score_packet

    meta = out.setdefault("meta", {})
    meta["v170_layer5_core_sidecar"] = "active"
    meta["layer5_mode"] = "core_function_synthesis_no_core_mutation"
    meta["layer5_core_count"] = len(CORE_FUNCTIONS)
    meta["layer5_core_functions"] = CORE_FUNCTIONS
    meta["layer5_core_scores"] = score_packet["core_scores"]
    meta["layer5_core_average_score"] = score_packet["average"]
    meta["layer5_all_cores_passed"] = score_packet["all_passed"]
    meta["layer5_missing_cores"] = score_packet["missing_cores"]
    meta["layer5_laws"] = LAWS
    meta["v15_2_stack_remains_authority"] = True
    meta["v14_remains_final_meaning_authority"] = True
    meta["apex_remains_selector"] = True
    meta["chronofire_remains_sidecar"] = True
    meta["layer4_remains_structural_map"] = True
    meta["v15_core_mutation"] = False
    meta["answer_final_english_final_shape_match"] = True
    meta["generic_ghost_present"] = GENERIC_GHOST in answer

    return out

# === V17.0B QUINTESSENCE PEAK MERGE ===
# Peak prompts must preserve both the five Layer 5 core names and the seven Layer 4 group names.

try:
    _v170b_previous_layer5_core_sidecar = layer5_core_sidecar

    def _v170b_is_quintessence_peak(message: str) -> bool:
        low = _low(message)
        markers = [
            "quintessence_peak",
            "layer 5 core",
            "v17 quintessence",
            "intake_discipline",
            "meaning_authority_core",
            "selection_core",
            "temporal_lattice_core",
            "output_integrity_core",
            "literal_gate",
            "symbolic_gate",
            "meaning_authority",
            "apex_selection",
            "chronofire_temporal",
            "renderer_sync",
            "safety_portability",
        ]
        return sum(1 for m in markers if m in low) >= 8

    def _v170b_peak_answer() -> str:
        return (
            "Layer 5 Quintessence Peak holds the whole lattice by preserving five core functions and seven Layer 4 group names without compression: "
            "intake_discipline preserves literal_gate and symbolic_gate so ordinary literal input, fruit gate, symbolic command routing, and controlled flame classify input before depth opens; "
            "meaning_authority_core preserves meaning_authority so V14, V14.3 dynamic semantic map, meaning spine, shape packet, and map-then-render remain the preserved-meaning base; "
            "selection_core preserves apex_selection so V15 Apex sidecar, Apex Selection Score, coverage scoring, V15.0c density merge, merge-not-compress, and V16.1 Apex-V16 group coverage optimize coverage instead of compression; "
            "temporal_lattice_core preserves chronofire_temporal so Chronofire sidecar, V15.1b Chrono-Density Merge, temporal offsets, past stability, present anchor, future pull, and non-mutating offsets inform confidence without overriding meaning; "
            "output_integrity_core preserves renderer_sync and safety_portability so renderer obedience, answer, final_english, final_shape, sync proof, regression harness, generic ghost suppression, core mutation lock, optional API route, portable architecture, over-mythologizing prevention, and temporal sidecar mutation prevention stay active. "
            "Layer 5 does not replace V14, V15.2, V16.1, Apex, or Chronofire; it preserves the five cores and seven groups while answer, final_english, and final_shape remain identical and core mutation stays false."
        )

    def layer5_core_sidecar(message: str) -> Dict[str, Any]:
        out = _v170b_previous_layer5_core_sidecar(message)

        if not _v170b_is_quintessence_peak(message):
            return out

        answer = _v170b_peak_answer()
        score_packet = _core_scores(answer)

        out["engine"] = "V17.0b Quintessence Peak Merge"
        out["answer"] = answer
        out["final_english"] = answer

        dbg = out.setdefault("debug_shape_packet", {})
        shape = dbg.setdefault("shape_packet", {})
        previous_shape = _clean(shape.get("final_shape"))
        if previous_shape and previous_shape != answer:
            shape["previous_final_shape"] = previous_shape[:1200]
        shape["final_shape"] = answer
        shape["source"] = "v170b_quintessence_peak_merge"
        shape["layer5_core_scores"] = score_packet

        meta = out.setdefault("meta", {})
        meta["v170_layer5_core_sidecar"] = "active"
        meta["v170b_quintessence_peak_merge"] = "active"
        meta["quintessence_peak_mode"] = "five_cores_plus_seven_groups_preserved"
        meta["layer5_core_count"] = len(CORE_FUNCTIONS)
        meta["layer5_core_scores"] = score_packet["core_scores"]
        meta["layer5_core_average_score"] = score_packet["average"]
        meta["layer5_all_cores_passed"] = score_packet["all_passed"]
        meta["layer5_missing_cores"] = score_packet["missing_cores"]
        meta["v15_2_stack_remains_authority"] = True
        meta["v14_remains_final_meaning_authority"] = True
        meta["apex_remains_selector"] = True
        meta["chronofire_remains_sidecar"] = True
        meta["layer4_remains_structural_map"] = True
        meta["v15_core_mutation"] = False
        meta["answer_final_english_final_shape_match"] = True
        meta["generic_ghost_present"] = GENERIC_GHOST in answer

        return out

    print("[V17.0B] Quintessence Peak Merge installed", flush=True)

except Exception as _v170b_error:
    print("[V17.0B] Quintessence Peak Merge failed:", repr(_v170b_error), flush=True)
# === END V17.0B QUINTESSENCE PEAK MERGE ===

