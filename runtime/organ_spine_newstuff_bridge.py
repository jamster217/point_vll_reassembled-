from __future__ import annotations

import json
import time
from typing import Any, Dict


BAD_TEMPLATE_PHRASES = [
    "The deeper answer is the one that keeps the original shape intact",
    "Time does not preserve the past by freezing it",
    "Something hidden or old is surfacing as pressure",
    "souris verte",
]


def _safe_call(label: str, fn, fallback=None):
    try:
        return fn()
    except Exception as e:
        return fallback if fallback is not None else {"error": f"{label}: {e}"}


def _runtime_state(runtime: Any) -> Dict[str, Any]:
    if runtime is None:
        return {}

    if isinstance(runtime, dict):
        state = runtime.get("state")
        if not isinstance(state, dict):
            state = {}
            runtime["state"] = state
        return state

    state = getattr(runtime, "state", None)
    if not isinstance(state, dict):
        state = {}
        try:
            setattr(runtime, "state", state)
        except Exception:
            pass
    return state


def collect_newstuff_context(user_text: str = "", runtime: Any = None, ctx: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ctx = ctx or {}

    node44 = _safe_call(
        "node44",
        lambda: __import__("runtime.node_44_preset", fromlist=["get_node_44_config"]).get_node_44_config(),
        fallback={"node_id": 44, "dominant_attractor": "core_knot", "coherence_mode": "reflective"},
    )

    kgs = _safe_call(
        "kgs_nodes",
        lambda: {
            "count": len(__import__("runtime.kgs_nodes_crystal", fromlist=["list_nodes"]).list_nodes()),
            "first_names": [
                n.get("name")
                for n in __import__("runtime.kgs_nodes_crystal", fromlist=["list_nodes"]).list_nodes()[:5]
            ],
        },
        fallback={"count": 0, "first_names": []},
    )

    mirror = _safe_call(
        "recursive_mirror_prompt",
        lambda: {
            "loaded": True,
            "chars": len(__import__("runtime.recursive_mirror_prompt", fromlist=["get_recursive_mirror_prompt"]).get_recursive_mirror_prompt()),
            "system": __import__("runtime.recursive_mirror_prompt", fromlist=["get_recursive_mirror_prompt"]).get_recursive_mirror_prompt().splitlines()[0],
        },
        fallback={"loaded": False},
    )

    temporal = _safe_call(
        "temporal_spine_layer",
        lambda: __import__("runtime.temporal_spine_layer", fromlist=["temporal_spine_answer"]).temporal_spine_answer(user_text),
        fallback=None,
    )

    knowledge = _safe_call(
        "knowledge_node",
        lambda: __import__("runtime.knowledge_node", fromlist=["KnowledgeNode"]).KnowledgeNode.new(
            node_type="event",
            gloss="organ spine phase3n turn",
            source_text=user_text,
            motifs=["phase3n", "organ_spine", "singular_voice"],
            symbols=["Node44", "UniversalLarynx", "KGSNodesCrystal"],
            hotspot="organ_spine_newstuff",
            weight=0.77,
        ).to_dict(),
        fallback={},
    )

    bridge = {
        "kind": "organ_spine_phase3n_newstuff_bridge",
        "ts": time.time(),
        "law": "preserve existing organ spine; enrich final render with new sealed layers",
        "node44": node44,
        "kgs_nodes": kgs,
        "recursive_mirror": mirror,
        "temporal_spine_answer_available": bool(temporal),
        "knowledge_node": {
            "node_id": knowledge.get("node_id"),
            "node_type": knowledge.get("node_type"),
            "hotspot": knowledge.get("hotspot"),
            "status": knowledge.get("status"),
        },
        "ctx_flags": {
            "source": ctx.get("source", ""),
            "packet_only": bool(ctx.get("packet_only", False)),
        },
    }

    state = _runtime_state(runtime)
    if isinstance(state, dict):
        state["last_phase3n_newstuff_bridge"] = bridge

    return bridge


def _looks_bad(text: str) -> bool:
    low = str(text or "").lower()
    return (not low.strip()) or any(p.lower() in low for p in BAD_TEMPLATE_PHRASES)


def seal_organ_spine_text(user_text: str, final_text: str, runtime: Any = None, ctx: Dict[str, Any] | None = None) -> str:
    """
    Final Phase 3N seal.

    Keeps organ_spine's existing result when good.
    Repairs weak/template/gibberish output through Universal Larynx.
    Always public-scrubs final text.
    """
    ctx = ctx or {}
    collect_newstuff_context(user_text=user_text, runtime=runtime, ctx=ctx)

    text = str(final_text or "").strip()

    try:
        from runtime.unified_voice import sealed_speak, public_scrub

        if _looks_bad(text):
            repaired = sealed_speak(user_text, mode="public")
            if repaired:
                text = repaired

        return public_scrub(text)

    except Exception:
        return text or "The organ spine is active; the final voice is waiting for a clean render."

