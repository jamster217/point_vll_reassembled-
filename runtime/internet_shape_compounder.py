#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[1]

OUT_JSONL = ROOT / "var" / "internet_memory" / "shape_compounds.jsonl"
OUT_MEMORY = ROOT / "assets" / "memory" / "internet_shape_memory.json"

LAW = "internet_learns_shape_not_source"

KEYS = [
    "memory",
    "boundary",
    "recursion",
    "dream",
    "signal",
    "language",
    "translation",
    "structure",
    "field",
    "pressure",
    "symbol",
    "mirror",
    "time",
    "coherence",
    "pattern",
]

def extract_shape(text: str) -> Dict[str, Any]:
    low = text.lower()

    motifs: List[str] = []

    for k in KEYS:
        if k in low:
            motifs.append(k)

    shape = {
        "motifs": motifs[:12],
        "density": round(min(1.0, len(motifs) / 10.0), 3),
        "symbolic_pressure": round(
            min(1.0, (len(text) / 1200.0)),
            3
        ),
        "coherence_estimate": round(
            min(1.0, 0.45 + (len(motifs) * 0.05)),
            3
        )
    }

    return shape

def compound(
    *,
    query: str,
    source_text: str,
    source_url: str = "",
) -> Dict[str, Any]:

    shape = extract_shape(source_text)

    packet = {
        "law": LAW,
        "ts": time.time(),
        "query": query,
        "source_url": source_url,
        "shape": shape,
        "summary": source_text[:600],
        "constraints": {
            "append_only": True,
            "no_source_rewrite": True,
            "reviewable": True
        }
    }

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)

    with OUT_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")

    existing = {"compounds": []}

    if OUT_MEMORY.exists():
        try:
            existing = json.loads(
                OUT_MEMORY.read_text(encoding="utf-8")
            )
        except Exception:
            pass

    compounds = existing.setdefault("compounds", [])
    compounds.append(packet)

    existing["latest"] = packet
    existing["compounds"] = compounds[-200:]

    OUT_MEMORY.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return packet

if __name__ == "__main__":

    demo = compound(
        query="autumn leaves",
        source_text="Leaves change color because chlorophyll breaks down during autumn."
    )

    print(json.dumps(demo, indent=2, ensure_ascii=False))

