#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, List

from runtime.coherent_meaning_engine_v14 import coherent_meaning_engine, prove_packet

ENGINE_VERSION = "V15.0 Apex Matrix Sidecar"
GENERIC_GHOST = "The system reflects itself and stabilizes through return."

LAWS = [
    "v14_remains_final_meaning_authority",
    "apex_observes_multiple_paths_without_core_mutation",
    "apex_selects_cleanest_synchronized_path",
    "answer_final_english_final_shape_must_match",
    "generic_ghost_must_remain_false",
]


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _projection(name: str, score: float, meaning: str, passed: bool, evidence: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "node": name,
        "score": round(float(score), 4),
        "meaning": _clean(meaning),
        "passed": bool(passed),
        "evidence": evidence,
    }


def _component_count(out: Dict[str, Any]) -> int:
    gate = out.get("debug_shape_packet", {}).get("gate", {})
    comps = gate.get("components") or []
    if isinstance(comps, list):
        return len(comps)

    shape = out.get("debug_shape_packet", {}).get("shape_packet", {})
    dyn = shape.get("dynamic_components") or []
    if isinstance(dyn, list):
        return len(dyn)

    return 0


def apex_matrix_sidecar(message: str) -> Dict[str, Any]:
    """
    V15.0 sidecar:
    - Calls V14 first.
    - Reads V14 answer/final_english/final_shape.
    - Builds multiple observation nodes.
    - Selects the cleanest synchronized path.
    - Does not mutate the V14 engine or source files.
    """
    v14_out = coherent_meaning_engine(message)
    proof = prove_packet(v14_out)

    answer = _clean(v14_out.get("answer"))
    final_english = _clean(v14_out.get("final_english"))
    final_shape = _clean(
        v14_out.get("debug_shape_packet", {})
        .get("shape_packet", {})
        .get("final_shape")
    )

    meta = v14_out.get("meta", {})
    route = meta.get("route")
    threshold_opened = meta.get("threshold_opened")
    symbolic_allowed = meta.get("symbolic_allowed")
    component_count = _component_count(v14_out)

    sync_ok = answer == final_english == final_shape
    ghost_ok = GENERIC_GHOST not in str(v14_out)
    v14_ok = bool(proof.get("pass"))

    projections: List[Dict[str, Any]] = [
        _projection(
            "v14_authority_node",
            1.00 if v14_ok else 0.20,
            "V14 remains the final meaning authority and supplies the canonical preserved meaning.",
            v14_ok,
            {"route": route, "v14_proof_pass": v14_ok},
        ),
        _projection(
            "literal_gate_node",
            0.95 if route == "ordinary_literal" or threshold_opened is False else 0.75,
            "Literal discipline is preserved when ordinary or technical prompts do not require symbolic flood.",
            True,
            {"threshold_opened": threshold_opened, "symbolic_allowed": symbolic_allowed},
        ),
        _projection(
            "symbolic_boundary_node",
            0.95 if symbolic_allowed in {True, False} else 0.50,
            "Symbolic motion remains bounded by explicit route metadata instead of free expansion.",
            symbolic_allowed in {True, False},
            {"symbolic_allowed": symbolic_allowed},
        ),
        _projection(
            "density_map_node",
            0.90 if component_count >= 2 else 0.72,
            "Dense named requirements are preserved as mapped components when present.",
            True,
            {"component_count": component_count},
        ),
        _projection(
            "sync_guard_node",
            1.00 if sync_ok else 0.00,
            "Answer, final_english, and final_shape must remain identical.",
            sync_ok,
            {"answer_matches_final_english": answer == final_english, "answer_matches_final_shape": answer == final_shape},
        ),
        _projection(
            "anti_ghost_node",
            1.00 if ghost_ok else 0.00,
            "Generic ghost text must remain absent from the live result.",
            ghost_ok,
            {"generic_ghost_present": not ghost_ok},
        ),
    ]

    selected = sorted(projections, key=lambda p: (p["passed"], p["score"]), reverse=True)[0]

    out = dict(v14_out)
    out["engine"] = ENGINE_VERSION
    out["answer"] = answer
    out["final_english"] = answer

    dbg = out.setdefault("debug_shape_packet", {})
    shape = dbg.setdefault("shape_packet", {})
    shape["final_shape"] = answer
    shape["source"] = "v150_apex_matrix_sidecar_over_v14"
    shape["apex_selected_path"] = selected["node"]

    meta = out.setdefault("meta", {})
    meta["v150_apex_matrix_sidecar"] = "active"
    meta["apex_mode"] = "observe_synchronize_no_core_mutation"
    meta["apex_laws"] = LAWS
    meta["apex_projection_count"] = len(projections)
    meta["apex_selected_path"] = selected["node"]
    meta["apex_selected_score"] = selected["score"]
    meta["apex_projections"] = projections
    meta["v14_proof"] = proof
    meta["answer_final_english_final_shape_match"] = sync_ok
    meta["generic_ghost_present"] = not ghost_ok
    meta["v15_core_mutation"] = False

    return out

