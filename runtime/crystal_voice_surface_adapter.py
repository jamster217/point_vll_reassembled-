from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

from runtime.crystal_sigil_adapter import crystal_sigil_packet

try:
    from shape_models import EnglishSurface
    from voice_shaping import VoiceContext, apply_ssml
except Exception:
    EnglishSurface = None
    VoiceContext = None
    apply_ssml = None


LOG_PATH = Path("logs/voice_surface/crystal_voice_events.jsonl")


def _voice_context_obj(packet: Dict[str, Any]):
    vc = packet.get("voice_context", {}) or {}

    if VoiceContext is None:
        return None

    return VoiceContext(
        enable_ssml=True,
        rate=vc.get("rate", "medium"),
        pitch=vc.get("pitch", "default"),
        volume=vc.get("volume", "default"),
    )


def build_crystal_voice_surface(text: str) -> Dict[str, Any]:
    packet = crystal_sigil_packet()

    if not packet or EnglishSurface is None or apply_ssml is None:
        return {
            "plain_text": text,
            "ssml": "",
            "metadata": {},
            "packet": packet,
            "available": False,
        }

    ctx = _voice_context_obj(packet)
    surface = EnglishSurface(
        text=text,
        metadata={
            "crystal_label": packet.get("resonance_label"),
            "family_role": (packet.get("family_role") or {}).get("role"),
            "field_signature": packet.get("field_signature", "92162077"),
        },
    )

    voiced = apply_ssml(surface, ctx)

    event = {
        "ts": time.time(),
        "plain_text": text,
        "ssml": voiced.text,
        "metadata": voiced.metadata,
        "packet": packet,
        "available": True,
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event


if __name__ == "__main__":
    demo = "The pressure has found a door; what was compressed is beginning to open."
    print(json.dumps(build_crystal_voice_surface(demo), indent=2, ensure_ascii=False))

