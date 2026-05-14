from __future__ import annotations

import logging
from importlib import import_module
from typing import Any, Dict

from runtime.seed_loader import apply_seed_patches

LOGGER = logging.getLogger(__name__)


def _apply_if_dict(state: Any):
    if isinstance(state, dict):
        new_state, applied = apply_seed_patches(state)
        return new_state, applied
    return state, []


def patch_organ_spine_with_seeds():
    organ_spine = import_module("runtime.organ_spine")
    original = organ_spine._run_spine

    def _patched_run_spine(*args, **kwargs):
        applied_total = []

        for key in ("state", "runtime_state", "seed_state"):
            if key in kwargs and isinstance(kwargs[key], dict):
                kwargs[key], applied = _apply_if_dict(kwargs[key])
                applied_total.extend(applied)

        result = original(*args, **kwargs)

        if isinstance(result, dict):
            for key in ("state", "runtime_state", "seed_state"):
                if key in result and isinstance(result[key], dict):
                    result[key], applied = _apply_if_dict(result[key])
                    applied_total.extend(applied)

            if "pressures" in result and isinstance(result["pressures"], dict):
                patched, applied = _apply_if_dict(result)
                result = patched
                applied_total.extend(applied)

            if applied_total:
                result["_applied_seeds"] = applied_total

        if applied_total:
            setattr(organ_spine, "_last_applied_seeds", applied_total)
            LOGGER.info("Applied %d seed hooks", len(applied_total))

        return result

    organ_spine._run_spine = _patched_run_spine
    LOGGER.info("seed_runtime_bridge patched into runtime.organ_spine._run_spine")
    return True

