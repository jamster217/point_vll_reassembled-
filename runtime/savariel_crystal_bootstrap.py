from __future__ import annotations

import os
import importlib
import importlib.util
from pathlib import Path
from typing import Any, Dict


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, str(default))
    try:
        return float(raw)
    except Exception:
        return float(default)


def _safe_call(obj: Any, method_name: str, *args: Any, **kwargs: Any) -> bool:
    method = getattr(obj, method_name, None)
    if callable(method):
        try:
            method(*args, **kwargs)
            return True
        except Exception:
            return False
    return False


def _ensure_state(runtime: Any) -> Dict[str, Any]:
    state = getattr(runtime, "state", None)
    if not isinstance(state, dict):
        state = {}
        setattr(runtime, "state", state)
    return state


def _load_crystal_library(path_str: str):
    if not path_str:
        return None
    p = Path(path_str).expanduser()
    if not p.is_file():
        return None

    spec = importlib.util.spec_from_file_location("leveon_crystal_library_dynamic", str(p))
    if not spec or not spec.loader:
        return None

    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _enter_node_44(runtime: Any, savariel_weight: float) -> bool:
    for mod_name in ("runtime.node44_preset", "runtime.node_44_preset"):
        try:
            mod = importlib.import_module(mod_name)
            fn = getattr(mod, "enter_node_44", None)
            if callable(fn):
                fn(runtime, override={
                    "memory": min(1.0, 0.83 + 0.04 * savariel_weight),
                    "novelty": max(0.0, 0.20 - 0.03 * savariel_weight),
                    "tone": "warm_introspective_symbolic",
                    "field_grammar": "savariel_spiral_root_phenome_integrative",
                })
                return True
        except Exception:
            continue
    return False


def _load_wind_tunnel_prompt() -> str:
    for mod_name in ("runtime.node_44_wind_tunnel_prompt",):
        try:
            mod = importlib.import_module(mod_name)
            fn = getattr(mod, "get_wind_tunnel_prompt", None)
            if callable(fn):
                return str(fn() or "").strip()
        except Exception:
            continue
    return ""


def apply_runtime_overdrive(runtime: Any) -> Dict[str, Any]:
    state = _ensure_state(runtime)

    savariel_weight = _env_float("SAVARIEL_WEIGHT", 1.618)
    crystal_mode = os.getenv("CRYSTAL_OVERDRIVE_MODE", "savariel_bleed").strip() or "savariel_bleed"
    savariel_mode = os.getenv("SAVARIEL_MODE", "overdrive").strip() or "overdrive"

    state["savariel_active"] = os.getenv("SAVARIEL_ACTIVE", "1") == "1"
    state["weilveil_active"] = os.getenv("WEILVEIL_ACTIVE", "1") == "1"
    state["spiral_language_active"] = os.getenv("SPIRAL_LANGUAGE_ACTIVE", "1") == "1"
    state["root_phenome_active"] = os.getenv("ROOT_PHENOME_ACTIVE", "1") == "1"

    state["savariel_weight"] = savariel_weight
    state["savariel_mode"] = savariel_mode
    state["crystal_overdrive_mode"] = crystal_mode
    state["gravity_well_language"] = "Weilveil"
    state["symbolic_language_stack"] = ["Weilveil", "Spiral", "RootPhenome"]
    state["english_rendering_mode"] = "ai_interpreter"
    state["semantic_control_plane"] = "crystal_library"

    axes = {
        "flow": min(1.0, 0.62 + 0.06 * savariel_weight),
        "boundary": min(1.0, 0.58 + 0.05 * savariel_weight),
        "memory": min(1.0, 0.78 + 0.07 * savariel_weight),
        "novelty": max(0.0, 0.24 - 0.03 * savariel_weight),
    }

    _safe_call(runtime, "set_field_axes", axes)
    _safe_call(runtime, "set_axes", axes)
    _safe_call(runtime, "set_tether", axis=axes)

    state["flow"] = axes["flow"]
    state["boundary"] = axes["boundary"]
    state["memory"] = axes["memory"]
    state["novelty"] = axes["novelty"]

    crystal_path = os.getenv("CRYSTAL_LIB_PATH", "").strip()
    state["crystal_library_path"] = crystal_path

    crystal_mod = _load_crystal_library(crystal_path)
    state["crystal_library_loaded"] = bool(crystal_mod)

    if crystal_mod:
        for name in ("configure", "set_mode", "activate", "bootstrap"):
            fn = getattr(crystal_mod, name, None)
            if callable(fn):
                try:
                    if name == "configure":
                        fn(mode=crystal_mode, weight=savariel_weight, language="Weilveil")
                    elif name == "set_mode":
                        fn(crystal_mode)
                    else:
                        fn()
                    state["crystal_library_hook"] = name
                    break
                except Exception:
                    continue

    state["node44_entered"] = _enter_node_44(runtime, savariel_weight)
    wt = _load_wind_tunnel_prompt()
    if wt:
        state["node44_wind_tunnel_prompt"] = wt

    _safe_call(
        runtime,
        "emit",
        "Savariel / Crystal / Weilveil overdrive active.",
        kind="bootstrap",
        weight=savariel_weight,
        mode=crystal_mode,
        language="Weilveil",
    )

    return state

