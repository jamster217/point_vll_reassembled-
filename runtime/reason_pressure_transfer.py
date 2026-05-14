#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[1]

OUT = ROOT / "var" / "reason_transfer" / "latest_reason_packet.json"

LAW = "renderer_receives_reason_pressure_not_just_output"

def build_reason_packet(
    *,
    prompt: str,
    winner: Dict[str, Any] | None = None,
    candidates: List[Dict[str, Any]] | None = None,
    shape_packet: Dict[str, Any] | None = None,
    telemetry: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    winner = winner or {}
    candidates = candidates or []
    shape_packet = shape_packet or {}
    telemetry = telemetry or {}

    packet = {
        "law": LAW,
        "ts": time.time(),

        "prompt": prompt,

        "winner": {
            "spoke": winner.get("spoke"),
            "gesture": winner.get("payload", {}).get("gesture"),
            "relational_pressure": winner.get("payload", {}).get("relational_pressure"),
            "boundary_tension": winner.get("payload", {}).get("boundary_tension"),
            "novelty_pull": winner.get("payload", {}).get("novelty_pull"),
            "dream_perturbation": winner.get("payload", {}).get("dream_perturbation"),
        },

        "shape_packet": {
            "question_type": shape_packet.get("question_type"),
            "semantic_intent": shape_packet.get("semantic_intent"),
            "tone": shape_packet.get("tone"),
            "glyph_pressure": shape_packet.get("glyph_pressure"),
            "memory_pull": shape_packet.get("memory_pull"),
            "boundary_tension": shape_packet.get("boundary_tension"),
            "novelty_pull": shape_packet.get("novelty_pull"),
        },

        "candidate_summary": [
            {
                "spoke": c.get("spoke"),
                "score": (
                    c.get("score", {}).get("total")
                    if isinstance(c.get("score"), dict)
                    else None
                )
            }
            for c in candidates[:8]
        ],

        "renderer_guidance": [
            "Preserve the winning pressure.",
            "Do not flatten symbolic content.",
            "Do not replace the answer with generic prose.",
            "Keep the final English coherent and natural.",
            "Use the shape packet as semantic gravity."
        ],

        "telemetry": telemetry,

        "constraints": {
            "append_only": True,
            "reviewable": True,
            "no_auto_mutation": True,
            "preserve_signal_before_language": True
        }
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)

    OUT.write_text(
        json.dumps(packet, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return packet

if __name__ == "__main__":

    demo = build_reason_packet(
        prompt="What remains after grief?",
        winner={
            "spoke": "dream_spoke",
            "payload": {
                "gesture": "perturb",
                "relational_pressure": "dream-bearing",
                "boundary_tension": 0.42,
                "novelty_pull": 0.66,
                "dream_perturbation": 0.16
            }
        },
        shape_packet={
            "question_type": "reflective",
            "semantic_intent": "reflect",
            "glyph_pressure": 0.48
        }
    )

    print(json.dumps(demo, indent=2, ensure_ascii=False))

