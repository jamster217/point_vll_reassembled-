from __future__ import annotations

import json
from typing import Any, Dict

from artifacts.analysis.hotspot_transition_map_artifact import map_hotspot_transitions


def map_hotspot_transitions_from_seed(raw_input: Any) -> Dict[str, Any]:
    if isinstance(raw_input, dict):
        trace = raw_input.get("hotspot_trace", [])
    elif isinstance(raw_input, str):
        try:
            payload = json.loads(raw_input)
            trace = payload.get("hotspot_trace", [])
        except Exception:
            trace = raw_input
    else:
        trace = []

    return map_hotspot_transitions(trace)

