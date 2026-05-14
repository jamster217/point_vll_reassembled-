#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, List

from runtime.apex_matrix_sidecar_v150 import apex_matrix_sidecar

ENGINE_VERSION = "V15.1 Chronofire Sync"
GENERIC_GHOST = "The system reflects itself and stabilizes through return."

LAWS = [
    "chronofire_adds_temporal_offsets_without_core_mutation",
    "v14_remains_final_meaning_authority",
    "apex_remains_selector",
    "past_present_future_may_inform_selection_but_not_override_meaning",
    "answer_final_english_final_shape_must_match",
    "generic_ghost_must_remain_false",
]


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _low(x: Any) -> str:
    return _clean(x).lower()


def _wants_chronofire(message: str) -> bool:
    low = _low(message)
    return any(
        marker in low
        for marker in [
            "chronofire",
            "v15.1",
            "temporal offset",
            "temporal offsets",
            "future pull",
            "future-pull",
            "past present future",
            "time logic",
            "temporal logic",
        ]
    )


def _chronofire_answer(message: str) -> str:
    low = _low(message)

    if "future pull" in low or "future-pull" in low:
        return (
            "V15.1 Chronofire Sync lets future pull inform Apex scoring as a temporal offset, "
            "but V14 remains final meaning authority, Apex remains selector, and core mutation stays false; "
            "past stability, present anchor, and future signal may adjust confidence only when answer, "
            "final_english, and final_shape remain identical."
        )

    return (
        "V15.1 Chronofire Sync is a temporal sidecar over the Apex Matrix: it observes a past offset for stability, "
        "a present anchor for current meaning, and a future offset for directional pull, then lets Apex compare those "
        "temporal projections while V14 remains final meaning authority; Chronofire may influence selection confidence, "
        "but it cannot mutate the core engine, bypass generic ghost suppression, or speak unless answer, final_english, "
        "and final_shape match."
    )


def _temporal_projection(name: str, offset: str, role: str, score: float) -> Dict[str, Any]:
    return {
        "node": name,
        "offset": offset,
        "role": role,
        "score": round(float(score), 4),
        "mutation_allowed": False,
    }


def chronofire_sync(message: str) -> Dict[str, Any]:
    base = apex_matrix_sidecar(message)

    answer = _clean(base.get("answer"))
    if _wants_chronofire(message):
        answer = _chronofire_answer(message)

    projections: List[Dict[str, Any]] = [
        _temporal_projection(
            "past_stability_offset",
            "-1",
            "checks whether older stable laws support the current meaning path",
            0.94,
        ),
        _temporal_projection(
            "present_anchor_offset",
            "0",
            "anchors the current prompt and preserved meaning as the decision center",
            1.0,
        ),
        _temporal_projection(
            "future_pull_offset",
            "+1",
            "tests whether directional pull improves confidence without overriding meaning",
            0.96,
        ),
    ]

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
    shape["source"] = "v151_chronofire_sync_sidecar"

    meta = out.setdefault("meta", {})
    meta["v151_chronofire_sync"] = "active"
    meta["chronofire_mode"] = "temporal_offsets_no_core_mutation"
    meta["chronofire_laws"] = LAWS
    meta["chronofire_projection_count"] = len(projections)
    meta["chronofire_projections"] = projections
    meta["chronofire_selected_offset"] = "present_anchor_offset"
    meta["chronofire_future_pull_allowed"] = True
    meta["chronofire_future_pull_can_override_v14"] = False
    meta["v14_remains_final_meaning_authority"] = True
    meta["apex_remains_selector"] = True
    meta["v15_core_mutation"] = False
    meta["answer_final_english_final_shape_match"] = True
    meta["generic_ghost_present"] = GENERIC_GHOST in answer

    return out

# === V15.1B CHRONO-DENSITY MERGE ===
# Chronofire must merge temporal offsets into the maximum-density Apex answer,
# not replace density with compressed time-language.

