from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[3]

VISUAL_MEMORY_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_memory_ledger.jsonl"
VISUAL_DIFF_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_difference_descriptions.jsonl"
VISUAL_JUDGE_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_judge_rankings.jsonl"
EVENT_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "difference_integration_events.jsonl"


def _sha16(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _read_jsonl_latest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    lines = [x for x in path.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()]
    for line in reversed(lines):
        try:
            return json.loads(line)
        except Exception:
            continue
    return {}


def integrate_difference() -> Dict[str, Any]:
    memory = _read_jsonl_latest(VISUAL_MEMORY_LOG)
    diff = _read_jsonl_latest(VISUAL_DIFF_LOG)
    judge = _read_jsonl_latest(VISUAL_JUDGE_LOG)

    difference = diff.get("difference") or {}
    metrics = judge.get("latest_metrics") or {}

    result = {
        "ts": time.time(),
        "version": "v12.9ae_visual_difference_integration",
        "status": "sealed_append_only",
        "depth": memory.get("depth") or judge.get("latest_depth"),
        "latest_svg": memory.get("svg_path") or judge.get("latest_svg"),
        "topology_score": memory.get("topology_score"),
        "chamber_family": memory.get("chamber_family"),
        "judge_improvement": judge.get("improvement"),
        "judge_coherence_delta": judge.get("coherence_delta"),
        "overall_organ_coherence": metrics.get("overall_organ_coherence") or metrics.get("visual_coherence"),
        "difference_recommendation": diff.get("recommendation"),
        "meaning_shift": difference.get("meaning_shift"),
        "stable_symbols": difference.get("stable_symbols"),
        "added_symbols": difference.get("added_symbols"),
        "removed_symbols": difference.get("removed_symbols"),
        "label_delta": difference.get("label_delta"),
        "surface_fragment": diff.get("surface_fragment"),
        "law": "visual_difference_is_persistently_integrated_after_each_cycle_without_touching_live_route",
    }

    result["integration_sha256"] = _sha16(result)

    EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with EVENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    return result


def main() -> None:
    print(json.dumps(integrate_difference(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

