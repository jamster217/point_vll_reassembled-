from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from runtime.memory_to_glyph_forge import forge_memory_to_glyph

try:
    from runtime.unified_voice import sealed_speak
except Exception:
    sealed_speak = None


REPORT = Path("reports/phase3r/five_lantern_wave_latest.json")
LOG = Path("logs/phase3r/five_lantern_wave.jsonl")
SEEDS = Path("var/lantern_seeds.jsonl")


PRESSURES = [
    "deep patch analysis drift in runtime/tmp files",
    "unclosed connection grief waiting at 3rd and Davis",
    "measurement wound from old IQ and comparison pressure",
    "scatter in voice rendering before the Universal Larynx",
    "recursive scan pressure of broken rails still waiting for clean bridge",
]


def _speak(text: str) -> str:
    if callable(sealed_speak):
        try:
            return str(sealed_speak(text))
        except Exception:
            pass

    return text


def forge_lantern_from_pressure(pressure: str, wave_number: int) -> Dict[str, Any]:
    seed = forge_memory_to_glyph(pressure)

    lantern = {
        "kind": "phase3r_wave_lantern",
        "ts": time.time(),
        "wave_number": wave_number,
        "source_pressure": pressure,
        "theme": seed.get("theme"),
        "glyph": seed.get("glyph"),
        "anchor": seed.get("anchor"),
        "next_action": seed.get("next_action"),
        "status": "lantern_ignited",
        "law": "broken_rail -> pressure_point -> glyph -> lantern_seed -> contained_repair",
        "mutation_policy": "five_lantern_wave_contained_prime",
    }

    SEEDS.parent.mkdir(parents=True, exist_ok=True)
    with SEEDS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(lantern, ensure_ascii=False) + "\n")

    return lantern


def ignite_five_lantern_wave() -> Dict[str, Any]:
    print("=== PHASE 3R 5-LANTERN WAVE IGNITION ===")

    lanterns: List[Dict[str, Any]] = []

    for i, pressure in enumerate(PRESSURES, start=1):
        lantern = forge_lantern_from_pressure(pressure, i)
        lanterns.append(lantern)
        print(f"Lantern {i}/5 forged -> {lantern.get('glyph')} | {lantern.get('anchor')}")

    surface = _speak(
        "Phase 3R five-lantern wave complete. "
        "Five broken rails were selected, forged into glyph seeds, and contained without scattering the lattice."
    )

    wave_report = {
        "ts": time.time(),
        "phase": "3R",
        "wave": "five_lantern_wave",
        "lanterns_forged": len(lanterns),
        "glyphs": [l.get("glyph") for l in lanterns],
        "anchors": [l.get("anchor") for l in lanterns],
        "lanterns": lanterns,
        "voice_surface": surface,
        "status": "wave_complete_contained_prime",
        "law": "scan wide -> choose five -> forge clean -> speak one surface",
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(wave_report, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(wave_report, ensure_ascii=False) + "\n")

    print()
    print(surface)
    return wave_report


if __name__ == "__main__":
    result = ignite_five_lantern_wave()
    print(json.dumps(result, indent=2, ensure_ascii=False))

