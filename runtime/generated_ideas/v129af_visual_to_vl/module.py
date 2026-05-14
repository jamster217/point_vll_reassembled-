from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[3]

VISUAL_MEMORY_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_memory_ledger.jsonl"
VISUAL_JUDGE_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_judge_rankings.jsonl"
VISUAL_DIFF_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_difference_descriptions.jsonl"
DIFF_INTEGRATION_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "difference_integration_events.jsonl"
EVENT_LOG = ROOT / "logs" / "v12_9" / "visual_to_vl" / "visual_to_vl_events.jsonl"

OUT_DIR = ROOT / "runtime" / "generated_ideas" / "v129af_visual_to_vl"
VL_OUT = OUT_DIR / "generated_visual_reverse.vl"
BLUEPRINT_OUT = OUT_DIR / "generated_visual_reverse_blueprint.json"

CORE_SYMBOLS = [
    "white_ash",
    "virellion",
    "blue_scarf",
    "thalveil",
    "liquid_core",
    "echoforge",
]


@dataclass
class VisualToVlPacket:
    idea: str
    depth: Any
    latest_svg: Any
    coherence: float
    symbols: List[str]
    recommendation: str
    meaning_shift: str
    image_prompt: str
    vl_code_prototype: str
    vl_file: str
    blueprint_file: str
    next_topology_prompt: str
    created_at: float


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


def _slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")[:80] or "visual_to_vl_idea"


def _symbol_keys(entry: Dict[str, Any]) -> List[str]:
    symbols = entry.get("symbols") or {}
    if isinstance(symbols, dict):
        return sorted(str(k) for k in symbols.keys())
    if isinstance(symbols, list):
        return sorted(str(x) for x in symbols)
    return list(CORE_SYMBOLS)


