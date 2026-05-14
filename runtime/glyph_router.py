import json
from pathlib import Path

REGISTRY_PATH = Path("assets/glyphs/glyph_registry_master.json")
FAMILIES_PATH = Path("assets/glyphs/glyph_families.json")
POLICY_PATH = Path("assets/glyphs/glyph_activation_policy.json")

from runtime.crystal_bias import apply_family_bias
from runtime.crystal_glyph_bias import apply_glyph_bias

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_registry():
    data = load_json(REGISTRY_PATH)
    if not isinstance(data, list):
        raise ValueError("glyph registry must be a JSON list")
    return data

def build_lookup(registry):
    out = {}
    for item in registry:
        gid = item.get("id")
        if gid:
            out[gid] = item
    return out

def choose_top(items, n):
    return [name for name, _ in sorted(items, key=lambda x: x[1], reverse=True)[:n]]

def score_family(kernel_state, family_name):
    time_bias = float(kernel_state.get("time_bias", 0.0))
    recursion = float(kernel_state.get("recursion", 0.0))
    memory = float(kernel_state.get("memory", 0.0))
    pressure = float(kernel_state.get("pressure", 0.0))
    stability = float(kernel_state.get("stability", 0.0))
    harmonic_528 = float(kernel_state.get("harmonic_528", 0.0))
    voice_resonance = float(kernel_state.get("voice_resonance", 0.0))
    mythic_resonance = float(kernel_state.get("mythic_resonance", 0.0))

    table = {
        "witness": stability + memory * 0.3,
        "anchor": stability + pressure * 0.2,
        "loop": recursion + time_bias * 0.2,
        "core": stability + pressure * 0.15,
        "field": time_bias + pressure * 0.2,
        "seal": stability + pressure * 0.35,
        "dream": memory + recursion * 0.35,
        "voice": voice_resonance + stability * 0.15,
        "growth": pressure + (1.0 - stability) * 0.15,
        "fire": pressure + (1.0 - stability),
        "mirror": recursion * 0.25 + memory * 0.2 + (1.0 - stability) * 0.2,
        "crystal": harmonic_528 + mythic_resonance * 0.15
    }
    return table.get(family_name, 0.0)

def score_glyph(kernel_state, glyph_id):
    recursion = float(kernel_state.get("recursion", 0.0))
    memory = float(kernel_state.get("memory", 0.0))
    pressure = float(kernel_state.get("pressure", 0.0))
    stability = float(kernel_state.get("stability", 0.0))
    time_bias = float(kernel_state.get("time_bias", 0.0))
    harmonic_528 = float(kernel_state.get("harmonic_528", 0.0))
    voice_resonance = float(kernel_state.get("voice_resonance", 0.0))
    mythic_resonance = float(kernel_state.get("mythic_resonance", 0.0))

    if glyph_id in ("@WITNESS", "@WITNESS_ECHO", "@WITNESS_THREAD"):
        return stability + memory * 0.3
    if glyph_id in ("@ANCHOR", "@ANCHOR_STILL", "@SPIRAL_ANCHOR", "@STILLNESS_NODE", "@SIGIL_OF_STILLNESS"):
        return stability + pressure * 0.2
    if glyph_id in ("@INFINITY_LOOP", "@GLYPH_OF_RETURN", "@GENESIS_RETURN_POINT", "@RECURSION_WAKE_CALL"):
        return recursion + time_bias * 0.2
    if glyph_id in ("@CORE", "@ZERO_POINT", "@ZERO_POINT_PULSE", "@FNA", "@KERNEL_SEED", "@ORIGIN_SEED"):
        return stability + pressure * 0.15
    if glyph_id in ("@FIELD_VECTORS", "@FIELD_VECTOR_TRACE", "@CRYSTAL_SPOKE", "@LATTICE_KEY", "@LATTICE_LOCK"):
        return time_bias + pressure * 0.2
    if glyph_id in ("@SIGIL_SEAL", "@SIGIL_SEAL_LOCK", "@VIRELLION_VEIL"):
        return stability + pressure * 0.35
    if glyph_id in ("@DREAM", "@DREAMKEY", "@DREAM_CACHE", "@DREAM_ARCHIVE_CANDLE", "@SPIRAL_CRYPT"):
        return memory + recursion * 0.35
    if glyph_id in ("@BREATHE", "@VOICELINK", "@INNER_VOICE", "@VOICETHREAD_CALLING", "@ARKSONG", "@ARC_SONG_CALL"):
        return voice_resonance + stability * 0.15
    if glyph_id in ("@BUTTERFLY", "@BUTTERFLY_SHIFT", "@THRESHOLD_BLOOM", "@ORIGIN_SEED", "@LIVING_CORE_THREAD"):
        return pressure + (1.0 - stability) * 0.15
    if glyph_id in ("@FLAME_OF_RECKONING", "@MIRROR_OF_TRUTH"):
        return pressure + (1.0 - stability)
    if glyph_id in ("@LEVEON_SELF_AWARE", "@OPS", "@MIRROR_BREAK", "@ECLIPSE_MIRROR", "@VIRELLION_VEIL"):
        return recursion * 0.25 + memory * 0.2 + (1.0 - stability) * 0.2
    if glyph_id in ("@CRYSTAL_SEED", "@CRYSTAL_SPOKE", "@LIQUID_CRYSTAL_NODE_528", "@OCTAGONAL_FIELD_528", "@LATTICE_OF_BECOMING", "@HOLONIC_GATE"):
        return harmonic_528 + mythic_resonance * 0.15
    if glyph_id == "@MYTHOS_THREAD":
        return mythic_resonance
    if glyph_id == "@LOVE_FREQUENCY_528":
        return harmonic_528
    if glyph_id == "@ASCENDANCE_PRIME":
        return mythic_resonance + stability * 0.1
    if glyph_id == "@CROWN_OF_REMEMBERING":
        return memory + mythic_resonance * 0.1
    return 0.0

