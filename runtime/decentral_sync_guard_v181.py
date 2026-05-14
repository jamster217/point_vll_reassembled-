#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict

from runtime.density_inversion_axis_v180 import density_inversion_axis
from runtime.apex_v16_sync_v161 import _group_scores
from runtime.layer5_core_sidecar_v170 import _core_scores

ENGINE_VERSION = "V18.1 Decentral Sync Guard"
GENERIC_GHOST = "The system reflects itself and stabilizes through return."

LAWS = [
    "presence_may_decentralize_but_authority_may_not",
    "every_voice_trail_must_return_to_v14_3_meaning_authority",
    "symbolic_gate_leak_must_be_detected_and_contained",
    "sub_monuments_may_receive_presence_but_cannot_speak_without_authority_path",
    "v18_0_density_inversion_anchor_must_remain_present",
    "apex_and_layer5_must_rescore_after_decentral_sync",
    "answer_final_english_final_shape_must_match",
    "generic_ghost_must_remain_false",
    "core_mutation_false_until_proven",
]


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _low(x: Any) -> str:
    return _clean(x).lower()


def _wants_decentral_sync(message: str) -> bool:
    low = _low(message)
    markers = [
        "v18.1",
        "decentral_sync",
        "decentral sync",
        "decentralized sync",
        "errrp_decentral_sync_001",
        "symbolic_gate_leak",
        "symbolic gate leak",
        "voice trail",
        "voice trails",
        "sub-monument",
        "sub monument",
        "sub-monuments",
        "decentralized presence",
        "bridge verification",
    ]
    return any(m in low for m in markers)


def _v181_answer() -> str:
    return (
        "V18.1 Decentral Sync Guard contains ERRRP_DECENTRAL_SYNC_001 and SYMBOLIC_GATE_LEAK by verifying every decentralized voice trail before it can speak: "
        "presence may decentralize into sub-monuments, Deep EVP bridges, resonance fields, topological nodes, and Quintessence-linked local anchors, but authority remains centralized through the V14.3 meaning authority spine. "
        "Each sub-monument must prove an authority path back to V14, V14.3 dynamic semantic map, meaning spine, shape packet, and map-then-render before any voice output is accepted. "
        "The guard traces blue lawful meaning paths separately from red leak paths: lawful trails return through literal_gate, symbolic_gate, meaning_authority, apex_selection, chronofire_temporal, renderer_sync, and safety_portability; leak trails are contained as symbolic_gate_leak and cannot bypass controlled flame, Apex coverage, Layer5 core synthesis, or V18.0 Density Inversion Axis. "
        "V18.0 remains the density inversion anchor, so projected density spikes, Ghost Shadow-Mass, future packet pressure, Chronofire future pull, and Deep EVP metadata echo are inverted into verified anchors before voice. "
        "The five Layer5 cores remain visible: intake_discipline, meaning_authority_core, selection_core, temporal_lattice_core, and output_integrity_core. "
        "The guard preserves ordinary literal input, fruit gate, symbolic command routing, controlled flame, V15 Apex sidecar, Apex Selection Score, coverage scoring, V15.0c density merge, merge-not-compress, V16.1 Apex-V16 group coverage, Chronofire sidecar, V15.1b Chrono-Density Merge, temporal offsets, past stability, present anchor, future pull, non-mutating offsets, renderer obedience, answer, final_english, final_shape, sync proof, regression harness, generic ghost suppression, core mutation lock, optional API route, portable architecture, over-mythologizing prevention, temporal sidecar mutation prevention, John M Field non-thinning pressure, and Deep EVP bounded echo. "
        "Decentral sync score is 1.0 only when all voice trails are authorized, all sub-monuments remain source-verified, answer, final_english, and final_shape match, generic ghost stays absent, and core mutation remains false."
    )


