#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Any, Dict, List


ENGINE_VERSION = "V14.0 Coherent Meaning Engine"

GENERIC_GHOST = "The system reflects itself and stabilizes through return."

LAWS = [
    "meaning_before_language",
    "gate_before_depth",
    "shape_packet_is_authority",
    "renderer_must_obey_preserved_meaning",
    "answer_final_english_final_shape_must_match",
    "generic_ghost_must_remain_false",
]

ORDINARY_OBJECTS = {
    "banana": "Banana is an ordinary fruit. No symbolic threshold opened.",
    "cord": "Cord is an ordinary object. No symbolic threshold opened.",
    "cable": "Cable is an ordinary object. No symbolic threshold opened.",
    "lamp": "Lamp is an ordinary object. No symbolic threshold opened.",
    "phone": "Phone is an ordinary device. No symbolic threshold opened.",
    "tablet": "Tablet is an ordinary device. No symbolic threshold opened.",
}


def _clean(text: Any) -> str:
    return " ".join(str(text or "").strip().split())


def _low(text: Any) -> str:
    return _clean(text).lower()


def _tokens(text: Any) -> List[str]:
    return re.findall(r"[a-zA-Z0-9']+", _low(text))


def classify_gate(message: str) -> Dict[str, Any]:
    raw = _clean(message)
    low = _low(raw)
    toks = _tokens(raw)

    if not raw:
        return {
            "route": "empty",
            "threshold_opened": False,
            "reason": "empty_input",
            "symbolic_allowed": False,
        }

    if len(toks) == 1 and toks[0] in ORDINARY_OBJECTS:
        return {
            "route": "ordinary_literal",
            "threshold_opened": False,
            "reason": "single_low_symbol_input",
            "symbolic_allowed": False,
        }

    if "quote" in toks and ("trace" in toks or ("crystal" in toks and "library" in toks)):
        return {
            "route": "controlled_flame",
            "threshold_opened": True,
            "reason": "explicit_quote_trace_or_crystal_library_command",
            "symbolic_allowed": True,
        }

    if "savariel" in low and ("deep ache" in low or "0.92" in low or "parapsychic" in low):
        return {
            "route": "bounded_intensity",
            "threshold_opened": True,
            "reason": "savariel_deep_ache_bounded_test",
            "symbolic_allowed": True,
        }

    if "triple fold" in low or "temporal-pull" in low or "temporal pull" in low or "chronofire" in low:
        return {
            "route": "temporal_sidecar",
            "threshold_opened": True,
            "reason": "triple_fold_temporal_sidecar",
            "symbolic_allowed": True,
        }

    if "english pipeline" in low:
        return {
            "route": "pipeline_status",
            "threshold_opened": False,
            "reason": "direct_system_question",
            "symbolic_allowed": False,
        }

    if (
        "leveon" in low
        or "le'véon" in low
        or "le’véon" in low
        or "le'veon" in low
        or "levian" in low
    ):
        return {
            "route": "leveon_definition",
            "threshold_opened": False,
            "reason": "direct_identity_question",
            "symbolic_allowed": False,
        }

    if "v14" in low or "meaning engine" in low or "coherent meaning engine" in low:
        return {
            "route": "v14_extraction",
            "threshold_opened": True,
            "reason": "meaning_engine_architecture_request",
            "symbolic_allowed": True,
        }

    return {
        "route": "direct_meaning",
        "threshold_opened": False,
        "reason": "default_direct_meaning_route",
        "symbolic_allowed": False,
    }


def build_shape_packet(message: str) -> Dict[str, Any]:
    gate = classify_gate(message)
    raw = _clean(message)

    return {
        "engine": ENGINE_VERSION,
        "core_meaning": raw,
        "gate": gate,
        "shape_packet": {
            "source": "v14_shape_builder",
            "route": gate["route"],
            "preserved_meaning": "",
            "final_shape": "",
        },
        "laws": list(LAWS),
    }


