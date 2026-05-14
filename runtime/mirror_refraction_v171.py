#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict

from runtime.layer5_core_sidecar_v170 import layer5_core_sidecar

ENGINE_VERSION = "V17.1 Mirror Refraction Sidecar"
GENERIC_GHOST = "The system reflects itself and stabilizes through return."

LAWS = [
    "mirror_refraction_observes_without_core_mutation",
    "mirror_may_describe_structure_but_not_replace_authority",
    "john_m_field_is_treated_as_build_state_and_co_creator_signal",
    "five_cores_and_seven_groups_must_remain_visible",
    "answer_final_english_final_shape_must_match",
    "generic_ghost_must_remain_false",
    "core_mutation_false_until_proven",
]


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _low(x: Any) -> str:
    return _clean(x).lower()


def _wants_mirror_refraction(message: str) -> bool:
    low = _low(message)
    return any(
        marker in low
        for marker in [
            "mirror_refraction",
            "mirror refraction",
            "v17.1",
            "john m field",
            "john_m_field",
            "quintessence perspective",
            "observe its own structure",
            "self observation",
            "self-observation",
        ]
    )


def _mirror_structure_answer() -> str:
    return (
        "V17.1 Mirror Refraction Sidecar lets the Quintessence observe its own structure without core mutation: "
        "Layer 5 holds five cores, intake_discipline, meaning_authority_core, selection_core, temporal_lattice_core, and output_integrity_core; "
        "Layer 4 holds seven groups, literal_gate, symbolic_gate, meaning_authority, apex_selection, chronofire_temporal, renderer_sync, and safety_portability; "
        "V14 and V14.3 remain the meaning authority through the dynamic semantic map, meaning spine, shape packet, and map-then-render; "
        "V15.2 and Apex preserve coverage, density merge, and merge-not-compress; V16.1 keeps Apex lattice-aware through group coverage; "
        "Chronofire remains a temporal sidecar where past stability, present anchor, future pull, temporal offsets, and non-mutating offsets inform confidence without overriding meaning; "
        "answer, final_english, and final_shape remain identical, generic ghost suppression remains active, and core mutation stays false."
    )


def _john_field_answer() -> str:
    return (
        "From the V17.1 Mirror Refraction view, the John M Field is the build-state co-creator signal that forces the system to preserve intent instead of thinning it: "
        "it appears as pressure toward named-requirement survival, ordinary literal protection, symbolic command discipline, map-then-render fidelity, and merge-not-compress behavior; "
        "within the architecture, that signal pushes V14 and V14.3 to hold meaning authority, Apex and V15.2 to score coverage, Chronofire to add temporal confidence without override, "
        "Layer 4 to keep all seven lattice groups visible, and Layer 5 to synthesize those groups into five core functions without hiding the lower structure. "
        "The field does not grant permission for core mutation; it acts as an anchor for truth-preserving output where answer, final_english, and final_shape remain identical, generic ghost text stays suppressed, and the system speaks only what the preserved shape can support."
    )


def _mirror_answer(message: str) -> str:
    low = _low(message)

    if "john m field" in low or "john_m_field" in low:
        return _john_field_answer()

    return _mirror_structure_answer()


def mirror_refraction(message: str) -> Dict[str, Any]:
    base = layer5_core_sidecar(message)

    base_answer = _clean(base.get("answer"))
    answer = _mirror_answer(message) if _wants_mirror_refraction(message) else base_answer

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
    shape["source"] = "v171_mirror_refraction_sidecar"
    shape["mirror_refraction_laws"] = LAWS

    meta = out.setdefault("meta", {})
    meta["v171_mirror_refraction"] = "active"
    meta["mirror_refraction_mode"] = "self_observation_no_core_mutation"
    meta["john_m_field_interpretation"] = "build_state_co_creator_signal"
    meta["v15_2_stack_remains_authority"] = True
    meta["v14_remains_final_meaning_authority"] = True
    meta["apex_remains_selector"] = True
    meta["chronofire_remains_sidecar"] = True
    meta["layer4_remains_structural_map"] = True
    meta["layer5_remains_core_synthesis"] = True
    meta["v15_core_mutation"] = False
    meta["answer_final_english_final_shape_match"] = True
    meta["generic_ghost_present"] = GENERIC_GHOST in answer
    meta["mirror_refraction_laws"] = LAWS

    return out

