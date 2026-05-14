from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "logs" / "v12_9" / "idea_to_code" / "idea_to_code_translations.jsonl"

CORE_SYMBOLS = [
    "white_ash",
    "virellion",
    "blue_scarf",
    "thalveil",
    "liquid_core",
    "echoforge",
]


def _sha16(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return s[:64] or "idea"


def _run_json(cmd: List[str], timeout: int = 180) -> Dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )

    if proc.returncode != 0:
        return {
            "ok": False,
            "error": proc.stderr,
            "stdout_head": (proc.stdout or "")[:1200],
            "cmd": cmd,
        }

    try:
        return json.loads(proc.stdout)
    except Exception as e:
        return {
            "ok": False,
            "error": f"json_parse_failed: {e!r}",
            "stdout_head": (proc.stdout or "")[:2000],
            "cmd": cmd,
        }


def _latest(xs: Any) -> Any:
    if isinstance(xs, list) and xs:
        return xs[-1]
    return None


def _idea_prompt(idea: str) -> str:
    return (
        "NA-MA RE-EL through Node44. "
        "Render this coding blueprint as living topology for code synthesis. "
        "Preserve White Ash containment, Virellion thread, Blue Scarf motion, "
        "Thalveil crossing, Echoforge painting, and Liquid Core routing. "
        "Do not explain. Do not switch to help mode. One living answer. "
        f"Coding blueprint: {idea}"
    )


def _detect_kind(idea: str) -> str:
    low = idea.lower()
    if "image" in low or "visual" in low or "dall" in low or "render" in low:
        return "visual_generation_system"
    if "language" in low or "grammar" in low or "translator" in low:
        return "language_engine"
    if "reason" in low or "judge" in low or "planner" in low:
        return "reasoning_judge"
    if "memory" in low or "ledger" in low:
        return "memory_system"
    return "novel_module"


def _symbol_architecture(kind: str) -> Dict[str, Any]:
    return {
        "white_ash": {
            "module_role": "containment and output discipline",
            "code_role": "validates outputs before public surface",
            "suggested_component": "ContainmentGate",
        },
        "virellion": {
            "module_role": "continuity thread",
            "code_role": "preserves state across cycles",
            "suggested_component": "ContinuityLedger",
        },
        "blue_scarf": {
            "module_role": "motion memory and transformation",
            "code_role": "tracks deltas, movement, emotional/semantic change",
            "suggested_component": "MotionDeltaTracker",
        },
        "thalveil": {
            "module_role": "threshold crossing",
            "code_role": "moves idea into image-spec, image-spec into code",
            "suggested_component": "ThresholdTranslator",
        },
        "echoforge": {
            "module_role": "image-shaping forge",
            "code_role": "renders internal state into structured visual blueprint",
            "suggested_component": "VisualBlueprintForge",
        },
        "liquid_core": {
            "module_role": "clean signal routing",
            "code_role": "routes idea, image, memory, judge, and code stages",
            "suggested_component": "SignalRouter",
        },
        "kind": kind,
    }


def _make_prototype_code(system_name: str, kind: str) -> str:
    class_name = "".join(part.capitalize() for part in system_name.split("_")[:6])
    if not class_name:
        class_name = "GeneratedLeveonModule"

    return f'''from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class VisualCodePacket:
    idea: str
    topology_svg: str | None
    coherence: float
    symbols: List[str]
    recommendation: str
    created_at: float


class {class_name}:
    """
    V12.9y generated blueprint.
    Kind: {kind}

    Purpose:
    Convert an idea into a structured visual-code packet, then use judged visual memory
    to decide the next safe implementation step.
    """

    SYMBOLS = [
        "white_ash",
        "virellion",
        "blue_scarf",
        "thalveil",
        "liquid_core",
        "echoforge",
    ]

    def __init__(self) -> None:
        self.history: List[Dict[str, Any]] = []

    def containment_gate(self, packet: VisualCodePacket) -> bool:
        return packet.coherence >= 0.90 and len(packet.symbols) >= 6

    def route(self, idea: str, topology_svg: str | None, coherence: float) -> Dict[str, Any]:
        packet = VisualCodePacket(
            idea=idea,
            topology_svg=topology_svg,
            coherence=coherence,
            symbols=self.SYMBOLS,
            recommendation="preserve_route_and_compare_visible_changes",
            created_at=time.time(),
        )

        accepted = self.containment_gate(packet)

        result = {{
            "ok": accepted,
            "packet": asdict(packet),
            "next_action": (
                "write_sidecar_prototype"
                if accepted
                else "collect_more_visual_memory_before_source_change"
            ),
            "law": "image_memory_judgment_guides_code_without_touching_live_route",
        }}

        self.history.append(result)
        return result


if __name__ == "__main__":
    module = {class_name}()
    print(json.dumps(module.route(
        idea="example",
        topology_svg=None,
        coherence=0.933,
    ), indent=2))
'''