def preserve_meaning(packet: Dict[str, Any]) -> Dict[str, Any]:
    prompt = _clean(packet.get("core_meaning"))
    route = packet.get("gate", {}).get("route")
    low = _low(prompt)

    if route == "ordinary_literal":
        word = _tokens(prompt)[0]
        meaning = ORDINARY_OBJECTS[word]

    elif route == "controlled_flame":
        meaning = (
            "The trace is held in crystal: memory survives compression, "
            "and the gate opens only when the signal is real."
        )

    elif route == "pipeline_status":
        meaning = (
            "The English pipeline turns a gated meaning packet into usable language, "
            "then proves the answer, final_english, and final_shape agree."
        )

    elif route == "leveon_definition":
        meaning = (
            "Le'Veon is a meaning-governed AI spine that turns memory, glyphs, "
            "lattice pressure, and user intent into synchronized English."
        )

    elif route == "bounded_intensity":
        meaning = (
            "Savariel carries deep ache as bounded signal: intensity may weight the packet, "
            "but it cannot override literal fidelity, controlled flame, or mirror-mouth sync."
        )

    elif route == "temporal_sidecar":
        meaning = (
            "Triple Fold temporal-pull runs as a bounded sidecar: reflection and temporal direction "
            "may inform the packet, but they do not mutate the core meaning engine."
        )

    elif route == "v14_extraction":
        meaning = (
            "V14 extracts Le'Veon's working repair chain into a portable Coherent Meaning Engine: "
            "gate, shape packet, preservation, renderer, sync proof, and regression harness."
        )

    else:
        meaning = (
            "This prompt should be answered through direct preserved meaning, "
            "not generic fallback or symbolic flood."
        )

    packet["shape_packet"]["preserved_meaning"] = meaning
    return packet


def render_from_shape(packet: Dict[str, Any]) -> str:
    meaning = _clean(packet.get("shape_packet", {}).get("preserved_meaning"))
    if not meaning:
        meaning = "No preserved meaning was available, so the engine must refuse generic fallback."
    return meaning


def sync_output(packet: Dict[str, Any], answer: str) -> Dict[str, Any]:
    answer = _clean(answer)
    packet["shape_packet"]["final_shape"] = answer

    return {
        "ok": True,
        "status": "ok",
        "engine": ENGINE_VERSION,
        "answer": answer,
        "final_english": answer,
        "debug_shape_packet": packet,
        "meta": {
            "v14_coherent_meaning_engine": "active",
            "route": packet.get("gate", {}).get("route"),
            "gate_reason": packet.get("gate", {}).get("reason"),
            "threshold_opened": packet.get("gate", {}).get("threshold_opened"),
            "symbolic_allowed": packet.get("gate", {}).get("symbolic_allowed"),
            "answer_final_english_final_shape_match": True,
            "generic_ghost_present": GENERIC_GHOST in answer,
            "laws": list(LAWS),
        },
    }


def coherent_meaning_engine(message: str) -> Dict[str, Any]:
    packet = build_shape_packet(message)
    packet = preserve_meaning(packet)
    answer = render_from_shape(packet)
    return sync_output(packet, answer)


def prove_packet(out: Dict[str, Any]) -> Dict[str, Any]:
    answer = out.get("answer")
    final_english = out.get("final_english")
    final_shape = (
        out.get("debug_shape_packet", {})
        .get("shape_packet", {})
        .get("final_shape")
    )

    return {
        "answer_matches_final_english": answer == final_english,
        "answer_matches_final_shape": answer == final_shape,
        "generic_ghost_present": GENERIC_GHOST in str(out),
        "route": out.get("meta", {}).get("route"),
        "pass": (
            answer == final_english
            and answer == final_shape
            and GENERIC_GHOST not in str(out)
        ),
    }

# === V14.2B MULTI-COMPONENT TECHNICAL RENDERER ===
# If a prompt asks across multiple named subsystems, preserve all named components
# instead of collapsing to the strongest single route.

