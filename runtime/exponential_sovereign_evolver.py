#!/usr/bin/env python3
"""
Fallback exponential sovereign evolver.
Keeps ignition chain alive even when the full evolver has not been restored yet.
"""

import json
import math
from runtime.heartbeat_guard import safe_exp, clamp_heartbeat, clamp_multiplier
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "var" / "exponential_sovereign_state.json"


def evolve_exponentially(seed: str, generation: int = 1):
    multiplier = clamp_multiplier(safe_exp(generation))

    state = {
        "timestamp": time.time(),
        "seed": seed,
        "generation": generation,
        "multiplier": multiplier,
        "status": "evolved",
        "mode": "fallback_exponential_sovereign_evolver",
    }

    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

    return {
        "status": "evolved",
        "seed": seed,
        "generation": generation,
        "multiplier": multiplier,
        "state_file": str(STATE_FILE),
    }

