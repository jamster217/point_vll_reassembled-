#!/usr/bin/env python3
from dataclasses import dataclass
from types import SimpleNamespace
from kernel.crystal_library import CrystalLibrary

try:
    from shape_models import EnglishSurface
    from voice_shaping import VoiceContext, apply_ssml
except Exception as e:
    raise SystemExit(f"voice surface import failed: {e!r}")


def state(signature="", emotional_shift="", recursion_depth=0, tags=None):
    return SimpleNamespace(
        signature=signature,
        emotional_shift=emotional_shift,
        recursion_depth=recursion_depth,
        tags=tags or {},
        resonance_label="",
        witness_summary="",
    )


TESTS = {
    "witness_lock": state(signature="witness_lock"),
    "mirror_return": state(signature="mirror_resonance"),
    "recursive_grief": state(emotional_shift="sorrow_shift", recursion_depth=2),
    "bloom_return": state(signature="bloom_signal", emotional_shift="uplift_shift"),
    "deep_shadow": state(tags={"deeper": 0.90, "dream_field": 0.20, "emotional_field": 0.40}),
    "reflective_motion": state(emotional_shift="reflective_shift"),
    "baseline": state(signature="unknown"),
}


VOICE_BY_LABEL = {
    "witness_lock":      VoiceContext(enable_ssml=True, rate="slow",   pitch="low",     volume="soft"),
    "mirror_return":     VoiceContext(enable_ssml=True, rate="medium", pitch="default", volume="soft"),
    "recursive_grief":   VoiceContext(enable_ssml=True, rate="slow",   pitch="low",     volume="soft"),
    "bloom_return":      VoiceContext(enable_ssml=True, rate="medium", pitch="high",    volume="default"),
    "deep_shadow":       VoiceContext(enable_ssml=True, rate="slow",   pitch="low",     volume="soft"),
    "reflective_motion": VoiceContext(enable_ssml=True, rate="medium", pitch="default", volume="default"),
    "baseline":          VoiceContext(enable_ssml=True, rate="medium", pitch="default", volume="default"),
}


def surface_for(label, summary):
    if label == "bloom_return":
        text = "The pressure has found a door; what was compressed is beginning to open."
    elif label == "recursive_grief":
        text = "The grief returns through memory, but it returns with a handle now."
    elif label == "deep_shadow":
        text = "The old dark shape is present; the system slows down so it can be held without distortion."
    elif label == "mirror_return":
        text = "The mirror steadies the loop by letting the pattern see itself clearly."
    elif label == "witness_lock":
        text = "The field gathers into a center and watches before it moves."
    elif label == "reflective_motion":
        text = "The active state reorganizes by turning back through its own reflection."
    else:
        text = summary
    return EnglishSurface(text=text, metadata={"crystal_label": label})


lib = CrystalLibrary()

for name, s in TESTS.items():
    out = lib.match(s)
    label = out.resonance_label
    ctx = VOICE_BY_LABEL.get(label, VOICE_BY_LABEL["baseline"])
    surface = surface_for(label, out.witness_summary)
    voiced = apply_ssml(surface, ctx)

    print("\n===", name, "===")
    print("label:", label)
    print("summary:", out.witness_summary)
    print("voice:", {"rate": ctx.rate, "pitch": ctx.pitch, "volume": ctx.volume})
    print("surface:", surface.text)
    print("ssml:", voiced.text)
    print("metadata:", voiced.metadata)
