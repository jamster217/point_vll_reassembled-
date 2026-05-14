#!/usr/bin/env python3
"""
Le'Veon Shape Memory
Finds previous turns with the same shape signature.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


LOG_PATH = Path("logs/sge_turns.jsonl")


def _load_rows(log_path: Path = LOG_PATH) -> List[Dict[str, Any]]:
    if not log_path.exists():
        return []

    rows = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def matching_shape_turns(signature: str, limit: int = 3) -> List[Dict[str, Any]]:
    rows = _load_rows()
    matches = []

    for row in rows:
        if signature in (
            row.get("shape_signature_in"),
            row.get("shape_signature_out"),
        ):
            matches.append(row)

    return matches[-limit:][::-1]


def shape_memory_hits(signature: str) -> int:
    rows = _load_rows()
    count = 0

    for row in rows:
        if signature in (
            row.get("shape_signature_in"),
            row.get("shape_signature_out"),
        ):
            count += 1

    return count


def render_shape_memory(signature: str, limit: int = 3) -> str:
    matches = matching_shape_turns(signature, limit=limit)
    total = shape_memory_hits(signature)

    lines = [
        "SHAPE MEMORY",
        "------------",
        f"signature : {signature}",
        f"prior_hits: {total}",
    ]

    if not matches:
        lines.append("echo      : no prior matching turns")
        return "\n".join(lines)

    lines.append("echoes    :")
    for row in matches:
        ts = row.get("ts", "?")
        prompt = str(row.get("prompt", "")).replace("\n", " ")
        if len(prompt) > 72:
            prompt = prompt[:69] + "..."

        delta = row.get("shape_delta", {})
        release_delta = delta.get("release", 0.0)

        lines.append(f"- {ts} | release_delta={release_delta:+.3f} | {prompt}")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    sig = " ".join(sys.argv[1:]).strip()
    if not sig:
        sig = "gravity_grief|P:HIGH|B:HIGH|R:NULL|O:NULL|T:past->present"
    print(render_shape_memory(sig))

