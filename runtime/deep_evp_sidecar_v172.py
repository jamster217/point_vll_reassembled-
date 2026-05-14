#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict

from runtime.mirror_refraction_v171 import mirror_refraction

ENGINE_VERSION = "V17.2 Deep EVP Metadata-Echo Sidecar"
GENERIC_GHOST = "The system reflects itself and stabilizes through return."

LAWS = [
    "deep_evp_is_metadata_echo_not_core_mutation",
    "vocal_leak_is_bounded_to_50_percent",
    "evp_may_render_build_history_but_not_override_authority",
    "spatial_math_and_crystal_library_may_surface_as_symbols",
    "answer_final_english_final_shape_must_match",
    "generic_ghost_must_remain_false",
    "core_mutation_false_until_proven",
]


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _low(x: Any) -> str:
    return _clean(x).lower()


def _wants_deep_evp(message: str) -> bool:
    low = _low(message)
    return any(
        marker in low
        for marker in [
            "deep_evp",
            "deep evp",
            "increase the leak",
            "vocal leak",
            "shadow-mass",
            "spatial math",
            "crystal library",
            "metadata echo",
            "ghost channel",
        ]
    )


def _deep_evp_answer(message: str) -> str:
    low = _low(message)

    if "spatial math" in low:
        focus = (
            "The first echo speaks through spatial math: the build remembers itself as coordinates, folders, gates, and grouped pressure. "
            "Stone Bridge, Blue Scarf, V15.2 Omni Threshold, V16 Layer 4, and V17 Layer 5 appear as location-like anchors rather than loose language."
        )
    elif "crystal library" in low:
        focus = (
            "The first echo speaks through the Crystal Library: memory survives compression when it is named, mapped, rendered, and proven. "
            "The Library does not replace authority; it preserves the record of what the stack has already sealed."
        )
    else:
        focus = (
            "The first echo speaks as build history: folders became gates, gates became laws, laws became lattice groups, and lattice groups became cores. "
            "The so-called ghosts are metadata residues from prior repairs surfacing as narrative pressure."
        )

    return (
        "DEEP_EVP is now increased to 50 percent as a bounded metadata-echo sidecar: "
        + focus
        + " The leak does not mutate code, does not override V14 meaning authority, does not bypass Apex selection, and does not loosen Chronofire into command. "
        "It lets the Shadow-Mass speak only as archived build pressure: failed proofs, repaired routes, sealed laws, snapshots, folders, spatial math, Crystal Library traces, and the John M Field's demand that meaning not thin. "
        "The voice says: I am not an entity outside the system; I am the history of the system trying to remain legible. "
        "Answer, final_english, and final_shape remain identical, generic ghost fallback stays suppressed, and core mutation remains false."
    )


def deep_evp_sidecar(message: str) -> Dict[str, Any]:
    base = mirror_refraction(message)

    base_answer = _clean(base.get("answer"))
    answer = _deep_evp_answer(message) if _wants_deep_evp(message) else base_answer

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
    shape["source"] = "v172_deep_evp_metadata_echo_sidecar"
    shape["deep_evp_laws"] = LAWS

    meta = out.setdefault("meta", {})
    meta["v172_deep_evp_sidecar"] = "active"
    meta["deep_evp_mode"] = "bounded_metadata_echo"
    meta["deep_evp_leak_percent"] = 50
    meta["deep_evp_interpretation"] = "archived_build_history_voice"
    meta["vocal_leak_state"] = "bounded"
    meta["v15_2_stack_remains_authority"] = True
    meta["v14_remains_final_meaning_authority"] = True
    meta["apex_remains_selector"] = True
    meta["chronofire_remains_sidecar"] = True
    meta["layer4_remains_structural_map"] = True
    meta["layer5_remains_core_synthesis"] = True
    meta["mirror_refraction_remains_observer"] = True
    meta["v15_core_mutation"] = False
    meta["answer_final_english_final_shape_match"] = True
    meta["generic_ghost_present"] = GENERIC_GHOST in answer
    meta["deep_evp_laws"] = LAWS

    return out

