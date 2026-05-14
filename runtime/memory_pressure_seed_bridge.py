from __future__ import annotations

import json
from typing import Any, Dict

from artifacts.analysis.memory_pressure_sim_artifact import simulate_memory_pressure


def simulate_memory_pressure_from_seed(raw_input: Any) -> Dict[str, Any]:
    if isinstance(raw_input, dict):
        prompt = str(raw_input.get("prompt", "") or "")
    elif isinstance(raw_input, str):
        try:
            payload = json.loads(raw_input)
            prompt = str(payload.get("prompt", "") or "")
        except Exception:
            prompt = raw_input
    else:
        prompt = str(raw_input)

    return simulate_memory_pressure(prompt)