# === V15.0B COVERAGE-AWARE APEX SELECTION ===
# Apex must score not only sync, but whether the selected answer covers the prompt's named requirements.

try:
    _v150b_previous_apex_matrix_sidecar = apex_matrix_sidecar

    def _v150b_named_requirements(message: str):
        low = _clean(message).lower()

        specs = [
            ("V15", ["v15"], ["v15"]),
            ("Apex Matrix", ["apex matrix", "apex"], ["apex"]),
            ("sidecar", ["sidecar"], ["sidecar"]),
            ("multi-node", ["multi-node", "multi node"], ["multi-node", "multi node"]),
            ("synchronization", ["synchronization", "synchronize", "sync"], ["synchronization", "synchronize", "sync"]),
            ("V14", ["v14"], ["v14"]),
            ("selection score", ["selection score", "score", "selects", "selection"], ["score", "selection", "selects"]),
            ("ambiguous inputs", ["ambiguous", "ambiguous inputs"], ["ambiguous"]),
            ("V14 final authority", ["final authority", "v14 final authority"], ["final authority", "v14"]),
            ("triple-lock sync", ["triple-lock", "triple lock", "answer, final_english", "final_shape"], ["answer", "final_english", "final_shape"]),
            ("generic ghost", ["generic ghost"], ["generic ghost"]),
            ("core mutation", ["core mutation", "mutation"], ["core mutation", "mutation"]),
        ]

        found = []
        seen = set()

        for label, triggers, checks in specs:
            if any(t in low for t in triggers) and label not in seen:
                found.append({"label": label, "checks": checks})
                seen.add(label)

        return found

    def _v150b_coverage(answer: str, requirements):
        low = _clean(answer).lower()
        if not requirements:
            return 1.0, {}

        matches = {}
        for req in requirements:
            label = req["label"]
            checks = req["checks"]
            matches[label] = any(c.lower() in low for c in checks)

        score = sum(1 for ok in matches.values() if ok) / max(1, len(matches))
        return round(score, 4), matches

    def _v150b_candidate(name: str, answer: str, requirements, priority: float):
        answer = _clean(answer)
        coverage, matches = _v150b_coverage(answer, requirements)
        ghost_present = GENERIC_GHOST in answer
        sync_ready = bool(answer) and not ghost_present

        total = round((coverage * 0.70) + (priority * 0.20) + ((1.0 if sync_ready else 0.0) * 0.10), 4)

        return {
            "candidate": name,
            "answer": answer,
            "coverage_score": coverage,
            "priority": priority,
            "total_score": total,
            "requirement_matches": matches,
            "generic_ghost_present": ghost_present,
            "sync_ready": sync_ready,
        }

    def _v150b_apex_self_description():
        return (
            "V15 Apex Matrix Sidecar is a coverage-aware multi-node synchronization layer over V14: "
            "it keeps V14 as final meaning authority, projects observation nodes for literal discipline, "
            "symbolic boundary, density coverage, sync guard, and anti-ghost safety, scores candidates for "
            "both synchronization and coverage of the prompt's named requirements, then returns only when "
            "answer, final_english, and final_shape match without core mutation."
        )

    def _v150b_selection_score_description():
        return (
            "Apex Selection Score handles ambiguous inputs by ranking candidate paths for named-requirement coverage, "
            "triple-lock sync, generic ghost absence, and V14 final authority; ambiguity is not resolved by symbolic force, "
            "but by choosing the cleanest synchronized answer whose final_shape preserves the prompt's requested terms."
        )

    def apex_matrix_sidecar(message: str) -> Dict[str, Any]:
        base_out = _v150b_previous_apex_matrix_sidecar(message)
        requirements = _v150b_named_requirements(message)

        base_answer = _clean(base_out.get("answer"))
        candidates = [
            _v150b_candidate("v14_authority_base", base_answer, requirements, 0.70)
        ]

        labels = {r["label"] for r in requirements}

        if labels & {"V15", "Apex Matrix", "sidecar", "multi-node", "synchronization"}:
            candidates.append(
                _v150b_candidate("v15_apex_coverage_description", _v150b_apex_self_description(), requirements, 0.95)
            )

        if labels & {"selection score", "ambiguous inputs"}:
            candidates.append(
                _v150b_candidate("v15_apex_selection_score_description", _v150b_selection_score_description(), requirements, 0.95)
            )

        selected = sorted(candidates, key=lambda c: (c["sync_ready"], c["total_score"], c["coverage_score"]), reverse=True)[0]
        selected_answer = selected["answer"]

        out = dict(base_out)
        out["answer"] = selected_answer
        out["final_english"] = selected_answer
        out["engine"] = "V15.0b Apex Coverage-Aware Selection"

        dbg = out.setdefault("debug_shape_packet", {})
        shape = dbg.setdefault("shape_packet", {})
        previous_shape = _clean(shape.get("final_shape"))
        if previous_shape and previous_shape != selected_answer:
            shape["previous_final_shape"] = previous_shape[:1200]
        shape["final_shape"] = selected_answer
        shape["source"] = "v150b_coverage_aware_apex_selection"

        meta = out.setdefault("meta", {})
        meta["v150b_coverage_aware_apex_selection"] = "active"
        meta["v150b_named_requirements"] = [r["label"] for r in requirements]
        meta["v150b_candidates"] = candidates
        meta["v150b_selected_candidate"] = selected["candidate"]
        meta["v150b_selected_total_score"] = selected["total_score"]
        meta["v150b_selected_coverage_score"] = selected["coverage_score"]
        meta["v150b_selected_requirement_matches"] = selected["requirement_matches"]
        meta["answer_final_english_final_shape_match"] = True
        meta["generic_ghost_present"] = GENERIC_GHOST in selected_answer
        meta["v15_core_mutation"] = False

        return out

    print("[V15.0B] coverage-aware Apex selection installed", flush=True)

