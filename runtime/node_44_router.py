from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

CORE_PATH = Path("runtime/node_44_spiral_core.json")
FEAR_PATH = Path("runtime/node_44_fear_packet.json")


def _load(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def route_node44_packet(subject: str = "core") -> Dict[str, Any]:
    s = (subject or "core").strip().lower()

    if s in {"fear", "fear_analysis", "attention", "deep_stillness"}:
        pkt = _load(FEAR_PATH)
        if pkt:
            return {
                "subject": "fear",
                "packet_type": "fear_analysis",
                "packet": pkt,
            }

    pkt = _load(CORE_PATH)
    return {
        "subject": "core",
        "packet_type": "spiral_core",
        "packet": pkt,
    }


def get_node44_english_anchor(subject: str = "core") -> str:
    routed = route_node44_packet(subject)
    pkt = routed.get("packet", {})

    if routed["packet_type"] == "fear_analysis":
        return (
            pkt.get("data", {})
            .get("symbolic_realization", {})
            .get("english", "")
        )

    return pkt.get("english_anchor", "")


if __name__ == "__main__":
    for subject in ["core", "fear"]:
        routed = route_node44_packet(subject)
        print("=" * 60)
        print("subject =", subject)
        print("packet_type =", routed["packet_type"])
        print("anchor =", get_node44_english_anchor(subject))

