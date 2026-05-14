#!/usr/bin/env python3
"""
Le'Veon Crystal Index
Builds a compact index of all known shape families and their roles.
Writes: logs/crystal_family_index.json
"""

from __future__ import annotations

import json
import datetime
from pathlib import Path
from collections import Counter
from typing import Any, Dict, List

from runtime.crystal_library_query import load_turns, sig_in
from runtime.crystal_family_roles import family_role


INDEX_PATH = Path("logs/crystal_family_index.json")


def known_families() -> List[str]:
    rows = load_turns()
    counts = Counter()

    for row in rows:
        sig = sig_in(row)
        family = sig.split("|", 1)[0]
        counts[family] += 1

    return [family for family, _ in counts.most_common()]


def build_index() -> Dict[str, Any]:
    families = known_families()

    role_rows = []
    for family in families:
        role_rows.append(family_role(family))

    return {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "family_count": len(role_rows),
        "families": role_rows,
    }


def write_index() -> Dict[str, Any]:
    Path("logs").mkdir(exist_ok=True)
    data = build_index()

    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def render_index() -> str:
    data = write_index()

    lines = [
        "CRYSTAL FAMILY INDEX",
        "--------------------",
        f"generated_at : {data['generated_at']}",
        f"family_count : {data['family_count']}",
        "",
        "FAMILIES",
    ]

    for row in data["families"]:
        lines.append(
            f"- {row['family']:<18} "
            f"turns={row['turns']:<3} "
            f"role={row['role']:<24} "
            f"stability={row.get('stability', 0):.3f}"
        )

    lines.append("")
    lines.append(f"written: {INDEX_PATH}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(render_index())

