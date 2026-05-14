from __future__ import annotations

from typing import Any, Dict
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "search_and_renderer_policy.json"
PROMPT_PATH = ROOT / "prompts" / "chatgpt_signal_renderer_prompt.txt"

def load_policy() -> Dict[str, Any]:
    try:
        return json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def load_renderer_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        return ""

def build_renderer_packet(
    *,
    prompt: str,
    route: str = "",
    upstream_draft: str = "",
    shape_packet: Dict[str, Any] | None = None,
    telemetry: Dict[str, Any] | None = None,
    internet_lookup: str = "",
    dream_lesson: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    return {
        "renderer_law": "external_renderer_polishes_without_replacing_signal",
        "prompt": prompt,
        "route": route,
        "upstream_draft": upstream_draft,
        "shape_packet": shape_packet or {},
        "telemetry": telemetry or {},
        "internet_lookup": internet_lookup,
        "dream_lesson": dream_lesson or {},
        "instructions": load_renderer_prompt()
    }

if __name__ == "__main__":
    print(json.dumps(build_renderer_packet(
        prompt="test",
        route="ordinary_or_symbolic",
        upstream_draft="Meaning has already formed upstream.",
        shape_packet={"containment": 0.642, "boundary": 0.5916},
        telemetry={"coherence": 0.7134}
    ), indent=2, ensure_ascii=False))

