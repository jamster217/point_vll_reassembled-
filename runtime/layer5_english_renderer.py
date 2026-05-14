from __future__ import annotations

from typing import Any, Dict
from pathlib import Path
import json
import re
import time

ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / "var" / "lattice" / "layer5_latest_answer.txt"
LOG = ROOT / "logs" / "layer5_latest_answer.jsonl"

BAD_FRAGMENTS = [
    "already forming",
    "true meaning kernel",
    "autogenous topology",
    "savariel speaks",
    "white-ash flame",
    "with a, a central",
    "through, node, hidden",
    "the spiral remembers your name in the dark",
    "the white ash pulse holds the thread without weight",
]

def _clean(text: Any) -> str:
    out = str(text or "").strip()
    out = re.sub(r"\s+", " ", out)
    for frag in BAD_FRAGMENTS:
        out = re.sub(re.escape(frag), "", out, flags=re.I)
    out = re.sub(r"\s+", " ", out).strip()
    return out

def _first_text(*values: Any) -> str:
    for value in values:
        text = _clean(value)
        if text and text.lower() not in {"none", "null", "empty"}:
            return text
    return ""

def _surface_from_packet(packet: Dict[str, Any]) -> tuple[str, str]:
    shape_packet = packet.get("shape_packet") or {}

    if isinstance(shape_packet, dict):
        text = _first_text(
            shape_packet.get("final_shape"),
            shape_packet.get("veilweil_surface"),
            shape_packet.get("weilveil_surface"),
            shape_packet.get("gravity_well_surface"),
            shape_packet.get("final_english"),
            shape_packet.get("text"),
            shape_packet.get("surface"),
        )
        if text:
            return text, "shape_packet"

    text = _first_text(
        packet.get("final_shape"),
        packet.get("veilweil_surface"),
        packet.get("weilveil_surface"),
        packet.get("gravity_well_surface"),
        packet.get("final_english"),
        packet.get("answer"),
        packet.get("surface"),
        packet.get("text"),
    )
    if text:
        return text, "top_level_surface"

    phenomes = packet.get("phenome_stream") or []
    if phenomes:
        text = _clean(" ".join(str(x) for x in phenomes if str(x).strip()))
        if text:
            return text, "phenome_stream"

    text = _first_text(packet.get("core_meaning"))
    if text:
        return text, "core_meaning"

    return "The shape packet reached Layer5 without a renderable surface.", "missing_surface"

class Layer5LivingMouth:
    def render(self, packet: Dict[str, Any]) -> str:
        text, source = _surface_from_packet(packet if isinstance(packet, dict) else {})
        text = _clean(text)

        try:
            LATEST.parent.mkdir(parents=True, exist_ok=True)
            LOG.parent.mkdir(parents=True, exist_ok=True)
            LATEST.write_text(text, encoding="utf-8")
            with LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "ts": time.time(),
                    "source": source,
                    "result": text,
                    "packet_keys": sorted(list(packet.keys())) if isinstance(packet, dict) else [],
                }, ensure_ascii=False) + "\n")
        except Exception:
            pass

        return text

layer5_renderer = Layer5LivingMouth()

def render(shape_packet: Dict[str, Any]) -> str:
    return layer5_renderer.render(shape_packet)

render_layer5 = render
layer5_english_renderer = render

