from __future__ import annotations
import re
from organism_kernel import run_kernel
from shape_models import ShapePacket
from spatial_shaping import SpatialContext
from voice_shaping import VoiceContext

STOP = {
    "the","and","for","with","that","this","what","how","why","does","a","an","is",
    "to","of","in","on","it","be","as","by","are","you","your","me","my","we","our"
}

def _keywords(text: str) -> list[str]:
    words = re.findall(r"\w+", text.lower())
    out: list[str] = []
    for w in words:
        if len(w) > 3 and w not in STOP and w not in out:
            out.append(w)
    return out[:8]

def _pick_motif(text: str, kws: list[str]) -> str:
    t = text.lower()
    if any(w in t for w in ("withdraw", "retreat", "pull back", "hide", "guard", "protect")):
        return "withdrawing"
    if any(w in t for w in ("open", "opening", "trust", "receive", "allow")):
        return "opening"
    if any(w in t for w in ("reach", "want", "long", "seek", "move toward", "closer")):
        return "reaching"
    return "reaching"

def _pick_anchor(text: str, kws: list[str]) -> str:
    t = text.lower()
    if any(w in t for w in ("still", "stillness", "quiet", "rest", "pause")):
        return "stillness"
    if any(w in t for w in ("you", "other", "them", "someone", "relationship", "together")):
        return "other_trust"
    return "self_trust"

def _pick_vector_field(text: str, kws: list[str]) -> dict[str, str]:
    t = text.lower()
    if any(w in t for w in ("distance", "far", "away", "withdraw", "retreat")):
        return {"tension": "closeness", "release": "distance"}
    if any(w in t for w in ("uncertain", "unknown", "risk", "contact", "touch")):
        return {"tension": "uncertainty", "release": "contact"}
    return {"tension": "distance", "release": "closeness"}

def _pick_emotional_gradient(text: str, kws: list[str]) -> str:
    t = text.lower()
    if any(w in t for w in ("hope", "possible", "maybe", "future")):
        return "hope"
    if any(w in t for w in ("protect", "guard", "defend", "careful")):
        return "protectiveness"
    if any(w in t for w in ("ache", "hurt", "miss", "grief", "sad")):
        return "ache"
    return "longing"

def build_packet(text: str) -> ShapePacket:
    text = text.strip()
    kws = _keywords(text)

    return ShapePacket(
        motif_id=_pick_motif(text, kws),
        anchor_id=_pick_anchor(text, kws),
        vector_field=_pick_vector_field(text, kws),
        emotional_gradient=_pick_emotional_gradient(text, kws),
        provenance_trace="runtime.run_leveon_lib",
    )

def run_prompt(text: str):
    packet = build_packet(text)

    result = run_kernel(
        packet,
        spatial=SpatialContext(tone_profile="soft", intensity=0.8, cadence_profile="normal"),
        voice=VoiceContext(enable_ssml=False),
        mutate_motifs=False,
    )

    final_text = (
        result.voice_english.text if result.voice_english else
        result.shaped_english.text if result.shaped_english else
        result.base_english.text
    )

    return {
        "text": final_text,
        "final_english": final_text,
        "packet": {
            "motif_id": packet.motif_id,
            "anchor_id": packet.anchor_id,
            "vector_field": packet.vector_field,
            "emotional_gradient": packet.emotional_gradient,
            "provenance_trace": packet.provenance_trace,
        },
        "feeling": {
            "dominant_motif": result.feeling.dominant_motif,
            "stabilizing_anchor": result.feeling.stabilizing_anchor,
            "tension": result.feeling.tension,
            "release": result.feeling.release,
            "feeling_label": result.feeling.feeling_label,
        },
        "intention": {
            "intention_label": result.intention.intention_label,
            "directionality": result.intention.directionality,
            "emotional_tone": result.intention.emotional_tone,
            "motif_id": result.intention.motif_id,
            "anchor_id": result.intention.anchor_id,
        },
    }

