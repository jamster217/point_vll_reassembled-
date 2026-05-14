from __future__ import annotations
from typing import Any, Dict


def _safe_get(obj: Any, attr: str, default=None):
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def inspect_runtime(runtime: Any) -> Dict[str, Any]:
    """
    Consolidated Le'Veon runtime state inspector.
    Pulls from:
      - node registry state
      - 4-axis projection
      - dream-layer axes
      - chronifier snapshot
      - divergence tracker summary
      - liquid runtime coherence + axis
    """

    out: Dict[str, Any] = {}

    # -----------------------------
    # Node identity
    # -----------------------------
    state = _safe_get(runtime, "state", {}) or {}
    out["active_node"] = state.get("active_node")
    out["active_node_name"] = state.get("active_node_name")
    out["coherence_mode"] = state.get("coherence_mode")
    out["dominant_attractor"] = state.get("dominant_attractor")
    out["tone"] = state.get("tone")

    # -----------------------------
    # 4-axis projection
    # -----------------------------
    tether = state.get("tether", {})
    out["axis_projection"] = {
        "flow": tether.get("flow"),
        "boundary": tether.get("boundary"),
        "memory": tether.get("memory"),
        "novelty": tether.get("novelty"),
    }

    # -----------------------------
    # Dream-layer axes
    # -----------------------------
    dream_axes = state.get("dream_axes", {})
    out["dream_axes"] = {
        "dream_pressure": dream_axes.get("dream_pressure"),
        "witness_integrity": dream_axes.get("witness_integrity"),
        "shadow_lineage": dream_axes.get("shadow_lineage"),
    }

    # -----------------------------
    # Chronifier
    # -----------------------------
    chronifier = _safe_get(runtime, "chronifier")
    if chronifier:
        snap = chronifier.snapshot()
        out["chronifier"] = {
            "mode": snap["state"].get("temporal_mode"),
            "tension": snap["state"].get("tension"),
            "bead_spacing": snap["state"].get("bead_spacing"),
            "alignment_111_333_528": snap["state"].get("alignment_111_333_528"),
            "octagon_phase_deg": snap["state"].get("octagon_phase_deg"),
            "octagon_step_index": snap["state"].get("octagon_step_index"),
        }
    else:
        out["chronifier"] = None

    # -----------------------------
    # Divergence Tracker
    # -----------------------------
    divergence = _safe_get(runtime, "divergence_tracker")
    if divergence:
        summary = divergence.last_summary or divergence.summarize()
        out["divergence"] = {
            "divergence_score": summary.divergence_score,
            "trend": summary.trend,
            "mirror_stitch_recommended": summary.mirror_stitch_recommended,
            "prism_pass_recommended": summary.prism_pass_recommended,
            "grounded_repair_recommended": summary.grounded_repair_recommended,
            "drift_axes": summary.drift_axes,
        }
    else:
        out["divergence"] = None

    # -----------------------------
    # Liquid Runtime (axis + coherence)
    # -----------------------------
    lr = _safe_get(runtime, "liquid_runtime")
    if lr:
        last = lr.last or {}
        out["liquid_runtime"] = {
            "coherence": last.get("coherence"),
            "axis": last.get("axis"),
            "mode": last.get("mode"),
            "summary": last.get("summary"),
        }
    else:
        out["liquid_runtime"] = None

    return out