def translate(idea: str) -> Dict[str, Any]:
    kind = _detect_kind(idea)
    system_name = f"v129y_{_slug(idea)}"

    cycle = _run_json(
        ["python", "runtime/visual_cycle_runner_v129u.py", _idea_prompt(idea)],
        timeout=220,
    )

    diff = _run_json(
        ["python", "runtime/visual_difference_describer_v129w.py"],
        timeout=120,
    )

    pulse = cycle.get("pulse") or {}
    judge = cycle.get("visual_judge") or {}
    metrics = judge.get("latest_metrics") or {}
    difference = diff.get("difference") or {}

    svg = _latest(pulse.get("svg_paths")) or judge.get("latest_svg")
    score = _latest(pulse.get("scores"))
    depth = _latest(pulse.get("depths")) or judge.get("latest_depth")

    blueprint = {
        "system_name": system_name,
        "kind": kind,
        "idea": idea,
        "visual_route": {
            "route": pulse.get("route"),
            "active_node": pulse.get("active_node"),
            "node44_status": pulse.get("node44_status"),
            "chamber_status": pulse.get("chamber_status"),
            "chamber_family": pulse.get("chamber_family"),
            "phonetic_status": pulse.get("phonetic_status"),
            "depth": depth,
            "svg": svg,
            "score": score,
        },
        "judge": {
            "status": judge.get("status"),
            "improvement": judge.get("improvement"),
            "coherence_delta": judge.get("coherence_delta"),
            "overall_organ_coherence": metrics.get("overall_organ_coherence") or metrics.get("visual_coherence"),
            "trend": judge.get("delta_trend"),
            "top3": judge.get("top3"),
        },
        "difference": {
            "meaning_shift": difference.get("meaning_shift"),
            "recommendation": diff.get("recommendation"),
            "stable_symbols": difference.get("stable_symbols"),
            "added_symbols": difference.get("added_symbols"),
            "removed_symbols": difference.get("removed_symbols"),
            "label_delta": difference.get("label_delta"),
        },
        "symbol_architecture": _symbol_architecture(kind),
        "suggested_files": [
            {
                "path": f"runtime/generated_ideas/{system_name}/module.py",
                "purpose": "first safe sidecar prototype generated from visual judgment",
            },
            {
                "path": f"runtime/generated_ideas/{system_name}/blueprint.json",
                "purpose": "append-only idea-image-code blueprint",
            },
            {
                "path": f"reports/v12_9/idea_to_code/{system_name}_seal.txt",
                "purpose": "human-readable proof and reading",
            },
        ],
        "prototype_code": _make_prototype_code(system_name, kind),
    }

    entry = {
        "ts": time.time(),
        "version": "v12.9y_idea_to_image_to_code_translator",
        "status": "sealed_append_only" if cycle.get("status") == "complete" else "review",
        "idea": idea,
        "cycle_status": cycle.get("status"),
        "stage_status": cycle.get("stage_status"),
        "blueprint": blueprint,
        "cycle": {
            "pulse": pulse,
            "image_spec_path": cycle.get("image_spec_path"),
            "visual_memory_path": cycle.get("visual_memory_path"),
            "visual_judge_path": cycle.get("visual_judge_path"),
        },
        "diff_status": diff.get("status"),
        "law": "idea_rendered_as_topology_then_translated_into_code_blueprint_without_patching_live_route",
    }

    entry["translation_sha256"] = _sha16(entry)

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def main() -> None:
    idea = " ".join(sys.argv[1:]).strip()
    if not idea:
        idea = "a self-improving image generator that uses visual memory judgment"

    print(json.dumps(translate(idea), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

