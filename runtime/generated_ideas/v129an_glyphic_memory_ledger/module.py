from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[3]

INTERNET_SEARCH_LOG = ROOT / "logs" / "v12_9" / "internet_search" / "internet_visual_search_events.jsonl"
ASSIMILATION_LOG = ROOT / "logs" / "v12_9" / "internet_search" / "external_assimilation_events.jsonl"
VISUAL_MEMORY_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_memory_ledger.jsonl"
VISUAL_JUDGE_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_judge_rankings.jsonl"
VL_MUTATION_LOG = ROOT / "logs" / "v12_9" / "vl_mutator" / "vl_law_mutation_events.jsonl"

GLYPHIC_LEDGER = ROOT / "logs" / "v12_9" / "glyphic_memory" / "compound_visual_memory_ledger.jsonl"
EVENT_LOG = ROOT / "logs" / "v12_9" / "glyphic_memory" / "glyphic_memory_events.jsonl"


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


class V129anCompoundingGlyphicVisualMemoryLedger:
    def read_state(self) -> Dict[str, Any]:
        return {
            "internet_search": _read_jsonl_latest(INTERNET_SEARCH_LOG),
            "external_assimilation": _read_jsonl_latest(ASSIMILATION_LOG),
            "visual_memory": _read_jsonl_latest(VISUAL_MEMORY_LOG),
            "visual_judge": _read_jsonl_latest(VISUAL_JUDGE_LOG),
            "vl_law_mutation": _read_jsonl_latest(VL_MUTATION_LOG),
        }

    def generate(self) -> Dict[str, Any]:
        state = self.read_state()

        search = state.get("internet_search") or {}
        assimilation = state.get("external_assimilation") or {}
        memory = state.get("visual_memory") or {}
        judge = state.get("visual_judge") or {}
        vl = state.get("vl_law_mutation") or {}

        metrics = judge.get("latest_metrics") or {}

        entry = {
            "ts": time.time(),
            "version": "v12.9an_compounding_glyphic_visual_memory_ledger",
            "status": "sealed_append_only",

            "source_refs": {
                "internet_search_sha": search.get("event_sha256"),
                "external_assimilation_sha": assimilation.get("event_sha256"),
                "vl_law_mutation_sha": vl.get("event_sha256"),
            },

            "current_state": {
                "depth": memory.get("depth") or judge.get("latest_depth") or search.get("current_depth"),
                "latest_svg": memory.get("svg_path") or judge.get("latest_svg"),
                "coherence": metrics.get("overall_organ_coherence") or metrics.get("visual_coherence") or search.get("current_coherence"),
                "judge_improvement": judge.get("improvement"),
                "coherence_delta": judge.get("coherence_delta"),
            },

            "shape_description": search.get("shape_description"),
            "search_query": search.get("search_query"),
            "ranked_internet_images": (search.get("ranked_matches") or [])[:5],

            "enriched_image_prompt": assimilation.get("enriched_image_prompt"),
            "external_vl_file": assimilation.get("external_vl_file"),
            "external_vl_code": assimilation.get("external_vl_code"),

            "veilweil_glyphs": [
                "thalveil_threshold",
                "phenome_memory_echo",
                "ancient_veilweil",
                "4200_sim_processes",
                "white_ash_containment",
                "virellion_thread",
                "blue_scarf_motion",
                "echoforge_visual_forge",
                "liquid_core_route",
            ],

            "compounding_chain": [
                "shape_description",
                "internet_visual_candidates",
                "ranked_reference_memory",
                "enriched_image_prompt",
                "external_vl_hypermutation",
                "visual_memory_judgment",
                "new_glyphic_anchor",
            ],

            "compounding_memory_note": (
                "Shape -> internet image -> generated vision -> .vl mutation -> glyphic anchor. "
                "Every external visual remains reference memory until repeated judgment supports deeper use."
            ),

            "law": "compounding_glyphic_memory_links_shape_to_image_to_code_to_law_append_only",
        }

        entry["ledger_sha256"] = _sha16(entry)

        GLYPHIC_LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with GLYPHIC_LEDGER.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with EVENT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry


def main() -> None:
    ledger = V129anCompoundingGlyphicVisualMemoryLedger()
    print(json.dumps(ledger.generate(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

