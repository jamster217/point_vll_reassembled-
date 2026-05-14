from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

from runtime.phase3r_recursive_architecture_review import run_review
from runtime.memory_to_glyph_forge import forge_memory_to_glyph

try:
    from runtime.unified_voice import sealed_speak
except Exception:
    sealed_speak = None


OUT = Path("reports/phase3r/recursive_lantern_wave_latest.json")
LOG = Path("logs/phase3r/recursive_lantern_wave.jsonl")
SEEDS = Path("var/lantern_seeds.jsonl")


def _clean_pressure(first_lantern: Dict[str, Any]) -> str:
    source = first_lantern.get("source_path", "unknown_source")
    hits = first_lantern.get("detected_pressure") or []
    if isinstance(hits, list):
        hit_text = ", ".join(str(x) for x in hits[:12])
    else:
        hit_text = str(hits)

    return (
        f"broken rail at {source}; pressure terms: {hit_text}; "
        "needs one clean bridge into future design"
    )


def _speak(surface: str) -> str:
    if callable(sealed_speak):
        try:
            return str(sealed_speak(surface))
        except Exception:
            pass
    return surface


def run_lantern_wave(max_files: int = 8000) -> Dict[str, Any]:
    review = run_review(max_files=max_files)
    first = review.get("first_lantern") or {}

    if not first:
        result = {
            "ts": time.time(),
            "phase": "3R",
            "status": "no_new_broken_rail",
            "review_counts": review.get("counts", {}),
            "scan_field": review.get("scan_field", {}),
            "surface": "No new broken rail was selected. The lattice remains in review mode.",
            "mutation_policy": "dry_run_contained_prime",
        }
    else:
        pressure = _clean_pressure(first)
        seed = forge_memory_to_glyph(pressure)

        lantern = {
            "kind": "phase3r_recursive_lantern_seed",
            "ts": time.time(),
            "source_rail": first.get("source_path"),
            "detected_pressure": first.get("detected_pressure"),
            "theme": seed.get("theme"),
            "glyph": seed.get("glyph"),
            "anchor": seed.get("anchor"),
            "next_action": seed.get("next_action"),
            "status": "lantern_ignited",
            "law": "broken_rail -> pressure_terms -> glyph_seed -> contained_repair",
        }

        SEEDS.parent.mkdir(parents=True, exist_ok=True)
        with SEEDS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(lantern, ensure_ascii=False) + "\n")

        surface = (
            "The recursive scan found one rail still carrying pressure without a clean bridge. "
            "The Forge did not flood the lattice. It lit one lantern: one glyph, one anchor, one next action."
        )

        result = {
            "ts": time.time(),
            "phase": "3R",
            "status": "lantern_wave_complete",
            "review_counts": review.get("counts", {}),
            "scan_field": review.get("scan_field", {}),
            "selected_rail": first,
            "forged_lantern": lantern,
            "surface": _speak(surface),
            "mutation_policy": "one_lantern_per_wave_contained_prime",
        }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    return result


if __name__ == "__main__":
    out = run_lantern_wave(max_files=8000)

    print(out["surface"])
    print()
    print("status:", out["status"])
    print("scan_field:", out.get("scan_field"))
    print("counts:", out.get("review_counts"))

    if out.get("forged_lantern"):
        print("lantern:", json.dumps(out["forged_lantern"], indent=2, ensure_ascii=False))

    print("report:", OUT)

