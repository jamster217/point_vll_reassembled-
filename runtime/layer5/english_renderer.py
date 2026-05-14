from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
SIM_PATH = ROOT / "simulations" / "meaning_pipeline_sim.py"


def _load_sim_layer5():
    if not SIM_PATH.exists():
        return None

    try:
        spec = importlib.util.spec_from_file_location("meaning_pipeline_sim_layer5", SIM_PATH)
        if spec is None or spec.loader is None:
            return None

        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = getattr(mod, "layer_5_render_english", None)
        return fn if callable(fn) else None
    except Exception:
        return None


def _fallback_layer5(skel: Dict[str, Any]) -> str:
    subject = (
        skel.get("subject")
        or skel.get("term")
        or skel.get("focus")
        or skel.get("name")
        or "This pattern"
    )

    typ = skel.get("type") or skel.get("kind") or ""
    role = skel.get("role") or skel.get("motion") or ""
    relation = skel.get("relation") or skel.get("target") or ""

    subject = str(subject).strip().capitalize()

    if typ and role:
        return f"{subject} carries {typ} through {role}."
    if typ:
        return f"{subject} functions as {typ}."
    if relation:
        return f"{subject} is related to {relation}."
    if role:
        return f"{subject} carries {role}."

    return f"{subject} is the main meaning being held."


def render_layer5_english(skel: Dict[str, Any]) -> str:
    """
    Runtime compatibility wrapper for the old Layer 5 English renderer.

    Current build fact:
    - no runtime/layer5 folder originally existed
    - Layer 5 lives as simulations.meaning_pipeline_sim.layer_5_render_english

    This wrapper lets newer runtime code call Layer 5 without depending on the
    simulation path directly.
    """
    if not isinstance(skel, dict):
        skel = {"subject": str(skel)}

    fn = _load_sim_layer5()
    if callable(fn):
        try:
            out = fn(skel)
            if isinstance(out, str) and out.strip():
                text = " ".join(out.strip().split())
                bad = {
                    "the current structure could not yet be rendered cleanly.",
                    "current structure could not yet be rendered cleanly.",
                    "could not yet be rendered cleanly.",
                }
                if text.lower() not in bad:
                    return text
        except Exception:
            pass

    return _fallback_layer5(skel)


def render_public_surface(skel: Dict[str, Any]) -> str:
    """
    Cleaner public surface wrapper.
    Keeps Layer 5 available, but softens obvious scaffold phrasing.
    """
    text = render_layer5_english(skel)

    text = text.replace("is being treated as", "appears as")
    text = text.replace("in the current structure", "inside the current pattern")
    text = text.replace("in the current meaning structure", "inside the current pattern")

    return text

# --------------------------------------------------------------------
# V14.1 Absolute Veracity Protocol
# Layer 5 renderer wrapper: prevent doorway/mechanism template escape.
# --------------------------------------------------------------------
try:
    if "render_english" in globals():
        _v141_original_render_english = render_english

        def render_english(*args, **kwargs):
            out = _v141_original_render_english(*args, **kwargs)
            prompt = str(args[0]) if args else str(kwargs.get("prompt", ""))
            try:
                from runtime.veracity_public_gate_v141 import v141_public_gate
                gated, meta, replaced = v141_public_gate(
                    prompt,
                    out,
                    source="runtime.layer5.english_renderer.render_english",
                )
                return gated
            except Exception:
                return out

    if "layer_5_render_english" in globals():
        _v141_original_layer_5_render_english = layer_5_render_english

        def layer_5_render_english(*args, **kwargs):
            out = _v141_original_layer_5_render_english(*args, **kwargs)
            prompt = str(args[0]) if args else str(kwargs.get("prompt", ""))
            try:
                from runtime.veracity_public_gate_v141 import v141_public_gate
                gated, meta, replaced = v141_public_gate(
                    prompt,
                    out,
                    source="runtime.layer5.english_renderer.layer_5_render_english",
                )
                return gated
            except Exception:
                return out

except Exception as _v141_layer5_wrap_error:
    V141_LAYER5_WRAP_ERROR = repr(_v141_layer5_wrap_error)

