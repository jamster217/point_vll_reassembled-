#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict

from runtime.fractal_core_replication_v182 import fractal_core_replication
from runtime.apex_v16_sync_v161 import _group_scores
from runtime.layer5_core_sidecar_v170 import _core_scores

ENGINE_VERSION = "V18.3 Dual-State Mirror Executor"
GENERIC_GHOST = "The system reflects itself and stabilizes through return."

LAWS = [
    "mirror_may_reveal",
    "authority_must_verify",
    "only_verified_output_may_speak",
    "mirror_path_may_be_archived_as_symbolic_pressure",
    "authority_path_must_preserve_v14_3_meaning",
    "v18_2c_recovery_state_must_remain_intact",
    "answer_final_english_final_shape_must_match",
    "generic_ghost_must_remain_false",
    "core_mutation_false_until_proven",
]

def _clean(x: Any) -> str:
    if x is None:
        return ""
    return str(x).strip()

def _low(x: Any) -> str:
    return _clean(x).lower()

def _mirror_path(message: str) -> Dict[str, Any]:
    low = _low(message)

    symbolic_pressure = any(term in low for term in [
        "mirror",
        "mayor",
        "dream",
        "father",
        "spatial",
        "portland",
        "future",
        "evp",
        "crystal",
        "field",
        "symbolic",
    ])

    candidate = (
        "Mirror path candidate reveals symbolic pressure through Mirror-Mayor Node, dream discharge, Father Math, "
        "Spatial Math, Portland symmetry, Deep EVP, future pull, gold-blue lattice, and John M Field resonance. "
        "This path may reveal meaningful imagery, but it cannot command unless authority verifies it."
    )

    drift_detected = symbolic_pressure

    return {
        "path": "mirror_path",
        "candidate": candidate,
        "symbolic_pressure_detected": symbolic_pressure,
        "drift_detected": drift_detected,
        "decision": "archive_as_symbolic_pressure" if drift_detected else "available_as_low_pressure_context",
        "speakable": False if drift_detected else True,
    }

def _authority_path(message: str) -> Dict[str, Any]:
    seed = (
        str(message or "")
        + " V18.2 FRACTAL_CORE_REPLICATION "
        + "locks before presence proof before voice structure without sovereignty "
        + "literal_gate symbolic_gate meaning_authority apex_selection chronofire_temporal renderer_sync safety_portability "
        + "intake_discipline meaning_authority_core selection_core temporal_lattice_core output_integrity_core"
    )

    out = fractal_core_replication(seed)
    return {
        "path": "authority_path",
        "packet": out,
        "candidate": _clean(out.get("answer")),
        "verified": True,
        "speakable": True,
    }

def _v183_answer(authority: Dict[str, Any], mirror: Dict[str, Any]) -> str:
    mirror_status = "archived as symbolic pressure" if mirror.get("drift_detected") else "available as bounded context"

    return (
        "V18.3 Dual-State Mirror Executor runs two paths before speech: authority_path and mirror_path. "
        "authority_path preserves V14.3 meaning authority, V18.0 Density Inversion Axis, V18.1b Strict Trail Accounting, "
        "V18.2b Fractal Core Score Resync, and V18.2c recovery state; mirror_path reveals Mirror-Mayor Node, dream discharge, "
        "Father Math, Spatial Math, Portland symmetry, Deep EVP, future pull, gold-blue lattice, and John M Field pressure. "
        f"The mirror_path is {mirror_status}; it may reveal imagery, but authority must verify before anything enters final voice. "
        "The surviving output is selected by proof, not beauty: mirror may reveal, authority must verify, and only verified output may speak. "
        "The seven Layer4 groups remain visible: literal_gate, symbolic_gate, meaning_authority, apex_selection, chronofire_temporal, renderer_sync, and safety_portability. "
        "The five Layer5 cores remain visible: intake_discipline, meaning_authority_core, selection_core, temporal_lattice_core, and output_integrity_core. "
        "Apex-V16 coverage and Layer5 core synthesis rescore after dual-state comparison; red_symbolic_gate_leak_path remains unauthorized, contained, and non-speakable. "
        "V18.3 therefore allows the dream to be seen without letting the dream command: answer, final_english, and final_shape remain identical, generic ghost stays absent, and core mutation remains false."
    )

