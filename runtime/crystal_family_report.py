#!/usr/bin/env python3
"""
Le'Veon Crystal Family Report
Summarizes one shape family across all remembered turns.
"""

from __future__ import annotations

import sys
from collections import Counter
from typing import Any, Dict, List

from runtime.crystal_library_query import load_turns, sig_in
from runtime.shape_visualizer import render_shape_visual


NUMERIC_KEYS = ("pull", "bind", "resist", "release")


def _num(shape: Dict[str, Any], key: str) -> float:
    try:
        return float(shape.get(key, 0.0))
    except Exception:
        return 0.0


def _avg(vals: List[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def _family(row: Dict[str, Any]) -> str:
    return sig_in(row).split("|", 1)[0]


def family_rows(family: str) -> List[Dict[str, Any]]:
    rows = load_turns()
    return [r for r in rows if _family(r) == family]


def average_shape(rows: List[Dict[str, Any]], which: str = "shape_in") -> Dict[str, Any]:
    avg_shape: Dict[str, Any] = {}

    for key in NUMERIC_KEYS:
        avg_shape[key] = round(_avg([_num(r.get(which) or {}, key) for r in rows]), 3)

    times = Counter(str((r.get(which) or {}).get("time", "present")) for r in rows)
    avg_shape["time"] = times.most_common(1)[0][0] if times else "present"

    keyword_counts = Counter()
    for r in rows:
        keys = (r.get(which) or {}).get("keywords", [])
        if not isinstance(keys, list):
            keys = [str(keys)]
        for k in keys:
            keyword_counts[str(k)] += 1

    avg_shape["keywords"] = [k for k, _ in keyword_counts.most_common(8)]
    return avg_shape


def render_family_report(family: str) -> str:
    rows = family_rows(family)

    lines = [
        "CRYSTAL FAMILY REPORT",
        "---------------------",
        f"family : {family}",
        f"turns  : {len(rows)}",
    ]

    if not rows:
        lines.append("result : no remembered turns for this family")
        return "\n".join(lines)

    sig_counts = Counter(sig_in(r) for r in rows)

    avg_in = average_shape(rows, "shape_in")
    avg_out = average_shape(rows, "shape_out")

    avg_delta = {}
    for key in NUMERIC_KEYS:
        vals = []
        for r in rows:
            try:
                vals.append(float((r.get("shape_delta") or {}).get(key, 0.0)))
            except Exception:
                pass
        avg_delta[key] = round(_avg(vals), 3)

    lines.append("")
    lines.append("DOMINANT SIGNATURES")
    for sig, count in sig_counts.most_common(5):
        lines.append(f"- hits={count:<3} {sig}")

    lines.append("")
    lines.append("AVERAGE INPUT SHAPE")
    lines.append(str(avg_in))

    lines.append("")
    lines.append(render_shape_visual(avg_in, f"{family.upper()} AVG INPUT"))

    lines.append("")
    lines.append("AVERAGE OUTPUT SHAPE")
    lines.append(str(avg_out))

    lines.append("")
    lines.append(render_shape_visual(avg_out, f"{family.upper()} AVG OUTPUT"))

    lines.append("")
    lines.append("AVERAGE DELTA")
    for key in NUMERIC_KEYS:
        marker = "+" if avg_delta[key] > 0 else ""
        lines.append(f"{key:<8}: {marker}{avg_delta[key]:.3f}")

    lines.append("")
    lines.append("LATEST ECHOES")
    for r in rows[-6:][::-1]:
        ts = r.get("ts", "?")
        prompt = str(r.get("prompt", "")).replace("\n", " ")
        voice = str(r.get("savariel", "")).replace("\n", " ")

        if len(prompt) > 78:
            prompt = prompt[:75] + "..."
        if len(voice) > 100:
            voice = voice[:97] + "..."

        lines.append(f"- {ts}")
        lines.append(f"  prompt : {prompt}")
        lines.append(f"  voice  : {voice}")

    return "\n".join(lines)


def main():
    family = " ".join(sys.argv[1:]).strip() or "visual_runtime"
    print(render_family_report(family))


if __name__ == "__main__":
    main()

