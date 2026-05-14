#!/usr/bin/env python3
"""
Le'Veon Shape Visualizer
Turns runtime shape dictionaries into a compact ASCII visual map.

Expected shape keys:
pull, bind, resist, release, flow, time, keywords
All keys are optional.
"""

from __future__ import annotations

from typing import Any, Dict, List


def _bar(value: float, width: int = 12) -> str:
    try:
        v = max(0.0, min(1.0, float(value)))
    except Exception:
        v = 0.0
    filled = round(v * width)
    return "█" * filled + "░" * (width - filled)


def _num(shape: Dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(shape.get(key, default))
    except Exception:
        return default


def render_shape_visual(shape: Dict[str, Any], title: str = "SHAPE VISUAL MAP") -> str:
    pull = _num(shape, "pull", _num(shape, "flow", 0.0))
    bind = _num(shape, "bind", 0.0)
    resist = _num(shape, "resist", 0.0)
    release = _num(shape, "release", 0.0)

    time = shape.get("time", "present")
    keywords = shape.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = [str(keywords)]

    flow_arrow = "↑" if pull >= 0.66 else "↗" if pull >= 0.33 else "→"
    release_arrow = "↗" if release >= 0.5 else "·"
    bind_ring = "◎" if bind >= 0.66 else "○" if bind >= 0.33 else "·"
    resist_mark = "⇄" if resist >= 0.5 else "—"

    keyword_line = ", ".join(str(k) for k in keywords[:8]) if keywords else "none"

    visual = f"""
╔══════════════════════════════════════╗
║ {title:<36} ║
╚══════════════════════════════════════╝

              {flow_arrow}
              │
        FLOW / PULL
        [{_bar(pull)}] {pull:.2f}
              │

        {bind_ring}─── CORE FIELD ───{release_arrow}
              │
              │
        BIND / HOLD
        [{_bar(bind)}] {bind:.2f}

        RESIST / FRICTION {resist_mark}
        [{_bar(resist)}] {resist:.2f}

        RELEASE / OPENING
        [{_bar(release)}] {release:.2f}

        TIME: {time}
        KEYS: {keyword_line}
""".strip()

    return visual


if __name__ == "__main__":
    demo = {
        "pull": 0.92,
        "bind": 0.88,
        "resist": 0.0,
        "release": 0.1,
        "time": "past->present",
        "keywords": ["ache", "black hole", "chest", "heavy", "hollow", "void"],
    }
    print(render_shape_visual(demo))