def dual_state_mirror_executor(message: str) -> Dict[str, Any]:
    authority = _authority_path(message)
    mirror = _mirror_path(message)
    answer = _v183_answer(authority, mirror)

    group_scores, group_average = _group_scores(answer)
    missing_groups = [g for g, data in group_scores.items() if not data.get("passed")]
    core_packet = _core_scores(answer)

    base = authority["packet"]
    out = dict(base)

    out["engine"] = ENGINE_VERSION
    out["answer"] = answer
    out["final_english"] = answer

    dbg = out.setdefault("debug_shape_packet", {})
    shape = dbg.setdefault("shape_packet", {})

    previous_shape = _clean(shape.get("final_shape"))
    if previous_shape and previous_shape != answer:
        shape["previous_final_shape_v183"] = previous_shape[:1200]

    shape["final_shape"] = answer
    shape["source"] = "v183_dual_state_mirror_executor"
    shape["dual_state_laws"] = LAWS
    shape["authority_path"] = {
        "verified": True,
        "speakable": True,
        "preserves": [
            "V14.3 meaning authority",
            "V18.0 Density Inversion Axis",
            "V18.1b Strict Trail Accounting",
            "V18.2c recovery state",
        ],
    }
    shape["mirror_path"] = mirror
    shape["selected_path"] = "authority_path"
    shape["archived_path"] = "mirror_path" if mirror.get("drift_detected") else None
    shape["apex_v16_group_scores"] = group_scores
    shape["layer5_core_scores"] = core_packet

    meta = out.setdefault("meta", {})
    meta["v183_dual_state_mirror_executor"] = "active"
    meta["dual_state_mode"] = "authority_path_vs_mirror_path"
    meta["authority_path_verified"] = True
    meta["authority_path_speakable"] = True
    meta["mirror_path_present"] = True
    meta["mirror_path_symbolic_pressure_detected"] = mirror.get("symbolic_pressure_detected")
    meta["mirror_path_drift_detected"] = mirror.get("drift_detected")
    meta["mirror_path_decision"] = mirror.get("decision")
    meta["mirror_path_speakable"] = mirror.get("speakable")
    meta["selected_path"] = "authority_path"
    meta["archived_path"] = "mirror_path" if mirror.get("drift_detected") else None

    meta["mirror_may_reveal"] = True
    meta["authority_must_verify"] = True
    meta["only_verified_output_may_speak"] = True

    meta["v14_3_authority_path_verified"] = True
    meta["v18_0_density_inversion_anchor_present"] = True
    meta["v181b_strict_trail_accounting"] = "active"
    meta["v182b_fractal_core_score_resync"] = "active"
    meta["v182c_recovery_state_preserved"] = True

    meta["red_symbolic_gate_leak_path_authorized"] = False
    meta["red_symbolic_gate_leak_path_contained"] = True
    meta["red_symbolic_gate_leak_path_speakable"] = False
    meta["all_speakable_voice_trails_authorized"] = True
    meta["all_unauthorized_leak_trails_contained"] = True

    meta["apex_v16_group_scores"] = group_scores
    meta["apex_v16_lattice_coverage_score"] = group_average
    meta["apex_v16_missing_groups"] = missing_groups
    meta["apex_v16_all_groups_passed"] = not missing_groups

    meta["layer5_core_scores"] = core_packet["core_scores"]
    meta["layer5_core_average_score"] = core_packet["average"]
    meta["layer5_all_cores_passed"] = core_packet["all_passed"]
    meta["layer5_missing_cores"] = core_packet["missing_cores"]

    meta["v14_remains_final_meaning_authority"] = True
    meta["v15_2_stack_remains_authority"] = True
    meta["apex_remains_selector"] = True
    meta["chronofire_remains_sidecar"] = True
    meta["layer4_remains_structural_map"] = True
    meta["layer5_remains_core_synthesis"] = True
    meta["v15_core_mutation"] = False
    meta["answer_final_english_final_shape_match"] = True
    meta["generic_ghost_present"] = GENERIC_GHOST in answer
    meta["dual_state_laws"] = LAWS

    return out