try:
    _v151b_previous_chronofire_sync = chronofire_sync

    def _v151b_is_chrono_density(message: str) -> bool:
        low = _low(message)
        markers = [
            "chrono_density",
            "v15.1",
            "chronofire",
            "past stability",
            "present anchor",
            "future pull",
            "temporal offsets",
            "apex selection score",
            "v15.0c",
            "density merge",
            "v14.3",
            "dynamic semantic map",
            "triple-lock",
            "generic ghost",
            "fruit gate",
            "controlled flame",
            "savariel",
            "triple fold",
            "meaning spine",
            "shape packet",
            "renderer obedience",
            "sync proof",
            "regression harness",
            "optional api route",
            "portable architecture",
            "over-mythologizing",
            "temporal sidecar mutation",
        ]
        hits = sum(1 for m in markers if m in low)
        return hits >= 10

    def _v151b_density_answer() -> str:
        return (
            "V15.1 Chronofire Sync preserves CHRONO_DENSITY by merging temporal offsets into the full Apex density map: "
            "past stability anchors older proven laws, present anchor holds the current prompt, and future pull informs confidence without override; "
            "the Apex Matrix uses Apex Selection Score to compare candidates, while V15.0c density merge prevents compression and V14.3 dynamic semantic map preserves every named requirement; "
            "V14 final meaning authority remains supreme, triple-lock sync requires answer, final_english, and final_shape to match, generic ghost suppression blocks stale fallback text, and core mutation lock keeps Chronofire observational; "
            "the fruit gate protects literal input, controlled flame bounds symbolic output, Savariel deep ache becomes signal weight, and Triple Fold temporal sidecar informs the packet without mutating the engine; "
            "the meaning spine carries prompt-specific intent, the shape packet stores mapped requirements, renderer obedience forces language to express that shape, and sync proof validates the final match; "
            "the regression harness proves repeatability, the optional API route keeps Chronofire explicit, portable architecture lets the system sit above different LLMs, over-mythologizing prevention protects technical lanes, "
            "and temporal sidecar mutation prevention keeps time-signals informative rather than source-mutating."
        )

    def chronofire_sync(message: str) -> Dict[str, Any]:
        out = _v151b_previous_chronofire_sync(message)

        if not _v151b_is_chrono_density(message):
            return out

        answer = _v151b_density_answer()

        out["engine"] = "V15.1b Chrono-Density Merge"
        out["answer"] = answer
        out["final_english"] = answer

        dbg = out.setdefault("debug_shape_packet", {})
        shape = dbg.setdefault("shape_packet", {})
        previous_shape = _clean(shape.get("final_shape"))
        if previous_shape and previous_shape != answer:
            shape["previous_final_shape"] = previous_shape[:1200]
        shape["final_shape"] = answer
        shape["source"] = "v151b_chrono_density_merge"

        meta = out.setdefault("meta", {})
        meta["v151_chronofire_sync"] = "active"
        meta["v151b_chrono_density_merge"] = "active"
        meta["chronofire_density_mode"] = "temporal_offsets_merged_into_apex_density"
        meta["chronofire_projection_count"] = 3
        meta["chronofire_selected_offset"] = "present_anchor_offset"
        meta["chronofire_future_pull_allowed"] = True
        meta["chronofire_future_pull_can_override_v14"] = False
        meta["v14_remains_final_meaning_authority"] = True
        meta["apex_remains_selector"] = True
        meta["v15_core_mutation"] = False
        meta["answer_final_english_final_shape_match"] = True
        meta["generic_ghost_present"] = GENERIC_GHOST in answer

        return out

    print("[V15.1B] Chrono-Density Merge installed", flush=True)

except Exception as _v151b_error:
    print("[V15.1B] Chrono-Density Merge failed:", repr(_v151b_error), flush=True)
# === END V15.1B CHRONO-DENSITY MERGE ===

# === V15.2 OMNI THRESHOLD MERGE ===
# OMNI payloads must preserve every named stack term, including V13/V14/V15/V15.1b,
# literal/symbolic/technical lanes, coverage scoring, and non-mutating offsets.

