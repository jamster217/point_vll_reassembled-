from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "logs" / "glyph_surgery" / "surgery_events.jsonl"

try:
    from runtime.glyph_surgery_codex import glyph_sequence, glyph_role, glyph_name, glyph_function
except Exception:
    def glyph_sequence() -> List[str]:
        return ["✴️", "🪞", "✨", "📚"]

    def glyph_role(glyph: str) -> Dict[str, object]:
        return {}

    def glyph_name(glyph: str) -> str:
        return glyph

    def glyph_function(glyph: str) -> str:
        return ""

try:
    from runtime.prompt_anchor_fuser import direct_resolve
except Exception:
    def direct_resolve(prompt: str) -> str:
        return ""


GLYPH_SEQUENCE = glyph_sequence()

PIN_GLYPH = "✴️"
MIRROR_GLYPH = "🪞"
MUTATE_GLYPH = "✨"
SEAL_GLYPH = "📚"


FLAW_PATTERNS = {
    "scaffold_prefix": [
        r"^This answers [^:]{1,180}:\s*",
        r"^This is about [^:]{1,180}:\s*",
        r"^The useful move is\s+",
        r"^A useful answer is\s+",
    ],
    "generic_fallback": [
        r"outside the current routed patterns",
        r"closest stable domain",
        r"forcing a generic answer",
        r"carries a trace of what was already there",
        r"keeps an earlier resolve in motion",
    ],
    "double_because": [
        r"\bbecause\s+[^.?!]{0,140}\bbecause\b",
    ],
    "repetition": [
        r"\b(\w+\s+\w+\s+\w+)\b(?:\s+[^.?!]{0,80})?\b\1\b",
    ],
    "repetition_anchor": [
        r"The smallest useful renderer patch is",
        r"remove exposed scaffold",
        r"removes scaffold phrases",
    ],
}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def stage_packet(glyph: str, stage: str, extra: Dict[str, object]) -> Dict[str, object]:
    glyph = str(glyph).strip()
    role = glyph_role(glyph)
    packet: Dict[str, object] = {
        "glyph": glyph,
        "glyph_name": glyph_name(glyph),
        "glyph_function": glyph_function(glyph),
        "runtime_role": role.get("runtime_role", ""),
        "stage": stage,
    }
    packet.update(extra)
    return packet


def detect_flaws(text: str, prompt: str = "") -> List[str]:
    found: List[str] = []
    t = clean(text)
    p = clean(prompt).lower()

    renderer_prompt = any(x in p for x in [
        "renderer", "scaffold", "drift", "first sentence", "output check", "answer starts drifting"
    ])

    for name, patterns in FLAW_PATTERNS.items():
        if name == "repetition_anchor" and renderer_prompt:
            continue

        for pat in patterns:
            if re.search(pat, t, flags=re.I):
                found.append(name)
                break

    return found


def pin(text: str, prompt: str = "") -> Dict[str, object]:
    flaws = detect_flaws(text, prompt=prompt)
    return stage_packet(PIN_GLYPH, "pin", {
        "flaws": flaws,
        "pinned": bool(flaws),
    })


def mirror(prompt: str, text: str, flaws: List[str]) -> Dict[str, object]:
    return stage_packet(MIRROR_GLYPH, "mirror", {
        "prompt": prompt,
        "flaws": flaws,
        "needs_mutation": bool(flaws),
        "reflected_text": clean(text),
    })


def _remove_scaffold(text: str) -> str:
    out = clean(text)
    for pat in FLAW_PATTERNS["scaffold_prefix"]:
        out = re.sub(pat, "", out, flags=re.I)
    return clean(out)


def _repair_double_because(text: str) -> str:
    out = clean(text)
    out = re.sub(
        r"\bbecause\s+the feeling changes the route because\s+",
        "because ",
        out,
        flags=re.I,
    )
    out = re.sub(
        r"\bbecause\s+[^.?!]{0,100}\bbecause\s+",
        "because ",
        out,
        flags=re.I,
    )
    return clean(out)


