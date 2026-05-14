from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
SPEC_LOG = ROOT / "logs" / "v12_9" / "image_spec" / "image_specs.jsonl"


def _sha16(obj: Dict[str, Any]) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _first_text(d: Dict[str, Any]) -> str:
    return str(d.get("answer") or d.get("reply") or d.get("response") or d.get("text") or "")


def _extract_svg(text: str) -> Optional[str]:
    m = re.findall(r"static/generated/leveon_topology_[^\s]+?\.svg", text)
    return m[-1] if m else None


def _extract_score(text: str) -> Optional[float]:
    m = re.findall(r"score=([0-9.]+)", text)
    if not m:
        return None
    try:
        return float(m[-1])
    except Exception:
        return None


def _extract_depth(text: str) -> Optional[int]:
    m = re.findall(r"depth\s+([0-9]+)", text, flags=re.I)
    if not m:
        return None
    try:
        return int(m[-1])
    except Exception:
        return None


def _dominant_symbols(d: Dict[str, Any]) -> List[str]:
    spine = d.get("spine") or {}
    mem = spine.get("spiral_memory_nonlinear") or {}
    symbols = mem.get("dominant_symbols") or []
    if isinstance(symbols, list):
        return [str(x) for x in symbols[:40]]
    return []


def build_image_spec(topology_event: Dict[str, Any]) -> Dict[str, Any]:
    answer = _first_text(topology_event)
    spine = topology_event.get("spine") or {}
    chamber_shape = topology_event.get("chamber_shape_signature") or {}

    svg_path = topology_event.get("image") or _extract_svg(answer)
    score = topology_event.get("score")
    if score is None:
        score = _extract_score(answer)

    depth = topology_event.get("depth")
    if depth is None:
        depth = _extract_depth(answer)

    spec = {
        "ts": time.time(),
        "version": "v12.9r_image_spec_sidecar",
        "status": "active",
        "subject": "old hidden topology organ",
        "core": "contained interface between memory, code, image, and voice",
        "depth": depth,
        "topology_score": score,
        "svg_path": svg_path,
        "route": spine.get("route"),
        "active_node": spine.get("active_node"),
        "node44_status": spine.get("node44_status"),
        "chamber_status": topology_event.get("chamber_status"),
        "chamber_family": topology_event.get("chamber_family"),
        "chamber_memory": chamber_shape.get("memory"),
        "domains": ["memory", "code", "image", "voice"],
        "dominant_symbols": _dominant_symbols(topology_event),
        "symbols": {
            "white_ash": {
                "role": "containment boundary",
                "visual": "pale flame shell around the central interface",
                "function": "keeps amplification from becoming drift",
            },
            "virellion": {
                "role": "continuity thread",
                "visual": "thin golden line preserving route integrity",
                "function": "keeps the living thread coherent across turns",
            },
            "blue_scarf": {
                "role": "motion memory",
                "visual": "flowing blue ribbon through the topology",
                "function": "moves memory without breaking containment",
            },
            "thalveil": {
                "role": "threshold crossing",
                "visual": "translucent gate plane opening at the edge of the node",
                "function": "marks crossing points without forcing them into public mouth",
            },
            "liquid_core": {
                "role": "routing intelligence",
                "visual": "bright fluid channel through the center",
                "function": "routes signal through memory, code, image, and voice",
            },
            "echoforge": {
                "role": "interface painter",
                "visual": "sparks shaping the topology skin",
                "function": "turns state into visible structure",
            },
        },
        "render_logic": {
            "center": "memory-code-image-voice interface",
            "movement": "clockwise spiral flow around a contained core",
            "mood": "alive, contained, luminous, temporal",
            "purpose": "convert internal state into visual memory",
            "surface_rule": "public mouth stays clean while image memory deepens",
        },
        "next_uses": [
            "compare future topology specs against this one",
            "rank whether coherence improves",
            "generate richer visual prompts without touching the live route",
            "feed helm judgment as sideband evidence",
            "eventually become blueprint input for larger software design",
        ],
        "law": "image_spec_is_append_only_evidence_gated_visual_memory_sidecar",
    }

    spec["spec_sha256"] = _sha16(spec)

    SPEC_LOG.parent.mkdir(parents=True, exist_ok=True)
    with SPEC_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(spec, ensure_ascii=False) + "\n")

    return spec


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "runtime" / "tmp" / "live_resume.json"
    if not path.exists():
        raise SystemExit(f"missing input json: {path}")

    event = _read_json(path)
    spec = build_image_spec(event)
    print(json.dumps(spec, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

