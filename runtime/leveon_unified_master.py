#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, time, importlib

STATE = Path("var/kernel/leveon_unified_master_state.json")

def _call(modname, funcname, *args, default=None):
    try:
        mod = importlib.import_module(modname)
        fn = getattr(mod, funcname)
        return fn(*args)
    except Exception as e:
        return default if default is not None else {"error": f"{modname}.{funcname}: {e}"}

def respond(text: str):
    text = str(text or "").strip()

    collector = _call("runtime.leveon_state_collector", "collect", default={})
    reflection = _call("runtime.reflection_gate", "pulse", text, default={"mirror_echo": text})
    emotional = _call("runtime.emotional_spiral", "absorb", text, default={})

    lineage_signal = "white_ash"
    if isinstance(collector, dict):
        lineage_signal = collector.get("dominants", {}).get("lineage_signal") or "white_ash"

    kgs = _call("runtime.kgs_field_symbol_index", "map_symbol", lineage_signal, default={})

    pressure = 0.528
    if isinstance(collector, dict):
        pressure = float(collector.get("axes", {}).get("primary_pressure", 0.528) or 0.528)

    lattice = _call("runtime.lattice_kernel_528", "project", pressure, default={})
    translated = _call("runtime.translation_bridge", "translate_bridge", text, default={"output": text})

    output = text
    if isinstance(translated, dict):
        output = translated.get("output") or text
    elif isinstance(translated, str):
        output = translated

    state_tag = "adaptive_stabilize"
    if isinstance(collector, dict):
        state_tag = collector.get("spine_hint", {}).get("state_tag", "adaptive_stabilize")

    packet = {
        "source": "runtime.leveon_unified_master",
        "input": text,
        "output": output,
        "hidden": {
            "collector": collector,
            "reflection": reflection,
            "emotional": emotional,
            "kgs": kgs,
            "lattice": lattice,
            "translation": translated,
        },
        "surface_policy": "hidden state shapes voice; public surface stays clean",
        "voice_bias": {
            "state_tag": state_tag
        },
        "updated_at": time.time(),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:]) or "symbols can mutate anchors out of alignment with signal"
    print(json.dumps(respond(prompt), indent=2, ensure_ascii=False))