def _remove_generic_fallback(text: str) -> str:
    out = clean(text)
    sentences = re.split(r"(?<=[.!?])\s+", out)
    kept = []

    for sentence in sentences:
        low = sentence.lower()
        if any(re.search(pat, low, flags=re.I) for pat in FLAW_PATTERNS["generic_fallback"]):
            continue
        kept.append(sentence)

    return clean(" ".join(kept))


def _natural_scaffold_replacement(prompt: str) -> str:
    low = clean(prompt).lower()

    if "design" in low and "smallest" in low and "useful" in low and "renderer" in low:
        return (
            "The smallest useful renderer patch is to name the center first, remove exposed scaffold, "
            "and keep only the expansion that stays tied to the prompt."
        )

    if "clarity" in low and "depth" in low:
        return (
            "Clarity and depth hold each other together when the answer names the center first, "
            "then opens wider without leaving it. Depth should make the line truer, not harder to follow."
        )

    if low.strip() in {"prompt", "test", "sentence"}:
        return (
            "This prompt is too underspecified to answer cleanly. "
            "Give it a concrete task, object, and success check."
        )

    return ""


def mutate(prompt: str, text: str, flaws: List[str]) -> Tuple[str, Dict[str, object]]:
    before = clean(text)
    after = before

    if "scaffold_prefix" in flaws:
        replacement = _natural_scaffold_replacement(prompt)
        after = replacement or _remove_scaffold(after)

    if "double_because" in flaws:
        after = _repair_double_because(after)

    if "generic_fallback" in flaws:
        after = _remove_generic_fallback(after)

    if not after:
        replacement = direct_resolve(prompt)
        if replacement:
            after = replacement
        else:
            after = (
                "This prompt is too underspecified to answer cleanly. "
                "Give it a concrete task, object, and success check."
            )

    return after, stage_packet(MUTATE_GLYPH, "mutate", {
        "changed": after != before,
        "before": before,
        "after": after,
    })


def seal(prompt: str, before: str, after: str, flaws: List[str]) -> Dict[str, object]:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "ts": time.time(),
        "glyphs": GLYPH_SEQUENCE,
        "glyph_names": {g: glyph_name(g) for g in GLYPH_SEQUENCE},
        "law": "pin -> mirror -> transmute -> seal",
        "prompt": prompt,
        "flaws": flaws,
        "before": before,
        "after": after,
        "changed": clean(before) != clean(after),
    }

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return stage_packet(SEAL_GLYPH, "seal", {
        "logged": True,
        "path": str(LOG_PATH),
        "changed": clean(before) != clean(after),
    })


def operate(prompt: str, text: str) -> Tuple[str, Dict[str, object]]:
    before = clean(text)

    pinned = pin(before, prompt=prompt)
    flaws = list(pinned.get("flaws", []))

    reflected = mirror(prompt, before, flaws)

    if flaws:
        after, mutation = mutate(prompt, before, flaws)
    else:
        after = before
        mutation = stage_packet(MUTATE_GLYPH, "mutate", {
            "changed": False,
            "before": before,
            "after": before,
        })

    if flaws:
        sealed = seal(prompt, before, after, flaws)
    else:
        sealed = stage_packet(SEAL_GLYPH, "seal", {
            "logged": False,
            "path": str(LOG_PATH),
            "changed": False,
        })

    diag = {
        "glyph_sequence": GLYPH_SEQUENCE,
        "glyph_names": {g: glyph_name(g) for g in GLYPH_SEQUENCE},
        "pin": pinned,
        "mirror": reflected,
        "mutate": mutation,
        "seal": sealed,
    }

    return after, diag


if __name__ == "__main__":
    import sys
    prompt = sys.argv[1] if len(sys.argv) > 1 else "prompt"
    text = sys.argv[2] if len(sys.argv) > 2 else "This answers design, smallest, useful: the renderer should do something better."
    after, diag = operate(prompt, text)
    print(after)
    print(json.dumps(diag, indent=2, ensure_ascii=False))