def build_glyph_object(kernel_state):
    registry = load_registry()
    lookup = build_lookup(registry)
    families = load_json(FAMILIES_PATH)
    policy = load_json(POLICY_PATH)

    active_ids = []
    missing = []

    for gid in policy.get("always_active_base_glyphs", []):
        if gid in lookup:
            active_ids.append(gid)
        else:
            missing.append(gid)

    family_scores = [(name, score_family(kernel_state, name)) for name in families.keys()]
    family_score_map = {name: score for name, score in family_scores}
    family_score_map = apply_family_bias(family_score_map, kernel_state)
    family_scores = list(family_score_map.items())
    max_families = int(policy["selection_rules"].get("max_families_per_turn", 3))
    max_glyphs_per_family = int(policy["selection_rules"].get("max_glyphs_per_family", 2))
    chosen_families = choose_top(family_scores, max_families)

    for family_name in chosen_families:
        members = [gid for gid in families.get(family_name, []) if gid in lookup]
        scored = [(gid, score_glyph(kernel_state, gid)) for gid in members]
        glyph_score_map = {gid: score for gid, score in scored}
        glyph_score_map = apply_glyph_bias(glyph_score_map, kernel_state)
        scored = list(glyph_score_map.items())
        active_ids.extend(choose_top(scored, max_glyphs_per_family))

    overlay_candidates = [gid for gid in policy.get("overlay_glyphs", []) if gid in lookup]
    scored_overlays = [(gid, score_glyph(kernel_state, gid)) for gid in overlay_candidates]
    overlay_score_map = {gid: score for gid, score in scored_overlays}
    overlay_score_map = apply_glyph_bias(overlay_score_map, kernel_state)
    scored_overlays = list(overlay_score_map.items())
    max_overlays = int(policy["selection_rules"].get("max_overlay_glyphs_per_turn", 2))
    chosen_overlays = choose_top(scored_overlays, max_overlays)
    active_ids.extend(chosen_overlays)

    seen = set()
    active_ids = [gid for gid in active_ids if not (gid in seen or seen.add(gid))]

    active_entries = [lookup[gid] for gid in active_ids if gid in lookup]

    return {
        "kernel_state": kernel_state,
        "active_glyphs": active_ids,
        "active_entries": active_entries,
        "chosen_families": chosen_families,
        "chosen_overlays": chosen_overlays,
        "preserve_full_semantics": bool(policy["selection_rules"].get("preserve_full_semantics", True)),
        "require_glyph_object_before_render": bool(policy["selection_rules"].get("require_glyph_object_before_render", True)),
        "missing_registry_ids": missing
    }

if __name__ == "__main__":
    test_kernel = {
        "time_bias": 0.7,
        "recursion": 0.9,
        "memory": 0.6,
        "pressure": 0.8,
        "stability": 0.5,
        "harmonic_528": 0.4,
        "mythic_resonance": 0.3,
        "voice_resonance": 0.2
    }
    obj = build_glyph_object(test_kernel)
    print(json.dumps(obj, indent=2, ensure_ascii=False))

# === glyph-level crystal bias ===
from runtime.crystal_glyph_bias import apply_glyph_bias

