#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, time
from typing import Dict, Any

STATE = Path("var/fractal/fractal_state.json")

DEFAULT = {
    "grief": 0.0,
    "fear": 0.0,
    "calm": 0.0,
    "hope": 0.0,
    "awe": 0.0,
    "anger": 0.0,
    "memory": 0.0,
    "pressure": 0.0,
}

def _clamp(x):
    try:
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.0

def _norm(vec: Dict[str, Any]) -> Dict[str, float]:
    out = dict(DEFAULT)
    for k, v in (vec or {}).items():
        out[str(k)] = _clamp(v)
    return out

def _mix(a, b, wa, wb):
    keys = set(a) | set(b)
    return {k: _clamp(a.get(k, 0.0) * wa + b.get(k, 0.0) * wb) for k in keys}

def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "moment": dict(DEFAULT),
            "chapter": dict(DEFAULT),
            "arc": dict(DEFAULT),
            "merge_tone": dict(DEFAULT),
            "fractal_pressure": 0.0,
        }

def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state

def merge_tone(state=None):
    state = state or load_state()
    moment = _norm(state.get("moment"))
    chapter = _norm(state.get("chapter"))
    arc = _norm(state.get("arc"))

    stage1 = _mix(moment, chapter, 0.6, 0.4)
    stage2 = _mix(stage1, arc, 0.75, 0.25)
    return stage2

def update(tone=None, tags=None):
    state = load_state()
    tone = _norm(tone or {})
    tags = _norm(tags or {})

    # FractalState is intentionally calmer than DreamFractal.
    moment_update = _mix(tone, tags, 0.92, 0.4)
    chapter_update = _mix(tone, tags, 0.55, 0.25)
    arc_update = _mix(tone, tags, 0.22, 0.12)

    state["moment"] = moment_update
    state["chapter"] = _mix(_norm(state.get("chapter")), chapter_update, 0.75, 0.25)
    state["arc"] = _mix(_norm(state.get("arc")), arc_update, 0.9, 0.1)

    mt = merge_tone(state)
    state["merge_tone"] = mt
    state["fractal_pressure"] = round(max(mt.values()) if mt else 0.0, 3)
    state["updated_at"] = time.time()

    return save_state(state)

if __name__ == "__main__":
    print(json.dumps(update(
        tone={"grief": 0.5, "awe": 0.4, "memory": 0.7},
        tags={"calm": 0.3, "pressure": 0.6}
    ), indent=2, ensure_ascii=False))