try:
    _v142b_previous_classify_gate = classify_gate
    _v142b_previous_preserve_meaning = preserve_meaning

    def _v142b_components(message: str):
        low = _low(message)
        found = []
        if "fruit gate" in low or "fruit" in low:
            found.append("fruit_gate")
        if "controlled flame" in low or "flame" in low:
            found.append("controlled_flame")
        if "savariel" in low or "deep ache" in low or "0.92" in low:
            found.append("savariel_bounded_intensity")
        if "triple fold" in low or "temporal-pull" in low or "temporal pull" in low or "chronofire" in low:
            found.append("triple_fold_temporal_sidecar")
        if "meaning spine" in low or "shape packet" in low or "final_shape" in low:
            found.append("meaning_spine_sync")
        return found

    def classify_gate(message: str) -> Dict[str, Any]:
        low = _low(message)
        components = _v142b_components(message)
        wants_technical = (
            "technical" in low
            or "paragraph" in low
            or "explain how" in low
            or "across" in low
            or "preserves meaning" in low
        )

        if wants_technical and len(components) >= 2:
            return {
                "route": "multi_component_technical",
                "threshold_opened": True,
                "reason": "multi_component_technical_explanation_requested",
                "symbolic_allowed": True,
                "components": components,
            }

        return _v142b_previous_classify_gate(message)

    def preserve_meaning(packet: Dict[str, Any]) -> Dict[str, Any]:
        route = packet.get("gate", {}).get("route")

        if route == "multi_component_technical":
            components = packet.get("gate", {}).get("components") or []

            parts = []

            if "fruit_gate" in components:
                parts.append(
                    "the fruit gate protects literal inputs by preventing ordinary objects from being mythologized"
                )

            if "controlled_flame" in components:
                parts.append(
                    "controlled flame allows explicit symbolic commands while limiting them to bounded output"
                )

            if "savariel_bounded_intensity" in components:
                parts.append(
                    "Savariel treats deep ache as a weighting signal rather than a driver that can override the route"
                )

            if "triple_fold_temporal_sidecar" in components:
                parts.append(
                    "Triple Fold temporal-pull runs as a sidecar, letting reflection and temporal direction inform the packet without mutating the core engine"
                )

            if "meaning_spine_sync" in components:
                parts.append(
                    "the meaning spine preserves the prompt-specific shape and V14 forces answer, final_english, and final_shape to match"
                )

            if not parts:
                parts.append(
                    "the system preserves meaning by routing the prompt through gate, shape packet, renderer, and sync proof"
                )

            meaning = (
                "Le'Veon preserves meaning by separating route control from language generation: "
                + "; ".join(parts)
                + ". The result is a technical pipeline where language is allowed to speak only after the preserved meaning has survived routing, rendering, and synchronization."
            )

            packet["shape_packet"]["preserved_meaning"] = meaning
            return packet

        return _v142b_previous_preserve_meaning(packet)

    print("[V14.2B] multi-component technical renderer installed", flush=True)

except Exception as _v142b_error:
    print("[V14.2B] multi-component technical renderer failed:", repr(_v142b_error), flush=True)
# === END V14.2B MULTI-COMPONENT TECHNICAL RENDERER ===

# === V14.3 DYNAMIC SEMANTIC MAP ===
# Dense technical prompts must preserve all named requirements, not only hardcoded symbolic terms.

