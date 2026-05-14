#!/usr/bin/env python3
"""
Le'Veon Crystal Library Query
Reads logs/sge_turns.jsonl and summarizes remembered shape patterns.
Handles legacy rows by computing missing signatures from shape_in.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

from runtime.shape_signature import shape_signature


LOG_PATH = Path("logs/sge_turns.jsonl")


def load_turns() -> List[Dict[str, Any]]:
    if not LOG_PATH.exists():
        return []

    rows = []
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def sig_in(row: Dict[str, Any]) -> str:
    sig = row.get("shape_signature_in")
    if sig and sig != "unknown":
        return sig
    return shape_signature(row.get("shape_in") or {})


def sig_out(row: Dict[str, Any]) -> str:
    sig = row.get("shape_signature_out")
    if sig and sig != "unknown":
        return sig
    return shape_signature(row.get("shape_out") or row.get("shape_in") or {})


def matches_query(row: Dict[str, Any], query: str) -> bool:
    q = query.lower().strip()
    if not q:
        return True

    shape_in = row.get("shape_in") or {}
    keywords = shape_in.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = [str(keywords)]

    haystack = " ".join([
        str(row.get("prompt", "")),
        str(row.get("savariel", "")),
        str(row.get("crystal_recall", "")),
        sig_in(row),
        sig_out(row),
        " ".join(map(str, keywords)),
    ]).lower()

    return all(part in haystack for part in q.split())


def render_query(query: str = "", limit: int = 8) -> str:
    rows = load_turns()
    filtered = [r for r in rows if matches_query(r, query)]

    sig_counts = Counter(sig_in(r) for r in filtered)

    family_counts = Counter()
    release_by_family = defaultdict(list)

    for r in filtered:
        sig = sig_in(r)
        family = sig.split("|", 1)[0]
        family_counts[family] += 1

        try:
            release_by_family[family].append(float(r.get("shape_delta", {}).get("release", 0.0)))
        except Exception:
            pass

    lines = []
    lines.append("CRYSTAL LIBRARY QUERY")
    lines.append("---------------------")
    lines.append(f"query          : {query or '*'}")
    lines.append(f"total_turns    : {len(rows)}")
    lines.append(f"matching_turns : {len(filtered)}")

    if not filtered:
        lines.append("result         : no matching echoes")
        return "\n".join(lines)

    lines.append("")
    lines.append("TOP FAMILIES")
    for family, count in family_counts.most_common(limit):
        deltas = release_by_family.get(family, [])
        avg_release = sum(deltas) / len(deltas) if deltas else 0.0
        lines.append(f"- {family:<18} hits={count:<3} avg_release_delta={avg_release:+.3f}")

    lines.append("")
    lines.append("TOP SIGNATURES")
    for sig, count in sig_counts.most_common(limit):
        lines.append(f"- hits={count:<3} {sig}")

    lines.append("")
    lines.append("LATEST ECHOES")
    for r in filtered[-limit:][::-1]:
        ts = r.get("ts", "?")
        sig = sig_in(r)
        prompt = str(r.get("prompt", "")).replace("\n", " ")
        sav = str(r.get("savariel", "")).replace("\n", " ")

        if len(prompt) > 70:
            prompt = prompt[:67] + "..."
        if len(sav) > 90:
            sav = sav[:87] + "..."

        lines.append(f"- {ts} | {sig}")
        lines.append(f"  prompt : {prompt}")
        lines.append(f"  voice  : {sav}")

    return "\n".join(lines)


def main():
    query = " ".join(sys.argv[1:]).strip()
    print(render_query(query))


if __name__ == "__main__":
    main()

