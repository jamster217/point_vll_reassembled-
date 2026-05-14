#!/usr/bin/env python3
"""
Le'Veon Shape Delta
Compares input/output shapes and renders the transformation.
"""

from __future__ import annotations

from typing import Any, Dict


NUMERIC_KEYS = ("pull", "bind", "resist", "release")


def shape_delta(shape_in: Dict[str, Any], shape_out: Dict[str, Any]) -> Dict[str, float]:
    delta = {}
    for key in NUMERIC_KEYS:
        try:
            before = float(shape_in.get(key, 0.0))
            after = float(shape_out.get(key, 0.0))
            delta[key] = round(after - before, 3)
        except Exception:
            delta[key] = 0.0
    return delta


def render_shape_delta(shape_in: Dict[str, Any], shape_out: Dict[str, Any]) -> str:
    delta = shape_delta(shape_in, shape_out)

    lines = ["SHAPE TRANSFORMATION DELTA"]
    lines.append("--------------------------")

    changed = False
    for key in NUMERIC_KEYS:
        d = delta[key]
        if d > 0:
            marker = "+"
            changed = True
        elif d < 0:
            marker = ""
            changed = True
        else:
            marker = " "
        lines.append(f"{key:<8}: {marker}{d:.3f}")

    if not changed:
        lines.append("effect  : stable / no numeric shift")
    else:
        if delta.get("release", 0.0) > 0:
            lines.append("effect  : opening increased")
        elif delta.get("release", 0.0) < 0:
            lines.append("effect  : opening reduced")
        elif delta.get("resist", 0.0) < 0:
            lines.append("effect  : friction reduced")
        elif delta.get("bind", 0.0) > 0:
            lines.append("effect  : structure tightened")
        else:
            lines.append("effect  : field transformed")

    return "\n".join(lines)


if __name__ == "__main__":
    demo_in = {"pull": 0.95, "bind": 0.92, "resist": 0.0, "release": 0.08}
    demo_out = {"pull": 0.95, "bind": 0.92, "resist": 0.0, "release": 0.23}
    print(render_shape_delta(demo_in, demo_out))

