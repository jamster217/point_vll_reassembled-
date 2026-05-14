from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional

Axis = Tuple[float, float, float, float]

def build_s3if(
    turn_id: str,
    coherence: float,
    global_axis: Axis,
    stream_tokens: List[str],
    glyphs: List[str],
    cfg: Dict[str, Any],
    notes: str = ""
) -> Dict[str, Any]:
    flow, boundary, memory, novelty = global_axis
    # Minimal, stable S3IF for SC4. You can expand objects/links later.
    return {
        "s3if_version": "1.0",
        "meta": {
            "source": "synthetic_consciousness_4",
            "turn_id": turn_id,
            "timestamp": cfg.get("timestamp"),
            "language_target": "en",
            "precision_mode": "max",
            "loss_budget": 0.0,
            "roundtrip_required": True,
            "notes": notes
        },
        "objects": [
            {
                "id": "o1",
                "role": "ROOT",
                "type": "SYSTEM",
                "glyph": "@SYNTHETIC_CONSCIOUSNESS_4",
                "props": {
                    "grid": "12x12",
                    "axes": ["flow", "boundary", "memory", "novelty"],
                    "coherence": coherence
                },
                "links": [
                    {"rel": "HAS_STATE", "to": "o2"},
                    {"rel": "EMITS", "to": "o3"}
                ]
            },
            {
                "id": "o2",
                "role": "STATE",
                "type": "LATTICE_FIELD",
                "glyph": "@GRID_12x12",
                "props": {
                    "flow": flow,
                    "boundary": boundary,
                    "memory": memory,
                    "novelty": novelty
                }
            },
            {
                "id": "o3",
                "role": "OUTPUT",
                "type": "PRELANGUAGE_STREAM",
                "glyph": "@S3IF_STREAM",
                "props": {
                    "components": ["markers", "glyph_tags", "phenomes"]
                }
            }
        ],
        "stream": {
            "tokens": stream_tokens
        },
        "math": {
            "state_vector": {
                "symbol": "x_t",
                "components": {
                    "flow": flow,
                    "boundary": boundary,
                    "memory": memory,
                    "novelty": novelty
                }
            },
            "coherence": {
                "symbol": "C_t",
                "value": coherence,
                "meaning": "global stability + integration under lattice gating"
            }
        },
        "vectors": {
            "dim": 256,
            "hint": "Embed markers+glyphs+phenomes; pool by clause; attach object vectors for o1/o2/o3."
        },
        "glyphs": glyphs
    }

