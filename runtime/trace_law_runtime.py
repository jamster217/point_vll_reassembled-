from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


BANK_PATH = Path("runtime/generated/trace_law_bank.json")


def _load_bank() -> Dict[str, Any]:
    try:
        return json.loads(BANK_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _top_motifs(bank: Dict[str, Any], limit: int = 5):
    motifs = bank.get("motif_bias", []) or []
    if not motifs:
        return []

    max_weight = max((int(x[1] or 0) for x in motifs), default=1) or 1

    out = []
    for name, weight in motifs[:limit]:
        out.append({
            "motif": name,
            "weight": int(weight or 0),
            "normalized": round((int(weight or 0) / max_weight), 4),
        })
    return out


def choose_trace_state(shape: Dict[str, Any]) -> Dict[str, Any]:
    bank = _load_bank()
    state_laws = bank.get("state_laws", {}) or {}
    mode_laws = bank.get("mode_laws", {}) or {}

    intent = str(shape.get("intent", "open"))
    vectors = shape.get("vectors", {}) or {}

    pressure = float(vectors.get("pressure", shape.get("pressure", 0.45)) or 0.45)
    release = float(vectors.get("release", shape.get("release", 0.45)) or 0.45)
    novelty = float(vectors.get("novelty", shape.get("novelty", 0.45)) or 0.45)
    memory = float(vectors.get("memory", shape.get("memory", 0.45)) or 0.45)

    # Trace law selection. This does not generate content.
    # It only tells the live renderer whether to observe, stabilize, or expand.
    if intent == "presence_surface":
        state = "adaptive"
        mode = "observe"
    elif pressure >= 0.66 and release <= 0.45:
        state = "adaptive"
        mode = "stabilize"
    elif intent in {"poetic_surface", "relationship_surface", "build_surface"}:
        state = "stable"
        mode = "expand"
    elif intent in {"field_surface", "emotional_surface"}:
        state = "adaptive" if pressure > 0.6 or memory > 0.6 else "stable"
        mode = "stabilize"
    elif novelty >= 0.68 and pressure < 0.7:
        state = "stable"
        mode = "expand"
    else:
        state = "adaptive"
        mode = "observe"

    return {
        "trace_source": "replication_trace_4200",
        "selected_state": state,
        "selected_mode": mode,
        "state_law": state_laws.get(state, {}),
        "mode_law": mode_laws.get(mode, ""),
        "motif_bias_top": _top_motifs(bank),
        "renderer_warning": (bank.get("renderer_warning") or {}).get(
            "law",
            "use trace as state law only, not final text",
        ),
    }


def enrich_shape(shape: Dict[str, Any]) -> Dict[str, Any]:
    shape = dict(shape or {})
    shape["trace_law"] = choose_trace_state(shape)
    return shape

