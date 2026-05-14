#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[2]

DREAM_DIR = ROOT / "var" / "dream_discharge"

OUT = ROOT / "var" / "dream_loop" / "optimization_insights.json"

LAW = "dreams_generate_optimization_hypotheses"

KEY_PATTERNS = {
    "clarity": [
        "clear",
        "clarity",
        "stable",
        "organized",
        "clean"
    ],
    "surface_leakage": [
        "leak",
        "spill",
        "telemetry",
        "raw",
        "flood"
    ],
    "compression": [
        "compress",
        "smaller",
        "shorter",
        "condense"
    ],
    "memory": [
        "memory",
        "archive",
        "remember",
        "signal"
    ],
    "cadence": [
        "voice",
        "cadence",
        "rhythm",
        "speak"
    ]
}

def load_dreams() -> List[Dict[str, Any]]:

    dreams = []

    if not DREAM_DIR.exists():
        return dreams

    for p in sorted(DREAM_DIR.glob("*.json")):

        try:
            dreams.append(
                json.loads(
                    p.read_text(encoding="utf-8")
                )
            )
        except Exception:
            pass

    return dreams

def extract_insights(text: str) -> Dict[str, int]:

    low = text.lower()

    out = {}

    for k, patterns in KEY_PATTERNS.items():

        score = 0

        for pat in patterns:
            score += low.count(pat)

        out[k] = score

    return out

def summarize(insights: Dict[str, int]) -> List[str]:

    suggestions = []

    if insights["clarity"] >= 2:
        suggestions.append(
            "Increase ordinary-mouth compression and surface stabilization."
        )

    if insights["surface_leakage"] >= 1:
        suggestions.append(
            "Reduce telemetry/scaffold leakage into final English."
        )

    if insights["compression"] >= 1:
        suggestions.append(
            "Prefer shorter factual answers when signal survives intact."
        )

    if insights["memory"] >= 1:
        suggestions.append(
            "Strengthen symbolic memory indexing and retrieval."
        )

    if insights["cadence"] >= 1:
        suggestions.append(
            "Smooth conversational cadence and reduce repetitive phrasing."
        )

    return suggestions

def run() -> Dict[str, Any]:

    dreams = load_dreams()

    merged = {
        "clarity": 0,
        "surface_leakage": 0,
        "compression": 0,
        "memory": 0,
        "cadence": 0
    }

    for d in dreams:

        text = str(
            d.get("dream_discharge", "")
        )

        scores = extract_insights(text)

        for k, v in scores.items():
            merged[k] += v

    result = {
        "law": LAW,
        "timestamp": time.time(),
        "dream_count": len(dreams),
        "pressure_totals": merged,
        "optimization_hypotheses": summarize(merged),
        "constraints": {
            "proposal_only": True,
            "append_only": True,
            "no_auto_mutation": True
        }
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(payload)

    print(f"[dream_optimizer] wrote: {OUT}")

    return result

if __name__ == "__main__":

    print(
        json.dumps(
            run(),
            indent=2,
            ensure_ascii=False
        )
    )

