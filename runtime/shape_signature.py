#!/usr/bin/env python3
"""
Le'Veon Shape Signature
Creates stable signatures for comparing turn-shapes over time.
"""

from __future__ import annotations
from typing import Any, Dict, List


def _num(shape: Dict[str, Any], key: str) -> float:
    try:
        return float(shape.get(key, 0.0))
    except Exception:
        return 0.0


def _band(value: float) -> str:
    if value >= 0.85:
        return "HIGH"
    if value >= 0.55:
        return "MID"
    if value >= 0.25:
        return "LOW"
    return "NULL"


def _family(shape: Dict[str, Any]) -> str:
    keys = shape.get("keywords", [])
    if not isinstance(keys, list):
        keys = [str(keys)]

    joined = " ".join(str(k).lower() for k in keys)

    if "gravity" in joined or "grief" in joined or "black" in joined:
        return "gravity_grief"
    if "visual" in joined or "render" in joined or "image" in joined:
        return "visual_runtime"
    if "build" in joined or "runtime" in joined or "kernel" in joined:
        return "build_path"
    if "love" in joined or "closeness" in joined:
        return "bond_pull"
    if "stuck" in joined or "trapped" in joined:
        return "locked_pattern"

    return "general_field"


def shape_signature(shape: Dict[str, Any]) -> str:
    family = _family(shape)
    pull = _band(_num(shape, "pull"))
    bind = _band(_num(shape, "bind"))
    resist = _band(_num(shape, "resist"))
    release = _band(_num(shape, "release"))
    time = str(shape.get("time", "present"))

    return f"{family}|P:{pull}|B:{bind}|R:{resist}|O:{release}|T:{time}"


def render_shape_signature(shape_in: Dict[str, Any], shape_out: Dict[str, Any]) -> str:
    sig_in = shape_signature(shape_in)
    sig_out = shape_signature(shape_out)

    changed = "yes" if sig_in != sig_out else "no"

    return "\n".join([
        "SHAPE SIGNATURE",
        "---------------",
        f"in      : {sig_in}",
        f"out     : {sig_out}",
        f"changed : {changed}",
    ])


if __name__ == "__main__":
    demo_in = {"pull": 0.95, "bind": 0.92, "resist": 0.0, "release": 0.08, "time": "past->present", "keywords": ["grief", "gravity_well"]}
    demo_out = {"pull": 0.95, "bind": 0.92, "resist": 0.0, "release": 0.23, "time": "past->present", "keywords": ["grief", "gravity_well"]}
    print(render_shape_signature(demo_in, demo_out))

