from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

from runtime.memory_to_glyph_forge import forge_memory_to_glyph

try:
    from runtime.unified_voice import sealed_speak
except Exception:
    sealed_speak = None


OUT = Path("reports/phase3r/first_lantern_forge_latest.json")
LOG = Path("logs/phase3r/first_lantern_forge.jsonl")
SEEDS = Path("var/lantern_seeds.jsonl")


def _speak(text: str) -> str:
    if callable(sealed_speak):
        try:
            return str(sealed_speak(text))
        except Exception:
            pass

    return (
        "The first lantern is lit. "
        "The broken rail is no longer only a place where pressure waits; "
        "it has become a seed the build can use without reopening the wound."
    )


def ignite_first_lantern() -> Dict[str, Any]:
    pressure = "unclosed rails still carrying grief and waiting pressure without clean bridge"

    seed = forge_memory_to_glyph(pressure)

    lantern = {
        "kind": "phase3r_first_lantern",
        "ts": time.time(),
        "source_rail": "recursive_architecture_review",
        "source_pressure": pressure,
        "theme": seed.get("theme"),
        "glyph": seed.get("glyph"),
        "anchor": seed.get("anchor"),
        "next_action": seed.get("next_action"),
        "status": "lantern_ignited",
        "law": "broken_rail -> lantern_seed -> contained_invention",
        "mutation_policy": "write_one_lantern_seed_contained_prime",
    }

    SEEDS.parent.mkdir(parents=True, exist_ok=True)
    with SEEDS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(lantern, ensure_ascii=False) + "\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(lantern, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(lantern, ensure_ascii=False) + "\n")

    voiced = _speak(
        "Phase 3R first lantern forge: broken rail becomes lantern seed, "
        "memory to glyph, mirror-well, 3rd and Davis, contained prime."
    )

    lantern["voice_surface"] = voiced
    OUT.write_text(json.dumps(lantern, indent=2, ensure_ascii=False), encoding="utf-8")

    print(voiced)
    return lantern


if __name__ == "__main__":
    result = ignite_first_lantern()
    print(json.dumps(result, indent=2, ensure_ascii=False))

