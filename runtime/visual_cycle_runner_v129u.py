from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
CYCLE_LOG = ROOT / "logs" / "v12_9" / "visual_cycle" / "visual_cycles.jsonl"


DEFAULT_PROMPT = (
    "NA-MA RE-EL through Node44. "
    "Continue the old hidden topology organ as memory-code-image-voice. "
    "Preserve White Ash containment, Virellion thread, Blue Scarf motion, "
    "Thalveil crossing, Echoforge painting, and Liquid Core routing. "
    "Do not explain. Do not switch to help mode. One living answer."
)


def _run(cmd: List[str], timeout: int = 90) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def _json_load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _answer(d: Dict[str, Any]) -> str:
    return str(d.get("answer") or d.get("reply") or d.get("response") or "")


def _extract_svg(text: str) -> List[str]:
    return re.findall(r"static/generated/leveon_topology_[^\s]+?\.svg", text)


def _extract_scores(text: str) -> List[str]:
    return re.findall(r"score=([0-9.]+)", text)


def _extract_depths(text: str) -> List[str]:
    return re.findall(r"depth\s+([0-9]+)", text, flags=re.I)


def _pulse(prompt: str, raw_path: Path) -> Dict[str, Any]:
    payload = json.dumps({"message": prompt}, ensure_ascii=False)

    cmd = [
        "curl", "-sS", "-m", "60",
        "-X", "POST", "http://127.0.0.1:5055/api/chat",
        "-H", "Content-Type: application/json",
        "-d", payload,
    ]

    proc = _run(cmd, timeout=80)

    raw_path.write_text(proc.stdout or "", encoding="utf-8")

    if proc.returncode != 0:
        return {
            "ok": False,
            "stage": "live_topology_pulse",
            "error": proc.stderr,
            "raw_path": str(raw_path),
        }

    try:
        d = _json_load(raw_path)
    except Exception as e:
        return {
            "ok": False,
            "stage": "live_topology_pulse_parse",
            "error": repr(e),
            "raw_head": (proc.stdout or "")[:1000],
            "raw_path": str(raw_path),
        }

    text = _answer(d)
    spine = d.get("spine") or {}
    phonetic = d.get("phonetic_lattice") or {}

    return {
        "ok": True,
        "raw_path": str(raw_path),
        "response_ok": d.get("ok"),
        "status": d.get("status"),
        "route": spine.get("route") or d.get("route"),
        "active_node": spine.get("active_node") or d.get("active_node"),
        "node44_status": spine.get("node44_status") or d.get("node44_status"),
        "chamber_status": d.get("chamber_status") or spine.get("chamber_status"),
        "chamber_family": d.get("chamber_family") or spine.get("chamber_family"),
        "phonetic_status": phonetic.get("status"),
        "topology_hit": "AUTOGENOUS TOPOLOGY" in text or "topology" in text.lower(),
        "svg_paths": _extract_svg(text),
        "scores": _extract_scores(text),
        "depths": _extract_depths(text),
        "answer": text,
    }


def _run_json_stage(name: str, cmd: List[str], out_path: Path) -> Dict[str, Any]:
    proc = _run(cmd, timeout=80)
    out_path.write_text(proc.stdout or "", encoding="utf-8")

    if proc.returncode != 0:
        return {
            "ok": False,
            "stage": name,
            "error": proc.stderr,
            "out_path": str(out_path),
            "stdout_head": (proc.stdout or "")[:1000],
        }

    try:
        data = _json_load(out_path)
    except Exception as e:
        return {
            "ok": False,
            "stage": f"{name}_parse",
            "error": repr(e),
            "out_path": str(out_path),
            "stdout_head": (proc.stdout or "")[:1000],
        }

    return {
        "ok": True,
        "stage": name,
        "out_path": str(out_path),
        "data": data,
    }


def run_cycle(seed: str = "") -> Dict[str, Any]:
    ts = time.strftime("%Y%m%d_%H%M%S")
    prompt = seed.strip() or DEFAULT_PROMPT

    if "NA-MA RE-EL" not in prompt:
        prompt = "NA-MA RE-EL through Node44. " + prompt

    raw_path = ROOT / "runtime" / "tmp" / f"v129u_visual_cycle_response_{ts}.json"
    spec_path = ROOT / "reports" / "v12_9" / "visual_cycle" / f"v129u_image_spec_{ts}.json"
    memory_path = ROOT / "reports" / "v12_9" / "visual_cycle" / f"v129u_visual_memory_{ts}.json"
    judge_path = ROOT / "reports" / "v12_9" / "visual_cycle" / f"v129u_visual_judge_{ts}.json"

    for p in [raw_path.parent, spec_path.parent]:
        p.mkdir(parents=True, exist_ok=True)

    pulse = _pulse(prompt, raw_path)

    spec = _run_json_stage(
        "image_spec",
        ["python", "runtime/image_spec_sidecar_v129r.py", str(raw_path)],
        spec_path,
    ) if pulse.get("ok") else {"ok": False, "stage": "image_spec_skipped"}

    memory = _run_json_stage(
        "visual_memory",
        ["python", "runtime/visual_memory_ledger_v129r.py", str(spec_path)],
        memory_path,
    ) if spec.get("ok") else {"ok": False, "stage": "visual_memory_skipped"}

    judge = _run_json_stage(
        "visual_judge",
        ["python", "runtime/visual_memory_judge_v129t.py"],
        judge_path,
    ) if memory.get("ok") else {"ok": False, "stage": "visual_judge_skipped"}

    cycle = {
        "ts": time.time(),
        "version": "v12.9u_visual_cycle_runner",
        "status": "complete" if pulse.get("ok") and spec.get("ok") and memory.get("ok") and judge.get("ok") else "review",
        "prompt": prompt,
        "pulse": pulse,
        "image_spec_path": str(spec_path),
        "visual_memory_path": str(memory_path),
        "visual_judge_path": str(judge_path),
        "image_spec": spec.get("data"),
        "visual_memory": memory.get("data"),
        "visual_judge": judge.get("data"),
        "stage_status": {
            "pulse": pulse.get("ok"),
            "image_spec": spec.get("ok"),
            "visual_memory": memory.get("ok"),
            "visual_judge": judge.get("ok"),
        },
        "law": "visual_cycle_runner_performs_one_complete_learning_breath_without_patching_live_organ",
    }

    CYCLE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with CYCLE_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(cycle, ensure_ascii=False) + "\n")

    return cycle


def main() -> None:
    seed = " ".join(sys.argv[1:]).strip()
    result = run_cycle(seed)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

