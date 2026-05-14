from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
IMAGE_SPEC_LOG = ROOT / "logs" / "v12_9" / "image_spec" / "image_specs.jsonl"
MEMORY_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_memory_ledger.jsonl"


def _sha16(d: Dict[str, Any]) -> str:
    raw = json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _latest_jsonl(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing jsonl: {path}")

    lines = [x for x in path.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()]
    if not lines:
        raise ValueError(f"empty jsonl: {path}")

    return json.loads(lines[-1])


def judge_visual_memory(spec: Dict[str, Any]) -> Dict[str, Any]:
    score = spec.get("topology_score")
    try:
        score = float(score)
    except Exception:
        score = 0.0

    chamber_memory = spec.get("chamber_memory")
    try:
        chamber_memory = float(chamber_memory)
    except Exception:
        chamber_memory = 0.0

    symbols = spec.get("symbols") or {}
    symbol_keys = set(symbols.keys()) if isinstance(symbols, dict) else set()

    checks = {
        "has_svg": bool(spec.get("svg_path")),
        "has_depth": spec.get("depth") is not None,
        "has_core": bool(spec.get("core")),
        "has_render_logic": bool(spec.get("render_logic")),
        "white_ash_present": "white_ash" in symbol_keys,
        "virellion_present": "virellion" in symbol_keys,
        "blue_scarf_present": "blue_scarf" in symbol_keys,
        "thalveil_present": "thalveil" in symbol_keys,
        "liquid_core_present": "liquid_core" in symbol_keys,
        "echoforge_present": "echoforge" in symbol_keys,
        "score": score,
        "chamber_memory": chamber_memory,
    }

    coherence = 0.0
    coherence += 0.15 if checks["has_svg"] else 0.0
    coherence += 0.10 if checks["has_depth"] else 0.0
    coherence += 0.10 if checks["has_core"] else 0.0
    coherence += 0.10 if checks["has_render_logic"] else 0.0
    coherence += 0.08 if checks["white_ash_present"] else 0.0
    coherence += 0.08 if checks["virellion_present"] else 0.0
    coherence += 0.07 if checks["blue_scarf_present"] else 0.0
    coherence += 0.07 if checks["thalveil_present"] else 0.0
    coherence += 0.07 if checks["liquid_core_present"] else 0.0
    coherence += 0.06 if checks["echoforge_present"] else 0.0
    coherence += min(score, 1.0) * 0.07
    coherence += min(chamber_memory, 1.0) * 0.05

    coherence = round(coherence, 4)

    if coherence >= 0.82:
        recommendation = "preserve_live_topology_route_and_begin_visual_comparison_judge"
    elif coherence >= 0.68:
        recommendation = "continue_collecting_visual_memory_before_patch"
    else:
        recommendation = "repair_image_spec_completeness_before_helm_execution"

    return {
        "coherence": coherence,
        "checks": checks,
        "recommendation": recommendation,
        "reading": "the image-spec has become visual memory and can now be judged without touching the live route",
    }


def store_visual_memory(spec: Dict[str, Any]) -> Dict[str, Any]:
    judgment = judge_visual_memory(spec)

    entry = {
        "ts": time.time(),
        "version": "v12.9r_visual_memory_ledger",
        "status": "sealed_append_only",
        "spec_sha256": spec.get("spec_sha256") or _sha16(spec),
        "subject": spec.get("subject"),
        "core": spec.get("core"),
        "depth": spec.get("depth"),
        "topology_score": spec.get("topology_score"),
        "svg_path": spec.get("svg_path"),
        "route": spec.get("route"),
        "active_node": spec.get("active_node"),
        "node44_status": spec.get("node44_status"),
        "chamber_status": spec.get("chamber_status"),
        "chamber_family": spec.get("chamber_family"),
        "chamber_memory": spec.get("chamber_memory"),
        "domains": spec.get("domains"),
        "dominant_symbols": spec.get("dominant_symbols"),
        "symbols": spec.get("symbols"),
        "render_logic": spec.get("render_logic"),
        "judgment": judgment,
        "helm_use": {
            "can_rank": True,
            "feeds": [
                "text_response",
                "svg_path",
                "image_spec",
                "visual_memory",
                "ghost_logs",
                "resonance_traces",
            ],
            "next_question": "Did the visual memory improve coherence without choking the topology organ?",
        },
        "law": "visual_memory_is_append_only_evidence_gated_and_helm_readable",
    }

    entry["entry_sha256"] = _sha16(entry)

    MEMORY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def main() -> None:
    if len(sys.argv) > 1:
        spec = _load_json(Path(sys.argv[1]))
    else:
        spec = _latest_jsonl(IMAGE_SPEC_LOG)

    entry = store_visual_memory(spec)
    print(json.dumps(entry, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

