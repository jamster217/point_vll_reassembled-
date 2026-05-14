from __future__ import annotations

import json
import time
from pathlib import Path
from collections import Counter
from typing import Dict, Any, List

ROOT = Path.home() / "point_vll_reassembled"

STATE_PATH = ROOT / "var/observability/continuity_pressure_memory.json"

MAX_HISTORY = 12


def load_state() -> Dict[str, Any]:

    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {
            "history": []
        }


def save_state(state: Dict[str, Any]) -> None:

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def update_route_memory(selected_route: str) -> Dict[str, Any]:

    state = load_state()

    history: List[str] = state.get("history", [])

    history.append(selected_route)

    history = history[-MAX_HISTORY:]

    counts = Counter(history)

    dominant_route = max(
        counts,
        key=counts.get
    )

    continuity_bias = {}

    total = max(len(history), 1)

    for route, count in counts.items():

        continuity_bias[route] = round(
            count / total,
            4
        )

    state = {
        "ts": time.time(),
        "history": history,
        "dominant_route": dominant_route,
        "continuity_bias": continuity_bias,
        "law": "temporal_route_continuity_v1"
    }

    save_state(state)

    return state


if __name__ == "__main__":

    tests = [
        "ordinary_surface",
        "ordinary_surface",
        "build_surface",
        "ordinary_surface",
        "mirror_surface",
        "ordinary_surface",
    ]

    result = None

    for t in tests:
        result = update_route_memory(t)

    print(json.dumps(result, indent=2))

