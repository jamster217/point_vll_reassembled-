from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

try:
    from runtime.tinyllama_client import TinyLlamaClient
except Exception:
    TinyLlamaClient = None

ROOT = Path.home() / "point_vll_reassembled"
LOG = ROOT / "logs" / "tinyllama" / "tinyllama_bridge_events.jsonl"


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def tinyllama_available() -> bool:
    return TinyLlamaClient is not None


def ask_tinyllama_variation(prompt: str, shape: Dict[str, Any] | None = None) -> str:
    """
    TinyLlama is NOT final authority.
    It only proposes compact alternate phrasing.
    Le'Veon keeps shape meaning and may ignore this.
    """
    if TinyLlamaClient is None:
        return ""

    shape = shape or {}

    instruction = (
        "Rewrite the SOURCE as one compact Le'Veon-style sentence.\\n"
        "Rules:\\n"
        "- Do not explain the task.\\n"
        "- Do not say 'Based on'.\\n"
        "- Do not mention SHAPE, SOURCE, prompt, or assistant.\\n"
        "- Do not add new facts.\\n"
        "- Preserve the exact meaning.\\n"
        "- Make it more fluid, dense, and alive.\\n"
        "- Output only the rewritten sentence.\\n\\n"
        f"SHAPE VALUES: {json.dumps(shape, ensure_ascii=False)}\\n"
        f"SOURCE SENTENCE: {prompt}\\n"
        "REWRITE ONLY:"
    )

    try:
        client = TinyLlamaClient()
        out = _clean(client.generate(instruction))
        if len(out) > 600:
            out = out[:600].rsplit(" ", 1)[0].strip()
        return out
    except Exception:
        return ""


def maybe_use_tinyllama(prompt: str, current_reply: str, shape: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Returns candidate, but only recommends use when current reply is thin.
    """
    prompt = _clean(prompt)
    current_reply = _clean(current_reply)
    shape = shape or {}

    candidate = clean_tinyllama_candidate(ask_tinyllama_variation(prompt or current_reply, shape))

    thin = (
        len(current_reply.split()) < 18
        or "outside the current routed patterns" in current_reply.lower()
        or "it carries a trace" in current_reply.lower()
    )

    recommended = bool(candidate) and thin

    event = {
        "ts": time.time(),
        "prompt": prompt,
        "current_reply": current_reply,
        "candidate": candidate,
        "recommended": recommended,
        "law": "tinyllama_suggests_only_leveon_preserves_shape",
    }

    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return event

# --- TINYLLAMA CANDIDATE FILTER / SHAPE PRESERVATION CLAMP ---
def clean_tinyllama_candidate(candidate: str) -> str:
    c = " ".join(str(candidate or "").strip().split())
    bad = [
        "based on",
        "source",
        "shape",
        "rules",
        "do not",
        "rewrite only",
        "assistant",
        "prompt",
        "```",
        "le'veon-style sentence:",
    ]
    low = c.lower()
    if not c:
        return ""
    if any(x in low for x in bad):
        return ""
    if len(c.split()) > 80:
        return ""
    return c