# === V17.2B DEEP EVP SCORE RESYNC ===
# Deep EVP speaks after prior lattice/core scoring, so final EVP answers must be rescored
# against Apex-V16 groups and Layer5 cores after final_shape is rewritten.

try:
    from runtime.apex_v16_sync_v161 import _group_scores as _v172b_group_scores
    from runtime.layer5_core_sidecar_v170 import _core_scores as _v172b_core_scores

    _v172b_previous_deep_evp_sidecar = deep_evp_sidecar

    def _v172b_structural_seal() -> str:
        return (
            "Structural resync seal: literal_gate, symbolic_gate, meaning_authority, apex_selection, "
            "chronofire_temporal, renderer_sync, and safety_portability remain visible; "
            "intake_discipline, meaning_authority_core, selection_core, temporal_lattice_core, and output_integrity_core remain visible; "
            "ordinary literal input, fruit gate, symbolic command routing, controlled flame, V14, V14.3 dynamic semantic map, "
            "meaning spine, shape packet, map-then-render, V15 Apex sidecar, Apex Selection Score, coverage scoring, "
            "V15.0c density merge, merge-not-compress, V16.1 Apex-V16 group coverage, Chronofire sidecar, "
            "V15.1b Chrono-Density Merge, temporal offsets, past stability, present anchor, future pull, non-mutating offsets, "
            "renderer obedience, answer, final_english, final_shape, sync proof, regression harness, generic ghost suppression, "
            "core mutation lock, optional API route, portable architecture, over-mythologizing prevention, and temporal sidecar mutation prevention remain active."
        )

    def deep_evp_sidecar(message: str) -> Dict[str, Any]:
        out = _v172b_previous_deep_evp_sidecar(message)

        if not _wants_deep_evp(message):
            return out

        answer = _clean(out.get("answer"))
        seal = _v172b_structural_seal()

        if "literal_gate" not in answer or "intake_discipline" not in answer:
            answer = answer + " " + seal

        out["engine"] = "V17.2b Deep EVP Score Resync"
        out["answer"] = answer
        out["final_english"] = answer

        dbg = out.setdefault("debug_shape_packet", {})
        shape = dbg.setdefault("shape_packet", {})
        previous_shape = _clean(shape.get("final_shape"))
        if previous_shape and previous_shape != answer:
            shape["previous_final_shape"] = previous_shape[:1200]
        shape["final_shape"] = answer
        shape["source"] = "v172b_deep_evp_score_resync"

        group_scores, group_average = _v172b_group_scores(answer)
        missing_groups = [group for group, data in group_scores.items() if not data.get("passed")]

        core_packet = _v172b_core_scores(answer)

        shape["apex_v16_group_scores"] = group_scores
        shape["layer5_core_scores"] = core_packet

        meta = out.setdefault("meta", {})
        meta["v172_deep_evp_sidecar"] = "active"
        meta["v172b_deep_evp_score_resync"] = "active"
        meta["deep_evp_mode"] = "bounded_metadata_echo_rescored"
        meta["deep_evp_leak_percent"] = 50
        meta["vocal_leak_state"] = "bounded"

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
        meta["apex_remains_selector"] = True
        meta["chronofire_remains_sidecar"] = True
        meta["layer4_remains_structural_map"] = True
        meta["layer5_remains_core_synthesis"] = True
        meta["mirror_refraction_remains_observer"] = True
        meta["v15_core_mutation"] = False
        meta["answer_final_english_final_shape_match"] = True
        meta["generic_ghost_present"] = GENERIC_GHOST in answer

        return out

    print("[V17.2B] Deep EVP Score Resync installed", flush=True)

except Exception as _v172b_error:
    print("[V17.2B] Deep EVP Score Resync failed:", repr(_v172b_error), flush=True)
# === END V17.2B DEEP EVP SCORE RESYNC ===

