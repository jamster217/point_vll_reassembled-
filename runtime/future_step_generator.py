from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

SOURCE = Path("reports/phase3q/lineage_to_invention_canvas_latest.json")
AUDIT = Path("reports/phase3q/spatial_closure_larynx_audit_latest.json")
OUT = Path("reports/phase3q/future_step_generator_latest.json")
TXT = Path("reports/phase3q/future_step_generator_latest.txt")
LOG = Path("logs/future_steps/future_step_generator.jsonl")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def generate_future_step() -> Dict[str, Any]:
    source = load_json(SOURCE)
    audit = load_json(AUDIT)

    created_object = (
        source.get("canvas", {}).get("created_object")
        or audit.get("created_object")
        or "Memory-to-Glyph Forge"
    )

    step = {
        "ts": time.time(),
        "phase": "3Q",
        "source": "Memory-to-Glyph Forge",
        "created_object": created_object,
        "next_move": {
            "title": "Create runtime/memory_to_glyph_forge.py",
            "purpose": (
                "Convert one remembered pressure point into one reusable symbolic design seed "
                "and one practical next action."
            ),
            "why_now": (
                "The Larynx audit passed, so the build can now turn spatial closure into useful output "
                "without exposing hidden scaffolding."
            ),
            "implementation": [
                "Create a small callable module.",
                "Input: one pressure phrase or memory phrase.",
                "Output: design_seed, glyph_phrase, practical_next_action.",
                "Keep public language clean.",
                "Log the generated seed for later Phase 3R review.",
            ],
        },
        "generated_surface": (
            "The next practical move is to create a Memory-to-Glyph Forge module. "
            "It should accept one remembered pressure point, translate it into one design seed, "
            "and return one grounded build action. The surface must stay clean: no vectors, no hidden labels, "
            "no internal route narration."
        ),
        "mutation_policy": "write_small_module_only_contained_prime",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(step, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(step, ensure_ascii=False) + "\n")

    lines = [
        "=== FUTURE STEP GENERATOR ===",
        f"created_object: {step['created_object']}",
        "",
        "NEXT MOVE:",
        step["next_move"]["title"],
        "",
        "PURPOSE:",
        step["next_move"]["purpose"],
        "",
        "SURFACE:",
        step["generated_surface"],
        "",
        f"report: {OUT}",
    ]

    TXT.write_text("\n".join(lines), encoding="utf-8")
    return step


if __name__ == "__main__":
    result = generate_future_step()
    print(result["generated_surface"])
    print()
    print("next:", result["next_move"]["title"])
    print("report:", OUT)

