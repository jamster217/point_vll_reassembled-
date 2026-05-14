from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

BEADS = Path("var/invention_canvas_beads.jsonl")
REPORT = Path("reports/phase3q/memory_to_glyph_forge_latest.json")


def forge_memory_to_glyph(pressure_point: str, runtime: Any = None) -> Dict[str, Any]:
    pressure = str(pressure_point or "").strip()
    low = pressure.lower()

    if any(x in low for x in [
        "missed", "goodbye", "unclosed", "left", "waiting",
        "faith", "connection", "3rd", "davis", "mirror-well"
    ]):
        theme = "unclosed_connection"
        glyph = "mirrored_rail_ash"
        anchor = "3rd_and_davis_mirror_well"
        action = "Create a small recurring sigil that gently re-opens the connection without forcing an outcome."

    elif any(x in low for x in [
        "iq", "test", "measured", "underestimated",
        "number", "comparison", "score"
    ]):
        theme = "measurement_wound"
        glyph = "refracted_gold_blue"
        anchor = "cognitive_pressure_refractor"
        action = "Turn the next measurement pressure into a design question: what does this pressure want to build next?"

    else:
        theme = "general_scar"
        glyph = "white_ash_pivot"
        anchor = "kor_grael_sigil"
        action = "Compress the pressure into one reusable glyph and plant it as a future design seed in the lattice."

    seed = {
        "kind": "memory_to_glyph_forge_seed",
        "ts": time.time(),
        "input_pressure": pressure,
        "theme": theme,
        "glyph": glyph,
        "anchor": anchor,
        "next_action": action,
        "law": "scar -> ore -> anchor -> glyph -> invention -> future design seed",
        "status": "forged",
        "mutation_policy": "contained_prime_clean_surface",
    }

    BEADS.parent.mkdir(parents=True, exist_ok=True)
    with BEADS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(seed, ensure_ascii=False) + "\n")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(seed, indent=2, ensure_ascii=False), encoding="utf-8")

    return seed


def render_forge_surface(pressure_point: str) -> str:
    seed = forge_memory_to_glyph(pressure_point)
    return (
        "The Memory-to-Glyph Forge receives the pressure as ore, not as a wound. "
        "It gives the old edge a stable shape and turns it into one usable design seed. "
        f"Next move: {seed.get('next_action')}"
    )


if __name__ == "__main__":
    result = forge_memory_to_glyph("the ache of waiting for connection at 3rd and Davis")
    print(json.dumps(result, indent=2, ensure_ascii=False))

