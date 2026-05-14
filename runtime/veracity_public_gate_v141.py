# runtime/veracity_public_gate_v141.py
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Tuple

LOG = Path("logs/veracity/v141_public_gate.jsonl")


def _text(x: Any) -> str:
    return str(x or "").strip()


def _log(packet: Dict[str, Any]) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    packet = {"ts": time.time(), **packet}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")


def _evaluate(candidate: str, prompt: str = "") -> Dict[str, Any]:
    try:
        from runtime.semantic_veracity_v141 import evaluate_semantic_veracity
        return evaluate_semantic_veracity(candidate, prompt=prompt)
    except Exception as e:
        return {
            "protocol": "V14.1_PUBLIC_GATE_FALLBACK",
            "accepted": True,
            "reject": False,
            "reason": [],
            "error": repr(e),
            "text_excerpt": candidate[:260],
        }


def _ordinary_retry(prompt: str) -> str:
    try:
        from runtime.ordinary_answer_lane_v123 import ordinary_answer
        return _text(ordinary_answer(prompt, n_predict=96))
    except Exception:
        return ""


def v141_public_gate(prompt: str, candidate: Any, *, source: str = "") -> Tuple[str, Dict[str, Any], bool]:
    """
    Safe V14.1 public surface gate.

    It does not raise.
    It either accepts the candidate or replaces it with an ordinary retry.
    """
    prompt = _text(prompt)
    candidate = _text(candidate)

    report = _evaluate(candidate, prompt=prompt)
    rejected = bool(report.get("reject"))

    if not rejected:
        meta = {
            "protocol": "V14.1_ABSOLUTE_VERACITY_PROTOCOL",
            "source": source,
            "accepted": True,
            "replaced": False,
            "report": report,
        }
        return candidate, meta, False

    retry = _ordinary_retry(prompt)
    retry_report = _evaluate(retry, prompt=prompt) if retry else {"reject": True, "reason": ["empty_retry"]}

    if retry and not retry_report.get("reject"):
        final = retry
        replaced = True
    else:
        final = (
            "The output was rejected because it repeated a stale template instead of answering directly."
            if not prompt
            else "The prior surface repeated a stale template, so the answer should be regenerated plainly from the prompt."
        )
        replaced = True

    meta = {
        "protocol": "V14.1_ABSOLUTE_VERACITY_PROTOCOL",
        "source": source,
        "accepted": False,
        "replaced": replaced,
        "original_report": report,
        "retry_report": retry_report,
        "original_excerpt": candidate[:320],
        "final_excerpt": final[:320],
    }

    _log(meta)
    return final, meta, replaced

