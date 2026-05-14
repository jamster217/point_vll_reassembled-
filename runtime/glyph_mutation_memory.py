from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
SURGERY_LOG = ROOT / "logs" / "glyph_surgery" / "surgery_events.jsonl"


BAD_MARKERS = [
    "outside the current routed patterns",
    "closest stable domain",
    "forcing a generic answer",
    "carries a trace of what was already there",
    "This answers",
    "This is about",
    "The useful move is the prompt is outside",
]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def load_events(limit: int = 100) -> List[Dict[str, Any]]:
    if not SURGERY_LOG.exists():
        return []

    events: List[Dict[str, Any]] = []

    for line in SURGERY_LOG.read_text(encoding="utf-8").splitlines()[-limit:]:
        line = line.strip()
        if not line:
            continue

        try:
            obj = json.loads(line)
        except Exception:
            continue

        if obj.get("changed") and obj.get("before") and obj.get("after"):
            events.append(obj)

    return events


def prompt_tokens(text: str) -> set[str]:
    stop = {
        "the","a","an","and","or","but","to","of","in","on","for","with","from",
        "is","are","was","were","be","been","being","do","does","did","what",
        "why","how","when","where","who","that","this","it","i","you","we",
        "should","would","could","give","make","turn","explain"
    }

    return {
        w for w in re.findall(r"[A-Za-z][A-Za-z0-9']+", str(text).lower())
        if len(w) > 2 and w not in stop
    }


def overlap(a: str, b: str) -> float:
    ta = prompt_tokens(a)
    tb = prompt_tokens(b)

    if not ta or not tb:
        return 0.0

    return len(ta & tb) / max(1, len(ta | tb))


def is_bad_output(text: str) -> bool:
    low = clean(text).lower()
    return any(marker.lower() in low for marker in BAD_MARKERS)



def domain_family(text: str) -> str:
    low = clean(text).lower()

    if any(x in low for x in ["renderer", "scaffold", "drift", "first sentence", "output check", "answer starts drifting"]):
        return "renderer"

    if any(x in low for x in ["fear", "anger", "trust", "grief", "emotion", "sentimental"]):
        return "emotion"

    if any(x in low for x in ["memory", "past repair", "future reply", "reuse"]):
        return "memory"

    if any(x in low for x in ["loop", "runtime gate", "current gate", "lanes", "glyph surgery"]):
        return "runtime"

    if any(x in low for x in ["turn ", "convert ", "confusion", "pressure", "static", "signal", "structure"]):
        return "transform"

    return "general"


def renderer_repair_text(text: str) -> bool:
    low = clean(text).lower()
    return (
        "smallest useful renderer patch" in low
        or "remove exposed scaffold" in low
        or "removes scaffold phrases" in low
    )


def best_mutation_for(prompt: str, answer: str = "") -> Optional[Dict[str, Any]]:
    events = load_events()

    if not events:
        return None

    ranked = []

    for event in events:
        event_prompt = str(event.get("prompt", ""))
        event_after = str(event.get("after", ""))
        score = overlap(prompt, event_prompt)

        p_low = prompt.lower()
        ep_low = event_prompt.lower()

        prompt_domain = domain_family(prompt)
        event_domain = domain_family(event_prompt)

        # Hard domain gate:
        # Renderer/scaffold repairs must not bleed into emotional/general/runtime prompts.
        if renderer_repair_text(event_after) and prompt_domain != "renderer":
            continue

        # General underspecified repair should only apply to underspecified/general prompts.
        if "too underspecified to answer cleanly" in event_after.lower() and prompt_domain not in {"general"}:
            continue

        if prompt_domain == event_domain:
            score += 0.25
        else:
            score -= 0.20

        if answer and is_bad_output(answer):
            score += 0.25

        if "renderer" in p_low and "renderer" in ep_low:
            score += 0.35

        if "scaffold" in p_low and ("scaffold" in ep_low or "renderer" in ep_low):
            score += 0.25

        if "prompt" in p_low and "prompt" in ep_low:
            score += 0.20

        if "static" in p_low and "static" in ep_low:
            score += 0.20

        ranked.append((score, event))

    ranked.sort(key=lambda item: item[0], reverse=True)

    if ranked and ranked[0][0] >= 0.22:
        return ranked[0][1]

    return None


def apply_mutation_memory(prompt: str, answer: str) -> str:
    answer = clean(answer)

    # Do not interfere with healthy output.
    if not is_bad_output(answer):
        return answer

    event = best_mutation_for(prompt, answer)

    if event and event.get("after"):
        return clean(str(event["after"]))

    return (
        "This prompt is too underspecified to answer cleanly. "
        "Give it a concrete task, object, and success check."
    )


def memory_summary(limit: int = 10) -> str:
    events = load_events(limit=limit)

    if not events:
        return "No changed mutations available yet."

    lines = []

    for event in events[-limit:]:
        prompt = clean(str(event.get("prompt", "")))[:70]
        before = clean(str(event.get("before", "")))[:55]
        after = clean(str(event.get("after", "")))[:85]
        lines.append(f"- {prompt} :: {before} -> {after}")

    return "\n".join(lines)


if __name__ == "__main__":
    print(memory_summary())

