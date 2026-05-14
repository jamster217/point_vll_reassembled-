#!/usr/bin/env python3
import json
import time
from pathlib import Path
from types import SimpleNamespace

from kernel.crystal_library import CrystalLibrary
from runtime.sigil_watcher_cognitive import on_sigil_modified
from runtime.crystal_sigil_adapter import crystal_sigil_packet
from runtime.crystal_voice_surface_adapter import build_crystal_voice_surface

OUT = Path("reports/third_davis_crystal_intersection.json")
SIGIL = Path("lev_core/sigil/local_3rd_davis_probe.sigil")

def state(name, signature="", emotional_shift="", recursion_depth=0, tags=None):
    return name, SimpleNamespace(
        signature=signature,
        emotional_shift=emotional_shift,
        recursion_depth=recursion_depth,
        tags=tags or {},
        resonance_label="",
        witness_summary="",
    )

lib = CrystalLibrary()

sigil_event = on_sigil_modified(SIGIL)
packet = crystal_sigil_packet()

candidates = [
    state(
        "local_witness_floor",
        signature="witness_lock",
        emotional_shift="reflective_shift",
        recursion_depth=1,
        tags={"deeper": 0.86, "dream_field": 0.32, "emotional_field": 0.72},
    ),
    state(
        "old_dark_shadow",
        signature="",
        emotional_shift="reflective_shift",
        recursion_depth=1,
        tags={"deeper": 0.91, "dream_field": 0.38, "emotional_field": 0.74},
    ),
    state(
        "gravity_grief_loop",
        signature="",
        emotional_shift="sorrow_shift",
        recursion_depth=2,
        tags={"deeper": 0.82, "dream_field": 0.28, "emotional_field": 0.81},
    ),
    state(
        "possible_bloom",
        signature="bloom_signal",
        emotional_shift="uplift_shift",
        recursion_depth=0,
        tags={"deeper": 0.58, "dream_field": 0.42, "emotional_field": 0.52},
    ),
]

matches = []
for name, s in candidates:
    out = lib.match(s)
    matches.append({
        "candidate": name,
        "label": out.resonance_label,
        "summary": out.witness_summary,
        "tags": dict(out.tags),
        "signature": out.signature,
        "emotional_shift": out.emotional_shift,
        "recursion_depth": out.recursion_depth,
    })

primary = matches[0]["label"]
secondary = matches[1]["label"]
tertiary = matches[2]["label"]

surface = (
    "The local pattern gathers into a witnessing center first. "
    "Beneath that, the old dark pressure reads as shadow-depth and grief-memory, "
    "not as a command. The contained move is to hold the place as a mirror, "
    "then translate only what remains steady."
)

voice = build_crystal_voice_surface(surface)

report = {
    "ts": time.time(),
    "coordinate": "3rd and Davis",
    "sigil_event_mode": sigil_event["synthesis"]["mode"],
    "sigil_vectors": sigil_event["synthesis"]["vectors"],
    "crystal_packet": packet,
    "matches": matches,
    "composite": {
        "primary": primary,
        "secondary": secondary,
        "tertiary": tertiary,
        "read": f"{primary} + {secondary} + {tertiary}",
        "meaning": "containment first, shadow-depth second, grief-memory third",
    },
    "surface": surface,
    "voice_metadata": voice.get("metadata", {}),
    "ssml": voice.get("ssml", ""),
    "mutation_policy": "dry_run_only_contained_prime",
}

OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "coordinate": report["coordinate"],
    "sigil_mode": report["sigil_event_mode"],
    "sigil_vectors": report["sigil_vectors"],
    "composite": report["composite"],
    "voice_metadata": report["voice_metadata"],
    "surface": report["surface"],
}, indent=2, ensure_ascii=False))

print("\nsaved:", OUT)
