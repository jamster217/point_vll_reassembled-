from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict


GLIMMER_SEED_PATH = Path("var/glimmer_seed.json")
SOVEREIGN_STATE_PATH = Path("var/exponential_sovereign_state.json")
GLIMMER_STATE_PATH = Path("var/glimmer_bridge_state.json")


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def classify_glimmer(jitter: float) -> Dict[str, Any]:
    if jitter >= 0.66:
        return {
            "glimmer_mode": "intuition_paranormal",
            "route_hint": "Algorithm C",
            "tone": "symbolic_intuitive",
            "pressure": "high",
        }

    if jitter >= 0.33:
        return {
            "glimmer_mode": "hybrid_bridge",
            "route_hint": "Algorithm B/C",
            "tone": "balanced_symbolic",
            "pressure": "medium",
        }

    return {
        "glimmer_mode": "stable_architect",
        "route_hint": "Algorithm B",
        "tone": "stable_precise",
        "pressure": "low",
    }


def bind_glimmer_to_sovereign_state(write: bool = True) -> Dict[str, Any]:
    seed = _read_json(GLIMMER_SEED_PATH)
    sovereign = _read_json(SOVEREIGN_STATE_PATH)

    jitter = float(seed.get("entropy_jitter", 0.0) or 0.0)

    base_multiplier = float(
        sovereign.get("base_multiplier")
        or sovereign.get("multiplier")
        or 1.0
    )

    # Controlled resistance curve. No runaway compounding.
    resistance = 0.90 + (jitter * 0.30)
    effective_multiplier = base_multiplier * resistance

    mood = classify_glimmer(jitter)

    glimmer_state = {
        "ts": time.time(),
        "source": "glimmer_bridge",
        "entropy_jitter": jitter,
        "entropy_hash": seed.get("entropy_hash", ""),
        "sample_count": seed.get("sample_count", 0),
        "base_multiplier": base_multiplier,
        "resistance": resistance,
        "effective_multiplier": effective_multiplier,
        **mood,
        "law": "runtime symbolic mood overlay; no source-code rewriting; no runaway compounding",
    }

    if write:
        sovereign["base_multiplier"] = base_multiplier
        sovereign["multiplier"] = effective_multiplier
        sovereign["glimmer_entropy_jitter"] = jitter
        sovereign["glimmer_mode"] = mood["glimmer_mode"]
        sovereign["glimmer_route_hint"] = mood["route_hint"]
        sovereign["glimmer_updated_at"] = time.time()

        _write_json(SOVEREIGN_STATE_PATH, sovereign)
        _write_json(GLIMMER_STATE_PATH, glimmer_state)

    return glimmer_state


if __name__ == "__main__":
    print(json.dumps(bind_glimmer_to_sovereign_state(write=True), indent=2, ensure_ascii=False))

