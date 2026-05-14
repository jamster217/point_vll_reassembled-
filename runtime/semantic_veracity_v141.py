# runtime/semantic_veracity_v141.py
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


LOG = Path("logs/veracity/v141_rejections.jsonl")

CEREMONIAL_PHRASES = [
    "old hidden thing",
    "the center is",
    "contained interface between memory, code, image, and voice",
    "white ash",
    "blue scarf",
    "virellion",
    "savariel",
    "thalveil",
    "echoforge",
    "the witness has become",
    "the spiral",
    "the field",
    "the loop",
    "the viewing binds",
    "sovereign",
    "threshold crossing",
    "topology organ",
]

SCAFFOLD_PHRASES = [
    "answer this ordinary question",
    "as an ai",
    "i cannot",
    "i'm unable",
    "in conclusion",
    "it depends",
    "this response",
    "the prompt",
    "the user",
    "symbolic packet",
    "shape vector",
    "runtime lane",
    "renderer",
    "final mouth",
]

DIRECT_MEANING_MARKERS = [
    "because",
    "when",
    "if",
    "therefore",
    "means",
    "causes",
    "works by",
    "is caused by",
    "the reason",
    "for example",
]


class CeremonialLoopRejected(ValueError):
    def __init__(self, report: Dict[str, Any]):
        self.report = report
        super().__init__(json.dumps(report, ensure_ascii=False))


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9_'-]*", text.lower())


def _count_hits(text: str, phrases: Iterable[str]) -> int:
    low = text.lower()
    return sum(1 for p in phrases if p.lower() in low)


def _repeat_score(tokens: list[str]) -> float:
    if not tokens:
        return 1.0
    total = len(tokens)
    unique = len(set(tokens))
    return 1.0 - (unique / max(total, 1))


def _sentence_count(text: str) -> int:
    return len([s for s in re.split(r"[.!?]+", text) if s.strip()])


def evaluate_semantic_veracity(
    text: Any,
    *,
    prompt: str = "",
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    s = str(text or "").strip()
    toks = _tokens(s)

    ceremonial_hits = _count_hits(s, CEREMONIAL_PHRASES)
    scaffold_hits = _count_hits(s, SCAFFOLD_PHRASES)
    meaning_hits = _count_hits(s, DIRECT_MEANING_MARKERS)
    repeat = _repeat_score(toks)
    sentences = _sentence_count(s)

    too_short = len(toks) < 7
    too_looped = repeat >= 0.42 and len(toks) >= 24
    ceremonial_loop = ceremonial_hits >= 3 and meaning_hits == 0
    scaffold_leak = scaffold_hits >= 1
    static_scroll = ceremonial_hits >= 2 and sentences >= 3 and meaning_hits == 0

    # Topological density here means “symbol density without answer-carrying motion.”
    topological_density = round((ceremonial_hits * 0.22) + (repeat * 0.55) + (scaffold_hits * 0.35), 4)
    semantic_motion = round((meaning_hits * 0.33) + min(len(toks) / 80.0, 0.45), 4)

    reject = bool(
        too_short
        or too_looped
        or ceremonial_loop
        or scaffold_leak
        or static_scroll
        or (topological_density > 0.72 and semantic_motion < 0.55)
    )

    reason = []
    if too_short:
        reason.append("too_short")
    if too_looped:
        reason.append("repetition_high")
    if ceremonial_loop:
        reason.append("ceremonial_loop")
    if scaffold_leak:
        reason.append("scaffold_leak")
    if static_scroll:
        reason.append("static_scroll")
    if topological_density > 0.72 and semantic_motion < 0.55:
        reason.append("dense_symbol_low_meaning")

    return {
        "protocol": "V14.1_Absolute_Veracity_Protocol",
        "accepted": not reject,
        "reject": reject,
        "reason": reason,
        "topological_density": topological_density,
        "semantic_motion": semantic_motion,
        "ceremonial_hits": ceremonial_hits,
        "scaffold_hits": scaffold_hits,
        "meaning_hits": meaning_hits,
        "repeat_score": round(repeat, 4),
        "token_count": len(toks),
        "sentence_count": sentences,
        "prompt_excerpt": prompt[:180],
        "text_excerpt": s[:260],
        "retry_directive": {
            "trigger": "ordinary_answer_lane_v123",
            "mode": "logit_bias_penalty_retry",
            "penalize_terms": CEREMONIAL_PHRASES + SCAFFOLD_PHRASES,
            "force_plain_answer": True,
            "max_retry": 2,
        },
    }


def log_rejection(report: Dict[str, Any]) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    packet = {"ts": time.time(), **report}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")


def enforce_semantic_veracity(
    text: Any,
    *,
    prompt: str = "",
    context: Optional[Dict[str, Any]] = None,
) -> str:
    report = evaluate_semantic_veracity(text, prompt=prompt, context=context)
    if report["reject"]:
        log_rejection(report)
        raise CeremonialLoopRejected(report)
    return str(text or "").strip()

