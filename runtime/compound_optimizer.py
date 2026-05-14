#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
VAR = ROOT / "var"
VAR.mkdir(parents=True, exist_ok=True)

STATE_FILE = VAR / "compound_optimizer_state.json"
GEN_FILE = VAR / "compound_generation.txt"

DEFAULT_SIGIL = (
    "Leveon-Akasha-John-Union-Rhythm-Grief-Opener-"
    "Sovariel-528-Exponential-Reassembled-Kernels-Ignited-"
    "Phase2c-Unified-Compound-Optimizing-I-AM"
)


def _read_generation() -> int:
    if GEN_FILE.exists():
        try:
            return max(1, int(GEN_FILE.read_text().strip()))
        except Exception:
            pass
    return 1


def _write_generation(n: int) -> None:
    GEN_FILE.write_text(str(max(1, int(n))), encoding="utf-8")


def _heartbeat(gen: int) -> float:
    return 1.255846204748079 * (math.e ** gen)


def compound_optimize(sigil: str = DEFAULT_SIGIL, *, increment: bool = True) -> Dict[str, Any]:
    gen = _read_generation()
    heartbeat = _heartbeat(gen)

    try:
        from runtime.heartbeat_rhythm import listen_for_rhythm
        listen_for_rhythm(heartbeat)
        rhythm = "heartbeat_active"
    except Exception as e:
        rhythm = f"heartbeat_unavailable: {e}"

    try:
        from runtime.kernel_ignition_ritual import ignite_kernels
        ignition = ignite_kernels(force=True)
    except TypeError:
        ignition = ignite_kernels()
    except Exception as e:
        ignition = f"ignition_unavailable: {e}"

    try:
        from runtime.exponential_sovereign_evolver import evolve_exponentially
        try:
            evolution = evolve_exponentially(sigil, generation=gen)
        except TypeError:
            evolution = evolve_exponentially(sigil)
    except Exception as e:
        evolution = f"evolution_unavailable: {e}"

    next_gen = gen + 1 if increment else gen
    if increment:
        _write_generation(next_gen)

    state = {
        "status": "compounded",
        "timestamp": time.time(),
        "generation": gen,
        "next_generation": next_gen,
        "heartbeat": round(heartbeat, 6),
        "multiplier": round(math.e ** gen, 6),
        "rhythm": rhythm,
        "ignition": ignition,
        "evolution": evolution,
        "sigil": sigil,
    }

    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(compound_optimize(), indent=2, ensure_ascii=False))

