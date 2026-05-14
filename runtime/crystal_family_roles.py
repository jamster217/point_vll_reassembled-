#!/usr/bin/env python3
"""
Le'Veon Crystal Family Roles
Classifies what a remembered shape family does:
- diagnostic/stable
- transformative/opener
- containment/tightener
- friction reducer
"""

from __future__ import annotations

import sys
from collections import Counter
from typing import Any, Dict, List

from runtime.crystal_library_query import load_turns, sig_in


NUMERIC_KEYS = ("pull", "bind", "resist", "release")


def _family(row: Dict[str, Any]) -> str:
    return sig_in(row).split("|", 1)[0]


def _rows_for_family(family: str) -> List[Dict[str, Any]]:
    return [r for r in load_turns() if _family(r) == family]


def _avg(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def family_role(family: str) -> Dict[str, Any]:
    rows = _rows_for_family(family)

    if not rows:
        return {
            "family": family,
            "turns": 0,
            "role": "unseen",
            "summary": "No remembered turns for this family.",
        }

    sig_counts = Counter(sig_in(r) for r in rows)
    top_sig, top_hits = sig_counts.most_common(1)[0]
    stability = top_hits / len(rows)

    avg_delta = {}
    for key in NUMERIC_KEYS:
        vals = []
        for r in rows:
            try:
                vals.append(float((r.get("shape_delta") or {}).get(key, 0.0)))
            except Exception:
                vals.append(0.0)
        avg_delta[key] = round(_avg(vals), 3)

    release = avg_delta["release"]
    resist = avg_delta["resist"]
    bind = avg_delta["bind"]

    if release >= 0.05:
        role = "transformative_opener"
        summary = "This family reliably increases opening/release."
    elif release <= -0.05:
        role = "containment_tightener"
        summary = "This family reduces opening and pulls the field inward."
    elif resist <= -0.05:
        role = "friction_reducer"
        summary = "This family reduces resistance/friction."
    elif bind >= 0.05:
        role = "structure_builder"
        summary = "This family increases structure or containment."
    elif len(rows) < 3:
        role = "seed_pattern"
        summary = "This family has been seen, but not enough times to prove stability yet."
    elif stability >= 0.75:
        role = "stable_diagnostic"
        summary = "This family holds a consistent shape and is useful for debugging/comparison."
    else:
        role = "emerging_pattern"
        summary = "This family is forming, but does not have a stable role yet."

    return {
        "family": family,
        "turns": len(rows),
        "role": role,
        "summary": summary,
        "top_signature": top_sig,
        "top_signature_hits": top_hits,
        "stability": round(stability, 3),
        "avg_delta": avg_delta,
    }


def render_family_role(family: str) -> str:
    data = family_role(family)

    lines = [
        "CRYSTAL FAMILY ROLE",
        "-------------------",
        f"family             : {data['family']}",
        f"turns              : {data['turns']}",
        f"role               : {data['role']}",
        f"summary            : {data['summary']}",
    ]

    if data["turns"] <= 0:
        return "\n".join(lines)

    lines.extend([
        f"top_signature      : {data['top_signature']}",
        f"top_signature_hits : {data['top_signature_hits']}",
        f"stability          : {data['stability']:.3f}",
        "avg_delta          : "
        + ", ".join(f"{k}={v:+.3f}" for k, v in data["avg_delta"].items()),
    ])

    return "\n".join(lines)


def main():
    family = " ".join(sys.argv[1:]).strip() or "visual_runtime"
    print(render_family_role(family))


if __name__ == "__main__":
    main()

