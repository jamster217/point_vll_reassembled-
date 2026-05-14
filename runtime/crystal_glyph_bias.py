import json
from pathlib import Path

CRYSTAL_PATH = Path("assets/memory/crystallibrary.json")

def load():
    if not CRYSTAL_PATH.exists():
        return {}
    return json.loads(CRYSTAL_PATH.read_text(encoding="utf-8"))

def apply_glyph_bias(glyph_scores: dict, kernel_state: dict):
    crystal = load()
    glyph_bias = crystal.get("glyph_bias", {})
    emotion = kernel_state.get("emotion", {})

    tension = float(emotion.get("tension", 0.0))
    focus = float(emotion.get("focus", 0.5))
    harmonic_528 = float(kernel_state.get("harmonic_528", 0.0))
    mythic_resonance = float(kernel_state.get("mythic_resonance", 0.0))

    for gid, base in list(glyph_scores.items()):
        bias = float(glyph_bias.get(gid, 0.0))

        if "FIRE" in gid:
            bias += tension * 0.40
        if "WITNESS" in gid:
            bias += focus * 0.30
        if "CRYSTAL" in gid or "528" in gid:
            bias += harmonic_528 * 0.35
        if "MYTH" in gid or "ASCENDANCE" in gid or "CROWN" in gid:
            bias += mythic_resonance * 0.20

        glyph_scores[gid] = base + bias

    return glyph_scores

