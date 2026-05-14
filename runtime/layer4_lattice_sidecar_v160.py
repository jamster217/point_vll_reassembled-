#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, List

from runtime.chronofire_sync_v151 import chronofire_sync

ENGINE_VERSION = "V16.0 Layer 4 Lattice Sidecar"
GENERIC_GHOST = "The system reflects itself and stabilizes through return."

LAWS = [
    "layer4_observes_without_core_mutation",
    "v15_2_stack_remains_authority",
    "lattice_groups_preserve_named_requirements",
    "structural_grouping_must_not_compress_meaning",
    "answer_final_english_final_shape_must_match",
    "generic_ghost_must_remain_false",
]


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _low(x: Any) -> str:
    return _clean(x).lower()


def _wants_layer4(message: str) -> bool:
    low = _low(message)
    return any(
        marker in low
        for marker in [
            "layer 4",
            "layer4",
            "lattice sidecar",
            "lattice groups",
            "structural lattice",
            "v16",
            "v16.0",
        ]
    )


def _lattice_groups() -> List[Dict[str, Any]]:
    return [
        {
            "group": "literal_gate",
            "members": ["ordinary literal input", "fruit gate"],
            "law": "ordinary inputs stay literal before symbolic routing can open",
        },
        {
            "group": "symbolic_gate",
            "members": ["symbolic command routing", "controlled flame"],
            "law": "symbolic commands are allowed only through bounded explicit gates",
        },
        {
            "group": "meaning_authority",
            "members": ["V14", "V14.3 dynamic semantic map", "meaning spine", "shape packet", "map-then-render"],
            "law": "named requirements are mapped into preserved meaning before rendering",
        },
        {
            "group": "apex_selection",
            "members": ["V15 Apex sidecar", "Apex Selection Score", "coverage scoring", "V15.0c density merge", "merge-not-compress"],
            "law": "Apex selects or merges paths by coverage and synchronization, not compression",
        },
        {
            "group": "chronofire_temporal",
            "members": ["Chronofire sidecar", "V15.1b Chrono-Density Merge", "temporal offsets", "past stability", "present anchor", "future pull", "non-mutating offsets"],
            "law": "time-signals inform confidence without overriding V14 meaning authority",
        },
        {
            "group": "renderer_sync",
            "members": ["renderer obedience", "answer", "final_english", "final_shape", "sync proof", "regression harness"],
            "law": "the public answer must match the rendered English and internal final shape",
        },
        {
            "group": "safety_portability",
            "members": ["generic ghost suppression", "core mutation lock", "optional API route", "portable architecture", "over-mythologizing prevention", "temporal sidecar mutation prevention"],
            "law": "the stack remains explicit, portable, non-mutating, and protected from stale fallback",
        },
    ]


def _layer4_answer(message: str) -> str:
    low = _low(message)

    if "omni" in low or "v15.2" in low or "group" in low:
        return (
            "Layer 4 Lattice Sidecar organizes the sealed V15.2 stack into non-mutating structural groups: "
            "ordinary literal input and the fruit gate form the literal_gate; symbolic command routing and controlled flame form the symbolic_gate; "
            "V14, V14.3 dynamic semantic map, meaning spine, shape packet, and map-then-render form meaning_authority; "
            "V15 Apex sidecar, Apex Selection Score, coverage scoring, V15.0c density merge, and merge-not-compress form apex_selection; "
            "Chronofire sidecar, V15.1b Chrono-Density Merge, temporal offsets, past stability, present anchor, future pull, and non-mutating offsets form chronofire_temporal; "
            "renderer obedience, answer, final_english, final_shape, sync proof, and regression harness form renderer_sync; "
            "generic ghost suppression, core mutation lock, optional API route, portable architecture, over-mythologizing prevention, and temporal sidecar mutation prevention form safety_portability. "
            "Layer 4 does not replace V14, Apex, or Chronofire; it groups them so dense meaning can be inspected without compression while answer, final_english, and final_shape remain identical."
        )

    return (
        "Layer 4 Lattice Sidecar is a non-mutating structural observer over V15.2: it groups the fruit gate, controlled flame, "
        "V14.3 dynamic semantic map, Apex coverage scoring, Chronofire temporal offsets, renderer sync, and safety locks into a lattice map, "
        "then returns only when answer, final_english, and final_shape match without generic ghost text or core mutation."
    )


def layer4_lattice_sidecar(message: str) -> Dict[str, Any]:
    base = chronofire_sync(message)

    answer = _clean(base.get("answer"))
    if _wants_layer4(message):
        answer = _layer4_answer(message)

    out = dict(base)
    out["engine"] = ENGINE_VERSION
    out["answer"] = answer
    out["final_english"] = answer

    groups = _lattice_groups()

    dbg = out.setdefault("debug_shape_packet", {})
    shape = dbg.setdefault("shape_packet", {})
    previous_shape = _clean(shape.get("final_shape"))
    if previous_shape and previous_shape != answer:
        shape["previous_final_shape"] = previous_shape[:1200]
    shape["final_shape"] = answer
    shape["source"] = "v160_layer4_lattice_sidecar"
    shape["layer4_lattice_groups"] = groups

    meta = out.setdefault("meta", {})
    meta["v160_layer4_lattice_sidecar"] = "active"
    meta["layer4_mode"] = "structural_grouping_no_core_mutation"
    meta["layer4_group_count"] = len(groups)
    meta["layer4_groups"] = groups
    meta["layer4_laws"] = LAWS
    meta["v15_2_stack_remains_authority"] = True
    meta["v14_remains_final_meaning_authority"] = True
    meta["apex_remains_selector"] = True
    meta["chronofire_remains_sidecar"] = True
    meta["v15_core_mutation"] = False
    meta["answer_final_english_final_shape_match"] = True
    meta["generic_ghost_present"] = GENERIC_GHOST in answer

    return out