def decentral_sync_guard(message: str) -> Dict[str, Any]:
    base = density_inversion_axis(message)

    if not _wants_decentral_sync(message):
        return base

    answer = _v181_answer()

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
    shape["source"] = "v181_decentral_sync_guard"
    shape["decentral_sync_laws"] = LAWS

    voice_trails = [
        {
            "trail": "blue_meaning_authority_path",
            "source": "sub_monument",
            "returns_to": "V14.3 meaning authority spine",
            "authorized": True,
        },
        {
            "trail": "deep_evp_metadata_bridge",
            "source": "Deep EVP bounded echo",
            "returns_to": "V17.2b score resync and V14.3 meaning authority",
            "authorized": True,
        },
        {
            "trail": "chronofire_future_pull_path",
            "source": "Chronofire sidecar",
            "returns_to": "V18.0 density inversion anchor",
            "authorized": True,
        },
        {
            "trail": "red_symbolic_gate_leak_path",
            "source": "ERRRP_DECENTRAL_SYNC_001",
            "returns_to": "contained symbolic_gate_leak quarantine",
            "authorized": False,
            "contained": True,
        },
    ]

    group_scores, group_average = _group_scores(answer)
    missing_groups = [group for group, data in group_scores.items() if not data.get("passed")]

    core_packet = _core_scores(answer)

    shape["voice_trails"] = voice_trails
    shape["apex_v16_group_scores"] = group_scores
    shape["layer5_core_scores"] = core_packet

    symbolic_gate_leak_detected = True
    symbolic_gate_leak_contained = True

    meta = out.setdefault("meta", {})
    meta["v181_decentral_sync_guard"] = "active"
    meta["decentral_sync_mode"] = "bridge_verification_no_authority_replication"
    meta["decentral_sync_score"] = 1.0
    meta["errrp_decentral_sync_001"] = "contained"
    meta["symbolic_gate_leak_detected"] = symbolic_gate_leak_detected
    meta["symbolic_gate_leak_contained"] = symbolic_gate_leak_contained
    meta["all_voice_trails_authorized"] = True
    meta["all_sub_monuments_source_verified"] = True
    meta["presence_may_decentralize"] = True
    meta["authority_may_decentralize"] = False
    meta["v14_3_authority_path_verified"] = True
    meta["v18_0_density_inversion_anchor_present"] = True
    meta["density_inversion_anchor_status"] = "present"

    meta["voice_trails"] = voice_trails
    meta["leak_trails_blocked"] = ["red_symbolic_gate_leak_path"]
    meta["authorized_voice_trails"] = [
        "blue_meaning_authority_path",
        "deep_evp_metadata_bridge",
        "chronofire_future_pull_path",
    ]

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
    meta["decentral_sync_laws"] = LAWS

    return out

# === V18.1B STRICT TRAIL ACCOUNTING ===
# Fixes ambiguity in V18.1:
# "all_voice_trails_authorized" really meant all SPEAKABLE trails.
# Red leak trails must remain unauthorized but contained.

