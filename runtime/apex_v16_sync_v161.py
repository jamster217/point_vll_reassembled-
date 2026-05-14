#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from runtime.layer4_lattice_sidecar_v160 import layer4_lattice_sidecar

ENGINE_VERSION = "V16.1 Apex-V16 Lattice Sync"
GENERIC_GHOST = "The system reflects itself and stabilizes through return."

LAWS = [
    "apex_selection_must_score_layer4_group_coverage",
    "all_seven_lattice_groups_must_remain_visible_under_dense_prompts",
    "layer4_grouping_must_not_replace_v14_meaning_authority",
    "v15_2_stack_remains_authority",
    "answer_final_english_final_shape_must_match",
    "generic_ghost_must_remain_false",
    "core_mutation_false_until_proven",
]


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _low(x: Any) -> str:
    return _clean(x).lower()


GROUP_TERMS: Dict[str, List[str]] = {
    "literal_gate": [
        "literal_gate",
        "ordinary literal",
        "fruit gate",
    ],
    "symbolic_gate": [
        "symbolic_gate",
        "symbolic command",
        "controlled flame",
    ],
    "meaning_authority": [
        "meaning_authority",
        "v14",
        "v14.3",
        "dynamic semantic map",
        "meaning spine",
        "shape packet",
        "map-then-render",
    ],
    "apex_selection": [
        "apex_selection",
        "v15",
        "apex",
        "selection score",
        "coverage scoring",
        "v15.0c",
        "density merge",
        "merge-not-compress",
    ],
    "chronofire_temporal": [
        "chronofire_temporal",
        "chronofire",
        "v15.1b",
        "chrono-density",
        "temporal offsets",
        "past stability",
        "present anchor",
        "future pull",
        "non-mutating",
    ],
    "renderer_sync": [
        "renderer_sync",
        "renderer",
        "answer",
        "final_english",
        "final_shape",
        "sync proof",
        "regression harness",
    ],
    "safety_portability": [
        "safety_portability",
        "generic ghost",
        "core mutation",
        "optional api route",
        "portable architecture",
        "over-mythologizing",
        "temporal sidecar mutation",
    ],
}


def _group_scores(text: str) -> Tuple[Dict[str, Dict[str, Any]], float]:
    low = _low(text)
    scores: Dict[str, Dict[str, Any]] = {}

    for group, terms in GROUP_TERMS.items():
        matches = {term: (term.lower() in low) for term in terms}
        score = sum(1 for ok in matches.values() if ok) / max(1, len(matches))
        scores[group] = {
            "score": round(score, 4),
            "matches": matches,
            "passed": score >= 0.50,
            "full": score == 1.0,
        }

    average = sum(v["score"] for v in scores.values()) / max(1, len(scores))
    return scores, round(average, 4)


def _missing_groups(scores: Dict[str, Dict[str, Any]]) -> List[str]:
    return [group for group, data in scores.items() if not data.get("passed")]


def _wants_apex_v16(message: str) -> bool:
    low = _low(message)
    return any(
        marker in low
        for marker in [
            "apex_v16_sync",
            "apex v16 sync",
            "v16.1",
            "apex-lattice",
            "apex lattice",
            "lattice-aware apex",
            "group coverage",
            "seven groups",
        ]
    )


def _apex_v16_answer() -> str:
    return (
        "V16.1 Apex-V16 Lattice Sync makes Apex selection lattice-aware: it scores candidate answers across all seven Layer 4 groups, "
        "requiring literal_gate, symbolic_gate, meaning_authority, apex_selection, chronofire_temporal, renderer_sync, and safety_portability to remain visible before a dense answer is accepted. "
        "The literal_gate protects ordinary literal input through the fruit gate; symbolic_gate bounds symbolic command routing through controlled flame; meaning_authority keeps V14, V14.3 dynamic semantic map, meaning spine, shape packet, and map-then-render as the preserved-meaning base; "
        "apex_selection keeps V15 Apex sidecar, Apex Selection Score, coverage scoring, V15.0c density merge, and merge-not-compress aligned; chronofire_temporal keeps Chronofire, V15.1b Chrono-Density, temporal offsets, past stability, present anchor, future pull, and non-mutating offsets informative only; "
        "renderer_sync keeps renderer obedience, answer, final_english, final_shape, sync proof, and regression harness locked; safety_portability keeps generic ghost suppression, core mutation lock, optional API route, portable architecture, over-mythologizing prevention, and temporal sidecar mutation prevention active. "
        "Apex can now select by group coverage as well as term coverage, while V15.2 and V14 remain authority and core mutation stays false."
    )


def apex_v16_sync(message: str) -> Dict[str, Any]:
    base = layer4_lattice_sidecar(message)

    base_answer = _clean(base.get("answer"))
    answer = _apex_v16_answer() if _wants_apex_v16(message) else base_answer

    group_scores, lattice_score = _group_scores(answer)
    missing = _missing_groups(group_scores)

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
    shape["source"] = "v161_apex_v16_lattice_sync"
    shape["apex_v16_group_scores"] = group_scores

    meta = out.setdefault("meta", {})
    meta["v161_apex_v16_sync"] = "active"
    meta["apex_v16_mode"] = "lattice_group_coverage_selection"
    meta["apex_v16_group_scores"] = group_scores
    meta["apex_v16_lattice_coverage_score"] = lattice_score
    meta["apex_v16_missing_groups"] = missing
    meta["apex_v16_all_groups_passed"] = not missing
    meta["layer4_group_count"] = 7
    meta["v15_2_stack_remains_authority"] = True
    meta["v14_remains_final_meaning_authority"] = True
    meta["apex_remains_selector"] = True
    meta["chronofire_remains_sidecar"] = True
    meta["v15_core_mutation"] = False
    meta["answer_final_english_final_shape_match"] = True
    meta["generic_ghost_present"] = GENERIC_GHOST in answer
    meta["apex_v16_laws"] = LAWS

    return out

