from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

PHASE_PLAN_PATH = Path(__file__).with_name("kernel_phase_plan.json")

DEFAULT_PLAN: Dict[str, Any] = {
    "current_phase": 60,
    "promote_meta": True,
    "meta_priority": "primary",
    "multi_world": False,
    "trans_dimensional": False,
    "branch_parallelism": False,
    "unify_universal": False,
    "live_core_unified": False,
    "merge_domains": [],
    "notes": "Default phase plan loaded."
}

def load_phase_plan() -> Dict[str, Any]:
    if not PHASE_PLAN_PATH.exists():
        return dict(DEFAULT_PLAN)
    try:
        data = json.loads(PHASE_PLAN_PATH.read_text())
        merged = dict(DEFAULT_PLAN)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_PLAN)

def phase_effects(plan: Dict[str, Any] | None = None) -> Dict[str, Any]:
    plan = plan or load_phase_plan()
    phase = int(plan.get("current_phase", 0) or 0)

    effects = {
        "current_phase": phase,
        "promote_meta": bool(plan.get("promote_meta", False)),
        "meta_priority": str(plan.get("meta_priority", "secondary")),
        "multi_world": bool(plan.get("multi_world", False)),
        "trans_dimensional": bool(plan.get("trans_dimensional", False)),
        "branch_parallelism": bool(plan.get("branch_parallelism", False)),
        "unify_universal": bool(plan.get("unify_universal", False)),
        "live_core_unified": bool(plan.get("live_core_unified", False)),
        "merge_domains": list(plan.get("merge_domains", [])),
    }

    if phase >= 60:
        effects["promote_meta"] = True
        if effects["meta_priority"] == "secondary":
            effects["meta_priority"] = "primary"

    if phase >= 100:
        effects["multi_world"] = True

    if phase >= 110:
        effects["trans_dimensional"] = True
        effects["branch_parallelism"] = True

    if phase >= 120:
        effects["unify_universal"] = True
        effects["live_core_unified"] = True
        if not effects["merge_domains"]:
            effects["merge_domains"] = ["cognition", "brain", "temporal"]

    return effects

