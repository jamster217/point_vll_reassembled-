#!/usr/bin/env python3
from pathlib import Path
import json, time

OUT = Path("var/leveon/state_collector_latest.json")
LOG = Path("var/leveon/state_collector_log.jsonl")

PATHS = {
    "fractal": Path("var/fractal/fractal_state.json"),
    "dream_fractal": Path("var/dream_fractal_state.json"),
    "dream_lineage": Path("var/dream/lineage_channel_state.json"),
    "dream_resonance": Path("var/dream/dream_resonance_state.json"),
    "dream_axis": Path("var/dream/dream_axis_state.json"),
    "holonomy": Path("var/holonomy/holonomy_depth_state.json"),
    "volcron_voice": Path("var/voice/volcron_voice_state.json"),
    "memory_pressure": Path("var/memory/memory_pressure_latest.json"),
    "novelty_pressure": Path("var/novelty/novelty_pressure_state.json"),
    "temporal_provenance": Path("var/temporal/temporal_provenance_state.json"),
}

def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def num(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default

def dominant(vec):
    if not isinstance(vec, dict) or not vec:
        return {"name": None, "value": 0.0}
    best = None
    best_val = -1.0
    for k, v in vec.items():
        val = num(v)
        if val > best_val:
            best = k
            best_val = val
    return {"name": best, "value": round(best_val, 3)}

def collect():
    fractal = load(PATHS["fractal"])
    dream_fractal = load(PATHS["dream_fractal"])
    dream_lineage = load(PATHS["dream_lineage"])
    dream_resonance = load(PATHS["dream_resonance"])
    dream_axis = load(PATHS["dream_axis"])
    holonomy = load(PATHS["holonomy"])
    voice = load(PATHS["volcron_voice"])
    memory_pressure = load(PATHS["memory_pressure"])
    novelty_pressure = load(PATHS["novelty_pressure"])
    temporal_provenance = load(PATHS["temporal_provenance"])

    lineage_depth = int(dream_lineage.get("lineage", {}).get("depth", 0) or 0)

    fractal_pressure = num(fractal.get("fractal_pressure"))
    dream_pressure = num(
        dream_axis.get("dream_pressure",
        dream_fractal.get("dream_pressure",
        dream_resonance.get("components", {}).get("composite", 0.0)))
    )

    shadow_lineage = num(
        dream_axis.get("shadow_lineage"),
        round(min(1.0, lineage_depth / 7.0), 3)
    )

    witness_integrity = num(
        dream_axis.get("witness_integrity"),
        0.72
    )

    max_depth = int(holonomy.get("max_depth", 1) or 1)
    cross_pass_allowed = bool(holonomy.get("cross_pass_allowed", False))

    merge_tone = fractal.get("merge_tone", {})
    dream_tone = dream_fractal.get("dream_tone", {})

    primary_pressure = round(max(
        fractal_pressure,
        dream_pressure,
        shadow_lineage,
        1.0 - witness_integrity
    ), 3)

    if max_depth <= 0:
        state_tag = "locked_observe"
    elif primary_pressure >= 0.65:
        state_tag = "weighted_containment"
    elif primary_pressure >= 0.35:
        state_tag = "adaptive_stabilize"
    else:
        state_tag = "clear_expand"

    if not cross_pass_allowed:
        recursion_mode = "single_pass"
    else:
        recursion_mode = f"cross_pass_depth_{max_depth}"

    packet = {
        "source": "runtime.leveon_state_collector",
        "updated_at": time.time(),

        "sources_present": {
            name: path.exists()
            for name, path in PATHS.items()
        },

        "axes": {
            "fractal_pressure": round(fractal_pressure, 3),
            "dream_pressure": round(dream_pressure, 3),
            "shadow_lineage": round(shadow_lineage, 3),
            "witness_integrity": round(witness_integrity, 3),
            "primary_pressure": primary_pressure,
        },

        "dominants": {
            "fractal_tone": dominant(merge_tone),
            "dream_tone": dominant(dream_tone),
            "lineage_signal": dream_lineage.get("last_signal"),
            "dream_projection": dream_fractal.get("projection"),
            "voice_emotion": voice.get("emotion"),
        },

        "holonomy": {
            "holonomy_depth_cap": holonomy.get("holonomy_depth_cap", "shallow"),
            "max_depth": max_depth,
            "cross_pass_allowed": cross_pass_allowed,
            "recursion_mode": recursion_mode,
        },

        "temporal_provenance": {
            "kind": temporal_provenance.get("kind"),
            "nodes": temporal_provenance.get("emergent_nodes"),
            "compressed_form": temporal_provenance.get("compressed_form"),
            "convergence_score": temporal_provenance.get("convergence_score"),
            "decision": temporal_provenance.get("decision"),
            "surface_rule": temporal_provenance.get("surface_rule"),
        },

        "novelty_pressure": {
            "level": novelty_pressure.get("novelty_pressure"),
            "kernel_variety": novelty_pressure.get("kernel_variety"),
            "voice_variety": novelty_pressure.get("voice_variety"),
            "total_variety": novelty_pressure.get("total_variety"),
        },

        "memory_pressure": {
            "recommended_profile": memory_pressure.get("recommended_profile"),
            "prompt_type": memory_pressure.get("prompt_type"),
            "low": memory_pressure.get("low_memory_output", {}).get("vector_profile"),
            "medium": memory_pressure.get("medium_memory_output", {}).get("vector_profile"),
            "high": memory_pressure.get("high_memory_output", {}).get("vector_profile"),
        },

        "spine_hint": {
            "state_tag": state_tag,
            "recommended_route": "observe" if max_depth <= 0 else "stabilize_then_render",
            "surface_rule": "use hidden state to shape voice, but keep public surface clean",
            "voice_bias": {
                "memory": dominant(merge_tone).get("name") == "memory",
                "dream_colored": dream_pressure > 0.25,
                "lineage_colored": shadow_lineage > 0.2,
                "deep_recursion_allowed": cross_pass_allowed and max_depth >= 3,
            }
        }
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")

    return packet

if __name__ == "__main__":
    print(json.dumps(collect(), indent=2, ensure_ascii=False))