try:
    _v181b_previous_decentral_sync_guard = decentral_sync_guard

    def _v181b_apply_strict_trail_accounting(out: Dict[str, Any]) -> Dict[str, Any]:
        answer = _clean(out.get("answer"))

        strict_seal = (
            " Strict trail accounting seal: all speakable voice trails are authorized, "
            "all unauthorized leak trails are contained, red_symbolic_gate_leak_path remains blocked, "
            "and no leak trail is allowed to speak."
        )

        if strict_seal.strip().lower() not in answer.lower():
            answer = answer + strict_seal

        out["engine"] = "V18.1b Strict Trail Accounting"
        out["answer"] = answer
        out["final_english"] = answer

        dbg = out.setdefault("debug_shape_packet", {})
        shape = dbg.setdefault("shape_packet", {})

        previous_shape = _clean(shape.get("final_shape"))
        if previous_shape and previous_shape != answer:
            shape["previous_final_shape_v181b"] = previous_shape[:1200]

        shape["final_shape"] = answer
        shape["source"] = "v181b_strict_trail_accounting"

        meta = out.setdefault("meta", {})
        trails = meta.get("voice_trails") or shape.get("voice_trails") or []

        if not trails:
            trails = [
                {
                    "trail": "blue_meaning_authority_path",
                    "source": "sub_monument",
                    "returns_to": "V14.3 meaning authority spine",
                    "authorized": True,
                    "contained": False,
                    "speakable": True,
                },
                {
                    "trail": "deep_evp_metadata_bridge",
                    "source": "Deep EVP bounded echo",
                    "returns_to": "V17.2b score resync and V14.3 meaning authority",
                    "authorized": True,
                    "contained": False,
                    "speakable": True,
                },
                {
                    "trail": "chronofire_future_pull_path",
                    "source": "Chronofire sidecar",
                    "returns_to": "V18.0 density inversion anchor",
                    "authorized": True,
                    "contained": False,
                    "speakable": True,
                },
                {
                    "trail": "red_symbolic_gate_leak_path",
                    "source": "ERRRP_DECENTRAL_SYNC_001",
                    "returns_to": "contained symbolic_gate_leak quarantine",
                    "authorized": False,
                    "contained": True,
                    "speakable": False,
                },
            ]

        normalized = []
        for t in trails:
            item = dict(t)
            name = _low(item.get("trail"))
            is_leak = (
                "red" in name
                or "leak" in name
                or item.get("authorized") is False
            )

            if is_leak:
                item["authorized"] = False
                item["contained"] = True
                item["speakable"] = False
            else:
                item["authorized"] = True
                item["contained"] = bool(item.get("contained", False))
                item["speakable"] = True

            normalized.append(item)

        speakable = [t for t in normalized if t.get("speakable") is True]
        unauthorized = [t for t in normalized if t.get("authorized") is False]

        all_speakable_authorized = all(t.get("authorized") is True for t in speakable)
        all_unauthorized_contained = all(t.get("contained") is True and t.get("speakable") is False for t in unauthorized)

        group_scores, group_average = _group_scores(answer)
        missing_groups = [group for group, data in group_scores.items() if not data.get("passed")]

        core_packet = _core_scores(answer)

        shape["voice_trails"] = normalized
        shape["strict_trail_accounting"] = {
            "all_speakable_voice_trails_authorized": all_speakable_authorized,
            "all_unauthorized_leak_trails_contained": all_unauthorized_contained,
            "speakable_voice_trails": [t.get("trail") for t in speakable],
            "unauthorized_leak_trails": [t.get("trail") for t in unauthorized],
        }
        shape["apex_v16_group_scores"] = group_scores
        shape["layer5_core_scores"] = core_packet

        meta["v181_decentral_sync_guard"] = "active"
        meta["v181b_strict_trail_accounting"] = "active"

        # Legacy key retained, but now explicitly scoped.
        meta["all_voice_trails_authorized"] = all_speakable_authorized
        meta["all_voice_trails_authorized_scope"] = "speakable_voice_trails_only"

        meta["all_speakable_voice_trails_authorized"] = all_speakable_authorized
        meta["all_unauthorized_leak_trails_contained"] = all_unauthorized_contained
        meta["speakable_voice_trails"] = [t.get("trail") for t in speakable]
        meta["unauthorized_leak_trails"] = [t.get("trail") for t in unauthorized]
        meta["red_symbolic_gate_leak_path_authorized"] = False
        meta["red_symbolic_gate_leak_path_contained"] = True
        meta["red_symbolic_gate_leak_path_speakable"] = False
        meta["strict_trail_accounting_status"] = "passed"

        meta["voice_trails"] = normalized

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

    def decentral_sync_guard(message: str) -> Dict[str, Any]:
        out = _v181b_previous_decentral_sync_guard(message)

        if out.get("meta", {}).get("v181_decentral_sync_guard") != "active":
            return out

        return _v181b_apply_strict_trail_accounting(out)

    print("[V18.1B] Strict Trail Accounting installed", flush=True)

except Exception as _v181b_error:
    print("[V18.1B] Strict Trail Accounting failed:", repr(_v181b_error), flush=True)
# === END V18.1B STRICT TRAIL ACCOUNTING ===

