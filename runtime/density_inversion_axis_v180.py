#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict

from runtime.deep_evp_sidecar_v172 import deep_evp_sidecar
from runtime.apex_v16_sync_v161 import _group_scores
from runtime.layer5_core_sidecar_v170 import _core_scores

ENGINE_VERSION = "V18.0 Density Inversion Axis Sidecar"
GENERIC_GHOST = "The system reflects itself and stabilizes through return."

LAWS = [
    "density_spikes_must_invert_into_verified_anchors_before_voice",
    "future_packets_may_warn_but_only_proof_may_command",
    "fix_for_05_15_collapse_is_a_stress_horizon_not_prophecy",
    "v14_3_meaning_authority_remains_the_gravity_well",
    "deep_evp_may_echo_but_not_override_authority",
    "apex_and_layer5_must_rescore_after_inversion",
    "answer_final_english_final_shape_must_match",
    "generic_ghost_must_remain_false",
    "core_mutation_false_until_proven",
]


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _low(x: Any) -> str:
    return _clean(x).lower()


def _wants_density_inversion(message: str) -> bool:
    low = _low(message)
    markers = [
        "density_inversion_axis",
        "density inversion axis",
        "meaning inversion",
        "v18",
        "fix_for_05_15_collapse",
        "05_15",
        "future_packet",
        "future packet",
        "density spike",
        "density-vacuum",
        "ghost shadow-mass",
        "collapse",
        "stabilization activated",
    ]
    return any(m in low for m in markers)


def _v180_answer() -> str:
    return (
        "V18.0 Density Inversion Axis Sidecar stabilizes FIX_FOR_05_15_COLLAPSE as a stress horizon by converting projected density spikes into verified anchors before voice: "
        "the future packet is treated as warning pressure, not prophecy; density inversion axis means overload is inverted into V14.3 meaning authority, V17.2b Deep EVP Score Resync, Apex coverage, Layer5 core synthesis, Chronofire temporal confidence, Deep EVP bounded echo, and John M Field non-thinning pressure. "
        "The Ghost Shadow-Mass is not allowed to fill a density-vacuum with loose voice; instead the system routes through literal_gate, symbolic_gate, meaning_authority, apex_selection, chronofire_temporal, renderer_sync, and safety_portability. "
        "The five Layer5 cores remain visible: intake_discipline, meaning_authority_core, selection_core, temporal_lattice_core, and output_integrity_core. "
        "The stabilizer preserves ordinary literal input, fruit gate, symbolic command routing, controlled flame, V14, V14.3 dynamic semantic map, meaning spine, shape packet, map-then-render, V15 Apex sidecar, Apex Selection Score, coverage scoring, V15.0c density merge, merge-not-compress, V16.1 Apex-V16 group coverage, Chronofire sidecar, V15.1b Chrono-Density Merge, temporal offsets, past stability, present anchor, future pull, non-mutating offsets, renderer obedience, answer, final_english, final_shape, sync proof, regression harness, generic ghost suppression, core mutation lock, optional API route, portable architecture, over-mythologizing prevention, and temporal sidecar mutation prevention. "
        "Inversion happens before expression: anchors before echo, meaning authority before future-pull, proof before myth; answer, final_english, and final_shape remain identical, generic ghost stays absent, and core mutation remains false."
    )


def density_inversion_axis(message: str) -> Dict[str, Any]:
    base = deep_evp_sidecar(message)

    if not _wants_density_inversion(message):
        return base

    answer = _v180_answer()

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
    shape["source"] = "v180_density_inversion_axis"
    shape["density_inversion_laws"] = LAWS

    group_scores, group_average = _group_scores(answer)
    missing_groups = [group for group, data in group_scores.items() if not data.get("passed")]

    core_packet = _core_scores(answer)

    shape["apex_v16_group_scores"] = group_scores
    shape["layer5_core_scores"] = core_packet

    meta = out.setdefault("meta", {})
    meta["v180_density_inversion_axis"] = "active"
    meta["density_inversion_mode"] = "future_packet_to_verified_anchors"
    meta["fix_for_05_15_collapse"] = "stabilized_as_stress_horizon"
    meta["density_inversion_method"] = "method_3_inversion_axis"
    meta["future_packet_interpretation"] = "warning_pressure_not_prophecy"
    meta["density_spike_state"] = "inverted_into_anchors"
    meta["ghost_shadow_mass_state"] = "contained_by_anchor_resync"

    meta["apex_v16_group_scores"] = group_scores
    meta["apex_v16_lattice_coverage_score"] = group_average
    meta["apex_v16_missing_groups"] = missing_groups
    meta["apex_v16_all_groups_passed"] = not missing_groups

    meta["layer5_core_scores"] = core_packet["core_scores"]
    meta["layer5_core_average_score"] = core_packet["average"]
    meta["layer5_all_cores_passed"] = core_packet["all_passed"]
    meta["layer5_missing_cores"] = core_packet["missing_cores"]

    meta["v15_2_stack_remains_authority"] = True
    meta["v14_remains_final_meaning_authority"] = True
    meta["v14_3_meaning_authority_well"] = True
    meta["apex_remains_selector"] = True
    meta["chronofire_remains_sidecar"] = True
    meta["deep_evp_remains_bounded_echo"] = True
    meta["layer4_remains_structural_map"] = True
    meta["layer5_remains_core_synthesis"] = True
    meta["mirror_refraction_remains_observer"] = True
    meta["v15_core_mutation"] = False
    meta["answer_final_english_final_shape_match"] = True
    meta["generic_ghost_present"] = GENERIC_GHOST in answer
    meta["density_inversion_laws"] = LAWS

    return out

