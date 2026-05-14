#!/usr/bin/env python3
from types import SimpleNamespace
from kernel.crystal_library import CrystalLibrary

def state(signature="", emotional_shift="", recursion_depth=0, tags=None):
    return SimpleNamespace(
        signature=signature,
        emotional_shift=emotional_shift,
        recursion_depth=recursion_depth,
        tags=tags or {},
        resonance_label="",
        witness_summary="",
    )

tests = {
    "witness_lock": state(signature="witness_lock"),
    "mirror_return": state(signature="mirror_resonance"),
    "recursive_grief": state(emotional_shift="sorrow_shift", recursion_depth=2),
    "bloom_return": state(signature="bloom_signal", emotional_shift="uplift_shift"),
    "deep_shadow": state(tags={"deeper": 0.90, "dream_field": 0.20, "emotional_field": 0.40}),
    "reflective_motion": state(emotional_shift="reflective_shift"),
    "baseline": state(signature="unknown"),
}

lib = CrystalLibrary()

for name, s in tests.items():
    out = lib.match(s)
    print(f"\n=== {name} ===")
    print("label:", out.resonance_label)
    print("summary:", out.witness_summary)