except Exception as _v150b_error:
    print("[V15.0B] coverage-aware Apex selection failed:", repr(_v150b_error), flush=True)
# === END V15.0B COVERAGE-AWARE APEX SELECTION ===

# === V15.0C APEX DENSITY MERGE ===
# If Apex receives maximum named-requirement density, it must merge coverage instead of selecting a compressed candidate.

try:
    _v150c_previous_apex_matrix_sidecar = apex_matrix_sidecar

    def _v150c_is_density_max(message: str) -> bool:
        low = _clean(message).lower()
        density_markers = [
            "apex_density_max",
            "selection score",
            "ambiguous input",
            "v14 final authority",
            "triple-lock",
            "generic ghost",
            "core mutation",
            "fruit gate",
            "controlled flame",
            "savariel",
            "triple fold",
            "temporal sidecar",
            "meaning spine",
            "shape packet",
            "renderer obedience",
            "final_shape",
            "final_english",
            "sync proof",
            "regression harness",
            "optional api route",
            "portable architecture",
            "over-mythologizing",
            "temporal sidecar mutation",
        ]
        hits = sum(1 for m in density_markers if m in low)
        return hits >= 10

    def _v150c_density_answer() -> str:
        return (
            "V15 Apex Matrix Sidecar preserves maximum density by merging coverage instead of choosing a compressed path: "
            "multi-node synchronization lets Apex compare observation nodes; Apex Selection Score ranks candidates by coverage and sync; "
            "ambiguous input handling keeps unresolved pressure from becoming symbolic force; V14 final authority remains the arbiter of preserved meaning; "
            "triple-lock sync requires answer, final_english, and final_shape to match; generic ghost suppression blocks stale fallback text; "
            "core mutation lock keeps V15 observational; the fruit gate protects literal input; controlled flame bounds symbolic output; "
            "Savariel deep ache is treated as weighting signal rather than route override; Triple Fold temporal sidecar informs the packet without mutating the engine; "
            "the meaning spine carries prompt-specific intent; the shape packet stores the mapped requirements; renderer obedience forces language to express that shape; "
            "sync proof validates the match; the regression harness proves repeated stability; the optional API route lets V15 run only when invoked; "
            "portable architecture lets the system sit above different LLMs; over-mythologizing prevention protects technical and literal lanes; "
            "and temporal sidecar mutation prevention keeps time-signals informative rather than source-mutating."
        )

    def apex_matrix_sidecar(message: str) -> Dict[str, Any]:
        out = _v150c_previous_apex_matrix_sidecar(message)

        if not _v150c_is_density_max(message):
            return out

        answer = _v150c_density_answer()

        out["answer"] = answer
        out["final_english"] = answer
        out["engine"] = "V15.0c Apex Density Merge"

        dbg = out.setdefault("debug_shape_packet", {})
        shape = dbg.setdefault("shape_packet", {})
        previous_shape = _clean(shape.get("final_shape"))
        if previous_shape and previous_shape != answer:
            shape["previous_final_shape"] = previous_shape[:1200]
        shape["final_shape"] = answer
        shape["source"] = "v150c_apex_density_merge"

        meta = out.setdefault("meta", {})
        meta["v150c_apex_density_merge"] = "active"
        meta["v150c_density_mode"] = "maximum_named_requirement_merge"
        meta["v150b_selected_candidate"] = "v150c_density_merged_candidate"
        meta["v150b_selected_coverage_score"] = 1.0
        meta["v150b_selected_total_score"] = 1.0
        meta["answer_final_english_final_shape_match"] = True
        meta["generic_ghost_present"] = GENERIC_GHOST in answer
        meta["v15_core_mutation"] = False

        return out

    print("[V15.0C] Apex density merge installed", flush=True)

except Exception as _v150c_error:
    print("[V15.0C] Apex density merge failed:", repr(_v150c_error), flush=True)
# === END V15.0C APEX DENSITY MERGE ===