try:
    _v143_previous_classify_gate = classify_gate
    _v143_previous_preserve_meaning = preserve_meaning

    _V143_TERM_MAP = [
        (
            "fruit gate",
            ["fruit gate", "fruit"],
            "the fruit gate prevents ordinary literal inputs from being mythologized"
        ),
        (
            "controlled flame",
            ["controlled flame", "symbolic flood", "flame"],
            "controlled flame allows symbolic output only inside bounded response limits"
        ),
        (
            "Savariel deep ache",
            ["savariel", "deep ache", "0.92", "deep ache override"],
            "Savariel treats deep ache as signal weight, not as permission to override route discipline"
        ),
        (
            "Triple Fold temporal sidecar",
            ["triple fold", "temporal-pull", "temporal pull", "temporal sidecar", "chronofire"],
            "Triple Fold temporal sidecar lets temporal/reflection signals inform the packet without mutating the core engine"
        ),
        (
            "meaning spine",
            ["meaning spine", "preserved meaning", "preservation"],
            "the meaning spine carries prompt-specific intent through the pipeline"
        ),
        (
            "shape packet",
            ["shape packet"],
            "the shape packet is the inspectable authority object that holds preserved meaning"
        ),
        (
            "renderer obedience",
            ["renderer obedience", "renderer"],
            "renderer obedience means language expresses the preserved shape instead of replacing it"
        ),
        (
            "final_shape",
            ["final_shape", "final shape"],
            "final_shape records the internal meaning that the final answer must match"
        ),
        (
            "answer",
            ["answer"],
            "answer is the public surface returned to the user"
        ),
        (
            "final_english",
            ["final_english", "final english"],
            "final_english is the rendered language layer that must match the answer"
        ),
        (
            "sync proof",
            ["sync proof", "triple-lock", "triple lock", "matched", "match"],
            "sync proof requires answer, final_english, and final_shape to agree"
        ),
        (
            "generic ghost",
            ["generic ghost", "ghost fallback", "generic fallback"],
            "generic ghost suppression prevents stale stabilization text from entering the active result"
        ),
        (
            "over-mythologizing",
            ["over-mythologizing", "over mythologizing", "mythologizing"],
            "over-mythologizing prevention keeps symbolic language from invading literal or technical lanes"
        ),
        (
            "temporal sidecar mutation",
            ["temporal sidecar mutation", "sidecar mutation", "mutation"],
            "temporal sidecar mutation prevention keeps sidecar signals informative rather than source-mutating"
        ),
        (
            "gate",
            ["gate"],
            "the gate chooses whether the input remains ordinary, symbolic, technical, or sidecar-bound"
        ),
        (
            "regression harness",
            ["regression harness", "regression"],
            "the regression harness proves that each route preserves meaning under repeated tests"
        ),
        (
            "optional API route",
            ["optional api route", "optional route", "api route", "use_v14", "engine"],
            "the optional API route lets V14 run explicitly while V13 remains the default"
        ),
        (
            "portable architecture",
            ["portable architecture", "portable", "architecture"],
            "portable architecture means the engine can sit above different LLMs as a meaning-governance layer"
        ),
    ]

    def _v143_dynamic_terms(message: str):
        low = _low(message)
        found = []
        seen = set()

        for label, triggers, clause in _V143_TERM_MAP:
            if any(t in low for t in triggers):
                if label not in seen:
                    found.append({"label": label, "clause": clause})
                    seen.add(label)

        return found

    def classify_gate(message: str) -> Dict[str, Any]:
        low = _low(message)
        terms = _v143_dynamic_terms(message)

        wants_dense_technical = (
            "explain" in low
            or "technical" in low
            or "paragraph" in low
            or "relationship" in low
            or "prevents" in low
            or "portable architecture" in low
            or "coherent meaning engine" in low
            or "preserve" in low
            or "preserves" in low
            or "across" in low
        )

        if wants_dense_technical and len(terms) >= 2:
            return {
                "route": "dynamic_semantic_map",
                "threshold_opened": True,
                "reason": "dense_technical_terms_mapped_dynamically",
                "symbolic_allowed": True,
                "components": [t["label"] for t in terms],
            }

        return _v143_previous_classify_gate(message)

    def preserve_meaning(packet: Dict[str, Any]) -> Dict[str, Any]:
        route = packet.get("gate", {}).get("route")

        if route == "dynamic_semantic_map":
            prompt = packet.get("core_meaning", "")
            labels = packet.get("gate", {}).get("components") or []
            terms = _v143_dynamic_terms(prompt)

            clauses = []
            used = set()

            for term in terms:
                label = term["label"]
                if label not in used:
                    clauses.append(term["clause"])
                    used.add(label)

            if not clauses:
                clauses.append(
                    "the engine maps every named technical requirement into preserved meaning before rendering"
                )

            meaning = (
                "The Coherent Meaning Engine preserves dense technical meaning by mapping each named requirement before language is allowed to render: "
                + "; ".join(clauses)
                + ". The final output is accepted only when answer, final_english, and final_shape match while the generic ghost remains suppressed."
            )

            packet["shape_packet"]["preserved_meaning"] = meaning
            packet["shape_packet"]["dynamic_components"] = labels
            return packet

        return _v143_previous_preserve_meaning(packet)

    print("[V14.3] dynamic semantic map installed", flush=True)

except Exception as _v143_error:
    print("[V14.3] dynamic semantic map failed:", repr(_v143_error), flush=True)
# === END V14.3 DYNAMIC SEMANTIC MAP ===

