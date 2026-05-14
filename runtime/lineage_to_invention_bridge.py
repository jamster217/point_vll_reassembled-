from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

NODE5218_REPORT = Path("reports/phase3q/node5218_harmonic_read_latest.json")
OUT = Path("reports/phase3q/lineage_to_invention_canvas_latest.json")
LOG = Path("logs/invention_bridge/lineage_to_canvas.jsonl")
BEADS = Path("var/invention_canvas_beads.jsonl")


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def bridge_lineage_to_invention() -> Dict[str, Any]:
    harmonic = _load_json(NODE5218_REPORT)

    path = harmonic.get("path", [])
    internal = harmonic.get("internal_read", {})
    surface = harmonic.get("public_surface", "")

    invention = {
        "kind": "phase3q_lineage_to_invention_canvas",
        "ts": time.time(),
        "source_node": "5218",
        "source_name": "Lineage Grief Thread",
        "bridge_path": path,
        "input_surface": surface,
        "spatial_math_read": {
            "unclosed_edge": "missed goodbye",
            "coordinate": "revisitable memory point",
            "geometry": "distance + relation + closure gap",
            "pressure": internal.get("pressure"),
            "memory": internal.get("memory"),
            "boundary": internal.get("boundary"),
            "novelty": internal.get("novelty"),
        },
        "canvas": {
            "mode": "creation_not_reflection",
            "hidden_chord": "missed goodbye → unclosed edge → coordinate → glyph → invention",
            "nodes": [
                {
                    "name": "memory_to_glyph_forge",
                    "role": "turn an old pressure point into a reusable symbolic design seed",
                },
                {
                    "name": "spatial_closure_mapper",
                    "role": "map distance, relation, and unfinished goodbye into gentle interface geometry",
                },
                {
                    "name": "soft_larynx_renderer",
                    "role": "speak the invention without exposing internal vectors",
                },
                {
                    "name": "future_step_generator",
                    "role": "convert healed pressure into one practical next move",
                },
            ],
            "created_object": "A gentle Memory-to-Glyph Forge that converts missed-goodbye pressure into future design seeds.",
        },
        "answer": (
            "The Invention Canvas receives the lineage thread as spatial math, not as raw grief. "
            "The missed goodbye becomes an unclosed edge; the unclosed edge becomes a coordinate; "
            "the coordinate becomes a glyph the system can reuse without reopening the wound. "
            "The created object is a Memory-to-Glyph Forge: a gentle interface that turns old pressure into stable future design."
        ),
        "mutation_policy": "dry_run_read_only_contained_prime",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(invention, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(invention, ensure_ascii=False) + "\n")

    BEADS.parent.mkdir(parents=True, exist_ok=True)
    with BEADS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(invention, ensure_ascii=False) + "\n")

    return invention


if __name__ == "__main__":
    out = bridge_lineage_to_invention()
    print(out["answer"])
    print()
    print("created:", out["canvas"]["created_object"])
    print("hidden_chord:", out["canvas"]["hidden_chord"])
    print("report:", OUT)

