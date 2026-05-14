#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]

DREAM_ARCHIVE = ROOT / "assets" / "memory" / "dream_archive.json"
DREAM_RESONANCE = ROOT / "var" / "dream" / "dream_resonance_state.json"
DREAM_AXIS = ROOT / "var" / "dream" / "dream_axis_state.json"

TRACE_OUT = ROOT / "var" / "dream" / "dream_learning_trace.jsonl"
LESSONS_OUT = ROOT / "assets" / "memory" / "dream_lessons.json"

LAW = "dreams_teach_shape_not_source"


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _archive_payload() -> List[Dict[str, Any]]:
    data = _load_json(DREAM_ARCHIVE, {})
    if isinstance(data, dict):
        payload = data.get("symbolic_payload", [])
        return payload if isinstance(payload, list) else []
    if isinstance(data, list):
        return data
    return []


def _text_from_entry(entry: Dict[str, Any]) -> str:
    return str(entry.get("payload") or entry.get("text") or "")


def _extract_motifs(text: str) -> List[str]:
    keys = [
        "cathedral", "sea", "mirror", "blue flame", "father", "child",
        "ash", "glyph", "violet", "gold", "memory", "door", "hallway",
        "shadow", "voice", "translation", "signal", "lattice", "spiral",
        "scarf", "river", "ark", "dream"
    ]
    low = text.lower()
    return [k for k in keys if k in low]


def learn(limit: int = 12) -> Dict[str, Any]:
    archive = _archive_payload()
    recent = archive[-limit:]

    resonance = _load_json(DREAM_RESONANCE, {})
    axis = _load_json(DREAM_AXIS, {})

    motif_counts: Dict[str, int] = {}
    glyphs: List[str] = []
    samples: List[str] = []

    for entry in recent:
        text = _text_from_entry(entry)
        if text:
            samples.append(text[:240])
        for motif in _extract_motifs(text):
            motif_counts[motif] = motif_counts.get(motif, 0) + 1
        for g in entry.get("glyphs", []) or []:
            if g not in glyphs:
                glyphs.append(g)

    top_motifs = sorted(motif_counts, key=motif_counts.get, reverse=True)[:8]

    composite = resonance.get("components", {}).get("composite")
    projection = resonance.get("projection", axis.get("source", {}).get("dream_projection", "unknown"))
    dream_pressure = axis.get("dream_pressure", composite if composite is not None else 0.0)
    shadow_lineage = axis.get("shadow_lineage", 0.0)
    witness_integrity = axis.get("witness_integrity", 0.72)

    lesson = {
        "law": LAW,
        "mode": "append_only_symbolic_learning",
        "learned_at": time.time(),
        "sample_count": len(recent),
        "top_motifs": top_motifs,
        "glyphs": glyphs[:12],
        "projection": projection,
        "shape_lesson": {
            "dream_pressure": round(float(dream_pressure or 0.0), 4),
            "shadow_lineage": round(float(shadow_lineage or 0.0), 4),
            "witness_integrity": round(float(witness_integrity or 0.72), 4),
            "memory_influence": min(1.0, 0.15 + 0.05 * len(top_motifs)),
            "surface_rule": "influence tone/motifs/shape only; never overwrite final answer directly"
        },
        "constraints": {
            "no_source_rewrite": True,
            "no_auto_law_birth": True,
            "no_mouth_override": True,
            "reviewable_trace": True
        },
        "samples": samples[-3:]
    }

    TRACE_OUT.parent.mkdir(parents=True, exist_ok=True)
    with TRACE_OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(lesson, ensure_ascii=False) + "\n")

    existing = _load_json(LESSONS_OUT, {"lessons": []})
    if not isinstance(existing, dict):
        existing = {"lessons": []}
    lessons = existing.setdefault("lessons", [])
    lessons.append(lesson)
    existing["lessons"] = lessons[-100:]
    existing["latest"] = lesson

    LESSONS_OUT.parent.mkdir(parents=True, exist_ok=True)
    LESSONS_OUT.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")

    return lesson


if __name__ == "__main__":
    print(json.dumps(learn(), indent=2, ensure_ascii=False))