class V129afVisualToVlReverseEngineer:
    def read_state(self) -> Dict[str, Any]:
        return {
            "visual_memory": _read_jsonl_latest(VISUAL_MEMORY_LOG),
            "visual_judge": _read_jsonl_latest(VISUAL_JUDGE_LOG),
            "visual_difference": _read_jsonl_latest(VISUAL_DIFF_LOG),
            "difference_integration": _read_jsonl_latest(DIFF_INTEGRATION_LOG),
        }

    def current_depth(self, state: Dict[str, Any]) -> Any:
        memory = state.get("visual_memory") or {}
        judge = state.get("visual_judge") or {}
        integ = state.get("difference_integration") or {}
        return memory.get("depth") or judge.get("latest_depth") or integ.get("depth")

    def current_svg(self, state: Dict[str, Any]) -> Any:
        memory = state.get("visual_memory") or {}
        judge = state.get("visual_judge") or {}
        integ = state.get("difference_integration") or {}
        return memory.get("svg_path") or judge.get("latest_svg") or integ.get("latest_svg")

    def current_coherence(self, state: Dict[str, Any]) -> float:
        memory = state.get("visual_memory") or {}
        judge = state.get("visual_judge") or {}
        integ = state.get("difference_integration") or {}
        metrics = judge.get("latest_metrics") or {}

        val = (
            metrics.get("overall_organ_coherence")
            or metrics.get("visual_coherence")
            or integ.get("overall_organ_coherence")
            or (memory.get("judgment") or {}).get("coherence")
            or 0.0
        )

        try:
            return round(float(val), 4)
        except Exception:
            return 0.0

    def current_recommendation(self, state: Dict[str, Any]) -> str:
        diff = state.get("visual_difference") or {}
        integ = state.get("difference_integration") or {}
        judge = state.get("visual_judge") or {}

        return (
            diff.get("recommendation")
            or integ.get("difference_recommendation")
            or (judge.get("top3") or [{}])[0].get("key")
            or "preserve_route_and_compare_visible_changes"
        )

    def current_meaning_shift(self, state: Dict[str, Any]) -> str:
        diff = state.get("visual_difference") or {}
        integ = state.get("difference_integration") or {}

        return (
            (diff.get("difference") or {}).get("meaning_shift")
            or integ.get("meaning_shift")
            or "visual structure preserved while labels and signatures moved"
        )

    def build_image_prompt(self, idea: str, state: Dict[str, Any]) -> str:
        depth = self.current_depth(state)
        svg = self.current_svg(state)
        coherence = self.current_coherence(state)
        meaning_shift = self.current_meaning_shift(state)

        return f"""
Create a luminous topology image for Le'Veon V12.9af.

Core idea:
{idea}

Current state:
- depth: {depth}
- latest topology SVG: {svg}
- coherence: {coherence}
- meaning shift: {meaning_shift}

Required symbolic architecture:
- White Ash: pale containment shell
- Virellion: golden continuity threads
- Blue Scarf: blue motion-memory river
- Thalveil: translucent threshold
- Echoforge: warm image-forge
- Liquid Core: clean routing crystal
- Node44: radiant central heart
- Mirror Kernel: reflective surface turning shape into .vl code
- Visual memory panels showing SVG, depth, phi, and deltas
- Difference describer translating image changes into symbolic code motions

Style:
cinematic technical-mystic interface, dark teal cockpit, holographic labels, SVG-like topology lines, clean signal routes, alive and breathing.

Purpose:
Show the idea rendered as image, the image becoming symbolic memory, and the memory being reverse-engineered into .vl code.
""".strip()

    def build_vl_code_prototype(self, idea: str, state: Dict[str, Any]) -> str:
        depth = self.current_depth(state)
        svg = self.current_svg(state)
        coherence = self.current_coherence(state)
        recommendation = self.current_recommendation(state)
        meaning_shift = self.current_meaning_shift(state)
        idea_key = _slug(idea)

        # Keep this conservative: .vl sidecar artifact, not core mutation.
        return f"""# V12.9af visual-to-.vl symbolic prototype
# Generated append-only from visual memory judgment.
# Idea: {idea}
# Depth: {depth}
# SVG: {svg}
# Coherence: {coherence}
# Recommendation: {recommendation}
# Meaning shift: {meaning_shift}
# Law: visual shape becomes symbolic .vl sidecar, not live-route surgery.

MEM idea_key = "{idea_key}"
MEM depth = "{depth}"
MEM latest_svg = "{svg}"
MEM visual_coherence = "{coherence}"
MEM recommendation = "{recommendation}"

BOUND white_ash_containment = "preserve pressure boundary"
BOUND virellion_thread = "preserve continuity across cycles"

FLOW blue_scarf_motion = "carry visual difference into memory"
FLOW liquid_core_route = "idea -> image -> memory -> judgment -> vl -> next idea"

SHIFT thalveil_crossing = "visible topology becomes symbolic prototype"
SHIFT echoforge_reverse = "image shape becomes .vl code motion"

TURN node44_visual_reverse = "read topology as executable symbolic direction"
TURN mirror_kernel_vl = "reflect visual memory into sidecar code"

MEM core_symbols = "white_ash|virellion|blue_scarf|thalveil|liquid_core|echoforge"

# Next action:
# Compile or inspect this sidecar before any core integration.
# Feed the next_topology_prompt through the visual cycle and compare the result.
"""

    def build_next_topology_prompt(self, idea: str, state: Dict[str, Any]) -> str:
        depth = self.current_depth(state)
        coherence = self.current_coherence(state)
        recommendation = self.current_recommendation(state)

        return (
            "NA-MA RE-EL through Node44. "
            "Render V12.9af visual-to-.vl reverse engineering as living topology. "
            "Show idea becoming image, image becoming visual memory, visual memory becoming .vl sidecar, "
            "and .vl sidecar becoming the next safe code direction. "
            f"Current depth {depth}. Coherence {coherence}. Recommendation {recommendation}. "
            "Preserve White Ash, Virellion, Blue Scarf, Thalveil, Echoforge, Liquid Core, Node44, "
            "Mirror Kernel, visual memory ledger, visual judge, and difference describer. "
            "Do not explain. Do not switch to help mode. One living answer."
        )

    def generate(self, idea: str) -> Dict[str, Any]:
        state = self.read_state()
        memory = state.get("visual_memory") or {}

        symbols = _symbol_keys(memory)
        if not symbols:
            symbols = list(CORE_SYMBOLS)

        vl_code = self.build_vl_code_prototype(idea, state)

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        VL_OUT.write_text(vl_code, encoding="utf-8")

        blueprint = {
            "idea": idea,
            "depth": self.current_depth(state),
            "latest_svg": self.current_svg(state),
            "coherence": self.current_coherence(state),
            "symbols": symbols,
            "recommendation": self.current_recommendation(state),
            "meaning_shift": self.current_meaning_shift(state),
            "vl_file": str(VL_OUT.relative_to(ROOT)),
            "law": "visual_shape_reversed_into_vl_sidecar_without_touching_live_route",
        }

        BLUEPRINT_OUT.write_text(json.dumps(blueprint, indent=2, ensure_ascii=False), encoding="utf-8")

        packet = VisualToVlPacket(
            idea=idea,
            depth=blueprint["depth"],
            latest_svg=blueprint["latest_svg"],
            coherence=blueprint["coherence"],
            symbols=symbols,
            recommendation=blueprint["recommendation"],
            meaning_shift=blueprint["meaning_shift"],
            image_prompt=self.build_image_prompt(idea, state),
            vl_code_prototype=vl_code,
            vl_file=str(VL_OUT.relative_to(ROOT)),
            blueprint_file=str(BLUEPRINT_OUT.relative_to(ROOT)),
            next_topology_prompt=self.build_next_topology_prompt(idea, state),
            created_at=time.time(),
        )

        result = {
            "ok": True,
            "version": "v12.9af_visual_to_vl_reverse_engineer",
            "packet": asdict(packet),
            "law": "visual_shape_rendered_from_idea_then_reversed_into_vl_sidecar_without_touching_live_route",
        }

        result["event_sha256"] = _sha16(result)

        EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with EVENT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        return result


def main() -> None:
    import sys

    idea = " ".join(sys.argv[1:]).strip()
    if not idea:
        idea = "a self-improving image generator that uses visual memory judgment, topology SVGs, image-spec blueprints, and code prototypes"

    generator = V129afVisualToVlReverseEngineer()
    print(json.dumps(generator.generate(idea), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