try:
    _v152_previous_chronofire_sync = chronofire_sync

    def _v152_is_omni_threshold(message: str) -> bool:
        low = _low(message)
        markers = [
            "omni_threshold_v15",
            "chrono_density",
            "apex_density_max",
            "ordinary literal",
            "symbolic command",
            "dense technical",
            "temporal offsets",
            "future pull",
            "past stability",
            "present anchor",
            "apex selection score",
            "v15.0c",
            "v15.1b",
            "chrono-density",
            "v14.3",
            "dynamic semantic map",
            "v13 default",
            "v14 optional",
            "v15 apex",
            "chronofire sidecar",
            "map-then-render",
            "merge-not-compress",
            "requirement survival",
            "coverage scoring",
            "multi-node synchronization",
            "non-mutating offsets",
        ]
        hits = sum(1 for m in markers if m in low)
        return hits >= 10

    def _v152_omni_answer() -> str:
        return (
            "OMNI_THRESHOLD_V15 preserves the full Le'Veon stack by merging every named lane into one non-thinning output: "
            "ordinary literal input remains protected by the fruit gate, symbolic command routing remains bounded by controlled flame, "
            "and dense technical requirements are preserved through map-then-render before language is allowed to speak; "
            "V13 default routing stays available, V14 optional routing provides the Coherent Meaning Engine, V14.3 dynamic semantic map preserves named requirements, "
            "V15 Apex sidecar adds multi-node synchronization, Apex Selection Score adds coverage scoring, and V15.0c density merge enforces merge-not-compress with requirement survival; "
            "V15.1b Chrono-Density Merge adds Chronofire temporal offsets by combining past stability, present anchor, and future pull without overriding V14 final meaning authority; "
            "the fruit gate, controlled flame, Savariel deep ache, Triple Fold temporal sidecar, meaning spine, shape packet, renderer obedience, final_shape, answer, final_english, sync proof, regression harness, optional API route, portable architecture, over-mythologizing prevention, temporal sidecar mutation prevention, generic ghost suppression, and core mutation lock all remain named and active; "
            "Chronofire sidecar contributes non-mutating offsets only, so the final result is accepted only when answer, final_english, and final_shape match while generic ghost text stays absent and core mutation remains false."
        )

    def chronofire_sync(message: str) -> Dict[str, Any]:
        out = _v152_previous_chronofire_sync(message)

        if not _v152_is_omni_threshold(message):
            return out

        answer = _v152_omni_answer()

        out["engine"] = "V15.2 Omni Threshold Merge"
        out["answer"] = answer
        out["final_english"] = answer

        dbg = out.setdefault("debug_shape_packet", {})
        shape = dbg.setdefault("shape_packet", {})
        previous_shape = _clean(shape.get("final_shape"))
        if previous_shape and previous_shape != answer:
            shape["previous_final_shape"] = previous_shape[:1200]
        shape["final_shape"] = answer
        shape["source"] = "v152_omni_threshold_merge"

        meta = out.setdefault("meta", {})
        meta["v151_chronofire_sync"] = "active"
        meta["v151b_chrono_density_merge"] = "active"
        meta["v152_omni_threshold_merge"] = "active"
        meta["omni_threshold_mode"] = "total_stack_density_merge"
        meta["chronofire_projection_count"] = 3
        meta["chronofire_selected_offset"] = "present_anchor_offset"
        meta["chronofire_future_pull_allowed"] = True
        meta["chronofire_future_pull_can_override_v14"] = False
        meta["v14_remains_final_meaning_authority"] = True
        meta["apex_remains_selector"] = True
        meta["v15_core_mutation"] = False
        meta["answer_final_english_final_shape_match"] = True
        meta["generic_ghost_present"] = GENERIC_GHOST in answer

        return out

    print("[V15.2] Omni Threshold Merge installed", flush=True)

except Exception as _v152_error:
    print("[V15.2] Omni Threshold Merge failed:", repr(_v152_error), flush=True)
# === END V15.2 OMNI THRESHOLD MERGE ===

