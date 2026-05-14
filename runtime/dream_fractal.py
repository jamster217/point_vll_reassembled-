#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json
from typing import Dict, Any

STATE = Path("var/dream_fractal_state.json")

DEFAULT_TONE = {
    "fear": 0.0,
    "surreal": 0.0,
    "calm": 0.0,
    "grief": 0.0,
    "wonder": 0.0,
}

def _clamp(x):
    try:
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.0

def _norm(vec: Dict[str, Any]) -> Dict[str, float]:
    out = dict(DEFAULT_TONE)
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
            "moment": dict(DEFAULT_TONE),
            "chapter": dict(DEFAULT_TONE),
            "arc": dict(DEFAULT_TONE),
            "projection": "soft_dream",
        }

def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state

def dream_tone(state=None):
    state = state or load_state()
    moment = _norm(state.get("moment"))
    chapter = _norm(state.get("chapter"))
    arc = _norm(state.get("arc"))
    stage1 = _mix(moment, chapter, 0.6, 0.4)
    return _mix(stage1, arc, 0.75, 0.25)

def project(tone):
    if tone.get("fear", 0.0) >= 0.6:
        return "night_fall"
    if tone.get("surreal", 0.0) >= 0.55:
        return "dream_haze"
    if tone.get("calm", 0.0) >= 0.55:
        return "lucid_drift"
    return "soft_dream"

def update(tone=None, tags=None):
    state = load_state()
    tone = _norm(tone or {})
    tags = _norm(tags or {})

    state["moment"] = _mix(tone, tags, 1.25, 1.3)
    state["chapter"] = _mix(_norm(state.get("chapter")), _mix(tone, tags, 0.55, 0.35), 0.75, 0.25)
    state["arc"] = _mix(_norm(state.get("arc")), _mix(tone, tags, 0.22, 0.12), 0.9, 0.1)

    dt = dream_tone(state)
    state["dream_tone"] = dt
    state["projection"] = project(dt)

    # Axis bridge: DREAM_TONE -> dream_pressure
    state["dream_pressure"] = round(max(dt.values()) if dt else 0.0, 3)
    return save_state(state)

if __name__ == "__main__":
    print(json.dumps(update({"surreal": 0.7, "calm": 0.3}, {"wonder": 0.5}), indent=2, ensure_ascii=False))

