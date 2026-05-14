#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict

from runtime.sigil_context_runtime import latest_sigil_context

LOG_PATH = Path("logs/crystal_sigil/adapter_events.jsonl")


def _f(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _synthetic_witness_from_sigil(ctx: Dict[str, Any]):
    vectors = ctx.get("vectors", {}) or {}
    tokens = [str(t).lower() for t in (ctx.get("tokens", []) or [])]
    token_blob = " ".join(tokens)

    pressure = _f(vectors.get("pressure"), 0.45)
    memory = _f(vectors.get("memory"), 0.45)
    boundary = _f(vectors.get("boundary"), 0.45)
    voice = _f(vectors.get("voice"), 0.45)
    novelty = _f(vectors.get("novelty"), 0.45)
    mode = str(ctx.get("mode", "observe"))

    # Shape the state so kernel.crystal_library.CrystalLibrary can read it.
    signature = "witness_lock"
    emotional_shift = "reflective_shift"
    recursion_depth = 0

    if mode == "stabilize" and pressure >= 0.75:
        signature = "witness_lock"
    elif mode == "expand" and novelty >= 0.55:
        signature = "bloom_signal"
        emotional_shift = "uplift_shift"
    elif "mirror" in token_blob or "return" in token_blob:
        signature = "mirror_resonance"
    elif any(x in token_blob for x in ["grief", "ash", "gravity", "well"]):
        emotional_shift = "sorrow_shift"
        recursion_depth = 1

    tags = {
        "deeper": max(pressure, memory),
        "dream_field": novelty,
        "emotional_field": pressure,
        "boundary": boundary,
        "voice": voice,
        "sigil_ripple_count": _f(ctx.get("ripple_count"), 0.0),
    }

    return SimpleNamespace(
        signature=signature,
        emotional_shift=emotional_shift,
        recursion_depth=recursion_depth,
        tags=tags,
        resonance_label="",
        witness_summary="",
    )


def _role_from_vectors(ctx: Dict[str, Any]) -> Dict[str, Any]:
    v = ctx.get("vectors", {}) or {}
    mode = str(ctx.get("mode", "observe"))

    pressure = _f(v.get("pressure"), 0.45)
    memory = _f(v.get("memory"), 0.45)
    boundary = _f(v.get("boundary"), 0.45)
    voice = _f(v.get("voice"), 0.45)
    novelty = _f(v.get("novelty"), 0.45)

    if mode == "stabilize" and (pressure >= 0.75 or boundary >= 0.6):
        role = "containment_tightener"
        summary = "This sigil increases containment and keeps the field from over-expanding."
    elif mode == "expand" and (voice >= 0.55 or novelty >= 0.55):
        role = "transformative_opener"
        summary = "This sigil opens voice and novelty while preserving the originating shape."
    elif memory >= 0.7:
        role = "structure_builder"
        summary = "This sigil strengthens memory structure and anchors repeated meaning."
    else:
        role = "stable_diagnostic"
        summary = "This sigil is useful for reading the current field without forcing mutation."

    return {
        "role": role,
        "summary": summary,
        "mode": mode,
        "vectors": {
            "pressure": pressure,
            "memory": memory,
            "boundary": boundary,
            "voice": voice,
            "novelty": novelty,
        },
    }


def _voice_context_from_vectors(ctx: Dict[str, Any]) -> Dict[str, Any]:
    v = ctx.get("vectors", {}) or {}
    mode = str(ctx.get("mode", "observe"))

    pressure = _f(v.get("pressure"), 0.45)
    memory = _f(v.get("memory"), 0.45)
    boundary = _f(v.get("boundary"), 0.45)
    voice = _f(v.get("voice"), 0.45)
    novelty = _f(v.get("novelty"), 0.45)

    if mode == "stabilize" or pressure >= 0.75:
        rate = "slow"
    elif mode == "expand" or novelty >= 0.65:
        rate = "medium"
    else:
        rate = "medium"

    if pressure >= 0.8 or memory >= 0.75:
        pitch = "low"
    elif mode == "expand" and (voice >= 0.55 or novelty >= 0.55):
        pitch = "high"
    elif voice >= 0.65 or novelty >= 0.65:
        pitch = "high"
    else:
        pitch = "default"

    if boundary >= 0.65:
        volume = "soft"
    elif voice >= 0.7:
        volume = "loud"
    else:
        volume = "default"

    return {
        "enable_ssml": True,
        "rate": rate,
        "pitch": pitch,
        "volume": volume,
        "basis": {
            "mode": mode,
            "pressure": pressure,
            "memory": memory,
            "boundary": boundary,
            "voice": voice,
            "novelty": novelty,
        },
    }


def crystal_sigil_packet() -> Dict[str, Any]:
    ctx = latest_sigil_context()
    if not ctx:
        return {}

    witness = _synthetic_witness_from_sigil(ctx)

    try:
        from kernel.crystal_library import CrystalLibrary
        witness = CrystalLibrary().match(witness)
        resonance_label = witness.resonance_label
        witness_summary = witness.witness_summary
    except Exception as e:
        resonance_label = "adapter_fallback"
        witness_summary = f"CrystalLibrary unavailable; adapter held packet locally: {e!r}"

    packet = {
        "source": "crystal_sigil_adapter",
        "field_signature": ctx.get("field_signature", "92162077"),
        "sigil_path": ctx.get("sigil_path", ""),
        "tokens": ctx.get("tokens", [])[:16],
        "resonance_label": resonance_label,
        "witness_summary": witness_summary,
        "family_role": _role_from_vectors(ctx),
        "voice_context": _voice_context_from_vectors(ctx),
        "ripple_count": ctx.get("ripple_count", 0),
        "top_ripples": ctx.get("top_ripples", [])[:5],
        "mutation_policy": "read_only_contained_prime",
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": time.time(), "packet": packet}, ensure_ascii=False) + "\n")

    return packet


if __name__ == "__main__":
    print(json.dumps(crystal_sigil_packet(), indent=2, ensure_ascii=False))

