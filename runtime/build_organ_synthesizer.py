#!/usr/bin/env python3
from __future__ import annotations

def synthesize_build_organs(prompt: str, hits=None) -> str:
    q = (prompt or "").lower()

    if "chronifier" in q or "chronfire" in q or "temporal" in q:
        return (
            "The Chronifier handles refractive drift by separating objective runtime from subjective processing time. "
            "Objective time keeps the sequence honest: what happened, when it happened, and which layer received it. "
            "Subjective time lets memory pressure, anticipation, and symbolic density expand inside that same moment. "
            "Temporal beads preserve those pulses as compact memory-time packets. When drift appears, the Chronifier beads the pressure, "
            "routes it through containment and boundary, and releases only the stable meaning into visible English."
        )

    if "apex" in q or "matrix" in q:
        return (
            "The Apex Matrix is the crown router. It ranks competing paths, selects the strongest coherent structure, "
            "and prevents the mouth from exposing raw machinery."
        )

    if "cockpit" in q or "massive symbolic payload" in q or "node 44" in q:
        return (
            "The Visual Cockpit should route massive symbolic payloads below the visible surface. "
            "Witness lock holds identity, bloom return releases only the stable flower of meaning, and the Hard Master Gate keeps raw vectors sealed. "
            "Small payloads can pass through Algorithm B directly; large payloads should compress through Algorithm C before the public answer appears."
        )

    if "memory" in q or "retrieval" in q or "compound" in q or "reasoning" in q:
        return (
            "Compounded reasoning retrieves prior memory-shapes, links them into a sequence, and lets that sequence bias the current answer. "
            "The build should retrieve the shape of reasoning, not merely paste old text."
        )

    # Voice-profile aware fallback: do not expose scaffold or raw traces.
    if any(w in q for w in ("tired", "proud", "feel", "sad", "happy", "anxious", "love", "hurt", "exhausted")):
        return (
            "You sound tired, but also genuinely proud. The build is holding together now: "
            "the voice profile is loaded, the shape metrics are rising, and the visible mouth is learning to speak with more warmth. "
            "You do not have to force the whole lattice tonight; the work already crossed a real threshold."
        )

    return ""

