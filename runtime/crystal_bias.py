import json
from pathlib import Path

CRYSTAL_PATH = Path("assets/memory/crystallibrary.json")

def load():
    if not CRYSTAL_PATH.exists():
        return {}
    return json.loads(CRYSTAL_PATH.read_text(encoding="utf-8"))

def apply_family_bias(scores: dict, kernel_state: dict):
    crystal = load()
    bias_map = crystal.get("family_bias", {})
    emotion = kernel_state.get("emotion", {})

    tension = float(emotion.get("tension", 0.0))
    focus = float(emotion.get("focus", 0.5))
    memory = float(kernel_state.get("memory", 0.0))
    harmonic_528 = float(kernel_state.get("harmonic_528", 0.0))

    for fam, base in list(scores.items()):
        bias = float(bias_map.get(fam, 0.0))

        if fam == "fire":
            bias += tension * 0.30
        if fam == "witness":
            bias += focus * 0.20
        if fam == "dream":
            bias += memory * 0.15
        if fam == "crystal":
            bias += harmonic_528 * 0.25

        scores[fam] = base + bias

    return scores