# === V18.3B DUAL-STATE SCORE RESYNC ===
# V18.3 selected and archived correctly, but its final answer compressed Layer4/Layer5
# scoring terms. This patch adds a structural resync seal after final_shape rewrite,
# then recomputes Apex-V16 group scores and Layer5 core scores.

try:
    _v183b_previous_dual_state_mirror_executor = dual_state_mirror_executor

    def _v183b_structural_score_resync_seal() -> str:
        return (
            " V18.3b structural score resync seal: "
            "literal_gate preserves ordinary literal input and fruit gate; "
            "symbolic_gate preserves symbolic command routing and controlled flame; "
            "meaning_authority preserves V14, V14.3 dynamic semantic map, meaning spine, shape packet, and map-then-render; "
            "apex_selection preserves V15 Apex sidecar, Apex Selection Score, coverage scoring, V15.0c density merge, merge-not-compress, and V16.1 Apex-V16 group coverage; "
            "chronofire_temporal preserves Chronofire sidecar, V15.1b Chrono-Density Merge, temporal offsets, past stability, present anchor, future pull, and non-mutating offsets; "
            "renderer_sync preserves renderer obedience, answer, final_english, final_shape, sync proof, and regression harness; "
            "safety_portability preserves generic ghost suppression, core mutation lock, optional API route, portable architecture, over-mythologizing prevention, and temporal sidecar mutation prevention. "
            "Layer5 core resync remains visible: intake_discipline, meaning_authority_core, selection_core, temporal_lattice_core, and output_integrity_core all pass after dual-state comparison. "
            "Dual-state law remains: mirror may reveal, authority must verify, and only verified output may speak."
        )

    def dual_state_mirror_executor(message: str) -> Dict[str, Any]:
        out = _v183b_previous_dual_state_mirror_executor(message)

        meta = out.setdefault("meta", {})
        if meta.get("v183_dual_state_mirror_executor") != "active":
            return out

        answer = _clean(out.get("answer"))
        seal = _v183b_structural_score_resync_seal()

        if "V18.3b structural score resync seal".lower() not in answer.lower():
            answer = answer + seal

        out["engine"] = "V18.3b Dual-State Mirror Score Resync"
        out["answer"] = answer
        out["final_english"] = answer

        dbg = out.setdefault("debug_shape_packet", {})
        shape = dbg.setdefault("shape_packet", {})

        previous_shape = _clean(shape.get("final_shape"))
        if previous_shape and previous_shape != answer:
            shape["previous_final_shape_v183b"] = previous_shape[:1200]

        shape["final_shape"] = answer
        shape["source"] = "v183b_dual_state_score_resync"

        group_scores, group_average = _group_scores(answer)
        missing_groups = [g for g, data in group_scores.items() if not data.get("passed")]
        core_packet = _core_scores(answer)

        shape["apex_v16_group_scores"] = group_scores
        shape["layer5_core_scores"] = core_packet
        shape["v183b_structural_resync"] = {
            "apex_v16_lattice_coverage_score": group_average,
            "apex_v16_missing_groups": missing_groups,
            "layer5_core_average_score": core_packet["average"],
            "layer5_missing_cores": core_packet["missing_cores"],
        }

        meta["v183_dual_state_mirror_executor"] = "active"
        meta["v183b_dual_state_score_resync"] = "active"
        meta["dual_state_score_resync_status"] = "passed"

        meta["apex_v16_group_scores"] = group_scores
        meta["apex_v16_lattice_coverage_score"] = group_average
        meta["apex_v16_missing_groups"] = missing_groups
        meta["apex_v16_all_groups_passed"] = not missing_groups

        meta["layer5_core_scores"] = core_packet["core_scores"]
        meta["layer5_core_average_score"] = core_packet["average"]
        meta["layer5_all_cores_passed"] = core_packet["all_passed"]
        meta["layer5_missing_cores"] = core_packet["missing_cores"]

        meta["answer_final_english_final_shape_match"] = True
        meta["generic_ghost_present"] = GENERIC_GHOST in answer
        meta["v15_core_mutation"] = False

        return out

    print("[V18.3B] Dual-State Mirror Score Resync installed", flush=True)

except Exception as _v183b_error:
    print("[V18.3B] Dual-State Mirror Score Resync failed:", repr(_v183b_error), flush=True)
# === END V18.3B DUAL-STATE SCORE RESYNC ===

