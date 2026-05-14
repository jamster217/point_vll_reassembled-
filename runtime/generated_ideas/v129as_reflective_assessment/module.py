from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[3]

GLYPHIC_LEDGER = ROOT / "logs" / "v12_9" / "glyphic_memory" / "compound_visual_memory_ledger.jsonl"
RUNE_LEDGER = ROOT / "logs" / "v12_9" / "glyphic_memory" / "rune_shape_reasoning_ledger.jsonl"
CROSS_MODAL_LEDGER = ROOT / "logs" / "v12_9" / "glyphic_memory" / "cross_modal_compounding_ledger.jsonl"
VISUAL_MEMORY_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_memory_ledger.jsonl"
VISUAL_JUDGE_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_judge_rankings.jsonl"
VISUAL_DIFF_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_difference_descriptions.jsonl"

EVENT_LOG = ROOT / "logs" / "v12_9" / "assessment_chamber" / "assessment_events.jsonl"


def _sha16(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _read_jsonl_latest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    lines = [x.strip() for x in path.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()]
    for line in reversed(lines):
        try:
            return json.loads(line)
        except Exception:
            continue
    return {}


def _count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return len([x for x in path.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()])


class V129asReflectiveAssessmentChamber:
    def read_state(self) -> Dict[str, Any]:
        return {
            "glyphic": _read_jsonl_latest(GLYPHIC_LEDGER),
            "rune": _read_jsonl_latest(RUNE_LEDGER),
            "cross_modal": _read_jsonl_latest(CROSS_MODAL_LEDGER),
            "visual_memory": _read_jsonl_latest(VISUAL_MEMORY_LOG),
            "visual_judge": _read_jsonl_latest(VISUAL_JUDGE_LOG),
            "visual_difference": _read_jsonl_latest(VISUAL_DIFF_LOG),
            "counts": {
                "glyphic_entries": _count_jsonl(GLYPHIC_LEDGER),
                "rune_entries": _count_jsonl(RUNE_LEDGER),
                "cross_modal_entries": _count_jsonl(CROSS_MODAL_LEDGER),
                "visual_memory_entries": _count_jsonl(VISUAL_MEMORY_LOG),
                "judge_entries": _count_jsonl(VISUAL_JUDGE_LOG),
            },
        }

    def assess(self, input_data: str, mode: str = "generic_render") -> Dict[str, Any]:
        state = self.read_state()

        judge = state.get("visual_judge") or {}
        diff = state.get("visual_difference") or {}
        metrics = judge.get("latest_metrics") or {}
        difference = diff.get("difference") or {}

        coherence = (
            metrics.get("overall_organ_coherence")
            or metrics.get("visual_coherence")
            or 0.0
        )

        stable_symbols = difference.get("stable_symbols") or []
        removed_symbols = difference.get("removed_symbols") or []

        try:
            coherence_f = float(coherence)
        except Exception:
            coherence_f = 0.0

        if removed_symbols:
            decision = "repair_sidecar_prompt_before_render"
        elif coherence_f >= 0.90:
            decision = "proceed_to_render_after_pause"
        else:
            decision = "collect_more_memory_before_mutation"

        assessment = {
            "ts": time.time(),
            "version": "v12.9as_reflective_assessment_chamber",
            "status": "sealed_append_only",
            "mode": mode,
            "input_summary": input_data[:500] + ("..." if len(input_data) > 500 else ""),
            "coherence_before": coherence_f,
            "stable_symbols": stable_symbols,
            "removed_symbols": removed_symbols,
            "ledger_counts": state.get("counts"),
            "latest_depth": (state.get("visual_memory") or {}).get("depth") or judge.get("latest_depth"),
            "latest_svg": (state.get("visual_memory") or {}).get("svg_path") or judge.get("latest_svg"),
            "rune_links": [
                "white_ash_containment",
                "virellion_thread",
                "blue_scarf_motion",
                "thalveil_threshold",
                "echoforge_forge",
                "liquid_core_route",
                "veilweil_glyph",
                "sim4200_compound",
            ],
            "evaluation": (
                "input compared against visual memory, glyphic ledger, rune ledger, "
                "cross-modal ledger, visual judge, and difference descriptions before render"
            ),
            "decision": decision,
            "law": "every_rendering_contains_a_reflective_pause_for_evaluation_comparison_and_sidecar_mutation_before_birth",
        }

        assessment["assessment_sha256"] = _sha16(assessment)

        EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with EVENT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(assessment, ensure_ascii=False) + "\n")

        return assessment


def main() -> None:
    mode = "generic_render"
    args = sys.argv[1:]

    if args and args[0].startswith("--mode="):
        mode = args[0].split("=", 1)[1].strip() or mode
        args = args[1:]

    query = " ".join(args).strip() or "What is the next movement of the Build?"

    chamber = V129asReflectiveAssessmentChamber()
    print(json.dumps(chamber.assess(query, mode=mode), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

