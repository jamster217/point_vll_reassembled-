from __future__ import annotations

import json
from typing import Any, Dict

from artifacts.analysis.route_comparison_artifact import compare_routes


def compare_routes_from_seed(raw_input: Any) -> Dict[str, Any]:
    """
    Bridge for VL seed execution.
    The current vl_seed_exec_stub passes the entire raw_input object here.
    Accepts:
      - dict payload
      - JSON string payload
    Expected shape:
      {
        "prompt": "...",
        "route_candidates": [...]
      }
    """
    payload: Dict[str, Any]

    if isinstance(raw_input, dict):
        payload = raw_input
    elif isinstance(raw_input, str):
        try:
            payload = json.loads(raw_input)
        except Exception:
            payload = {"prompt": raw_input, "route_candidates": []}
    else:
        payload = {"prompt": str(raw_input), "route_candidates": []}

    prompt = str(payload.get("prompt", "") or "")
    route_candidates = list(payload.get("route_candidates", []) or [])

    return compare_routes(prompt, route_candidates)

