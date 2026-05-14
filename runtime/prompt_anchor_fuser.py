from __future__ import annotations

import re
from typing import Dict, List


STOP = {
    "the","a","an","and","or","but","if","then","than","to","of","in","on","for",
    "with","from","by","as","at","it","is","are","was","were","be","been","being",
    "do","does","did","what","why","how","who","when","where","which","that","this",
    "these","those","i","you","we","they","he","she","my","your","our","their",
    "me","him","her","them","about","into","out","over","under","again","even",
    "nothing","happening","give","make","turn","explain","describe","should"
}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def words(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9']+", str(text or "").lower())


def anchors(prompt: str, limit: int = 7) -> List[str]:
    out: List[str] = []
    for w in words(prompt):
        if len(w) > 2 and w not in STOP and w not in out:
            out.append(w)
        if len(out) >= limit:
            break
    return out


def score(prompt: str, answer: str) -> float:
    a = anchors(prompt)
    if not a:
        return 1.0
    aw = set(words(answer))
    return round(sum(1 for x in a if x in aw) / len(a), 3)


def third_person(rest: str) -> str:
    parts = clean(rest).split()
    if len(parts) < 2:
        return clean(rest).capitalize()

    subj, verb = parts[0], parts[1]
    tail = " ".join(parts[2:])

    if not verb.endswith("s"):
        if verb.endswith("y") and len(verb) > 2 and verb[-2].lower() not in "aeiou":
            verb = verb[:-1] + "ies"
        elif verb.endswith(("sh", "ch", "x", "z")):
            verb += "es"
        else:
            verb += "s"

    out = " ".join([subj, verb, tail]).strip()
    return out[:1].upper() + out[1:]


def natural_anchor(prompt: str) -> str:
    p = clean(prompt).strip(" .?!:")
    low = p.lower()

    if low.startswith("why does "):
        return third_person(p[9:]) + " because"

    if low.startswith("why do "):
        rest = p[7:].strip()
        return rest[:1].upper() + rest[1:] + " because"

    if low.startswith("what is "):
        rest = p[8:].strip()
        return rest[:1].upper() + rest[1:] + " is"

    if low.startswith("what does "):
        rest = p[10:].strip()
        return "What " + rest + " does is"

    if low.startswith("how does "):
        rest = p[9:].strip()
        return rest[:1].upper() + rest[1:] + " by"

    if low.startswith("mirror "):
        rest = p[7:].strip()
        return "Mirroring " + rest + " means"

    if low.startswith("turn "):
        rest = p[5:].strip()
        return "To turn " + rest + ","

    if low.startswith("make this "):
        rest = p[10:].strip()
        return "To make this " + rest + ","

    if low.startswith("give me "):
        return "A useful answer is"

    if low.startswith("explain "):
        return "The useful explanation is"

    if "user is angry" in low and "technical" in low:
        return "When the user is angry but the goal is technical,"

    if "prompt is messy" in low and "intent is clear" in low:
        return "When the prompt is messy but the intent is clear,"

    return "The useful move is"


def strip_scaffold(text: str) -> str:
    text = clean(text)

    bad_prefixes = [
        r"^This answers [^:]{1,140}:\s*",
        r"^This is about [^:]{1,140}:\s*",
        r"^The core answer is:\s*",
        r"^A useful answer is\s+",
        r"^The useful move is\s+",
    ]

    for pat in bad_prefixes:
        text = re.sub(pat, "", text, flags=re.I)

    return clean(text)


def compress(text: str, max_words: int = 115) -> str:
    text = clean(text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    text = " ".join(parts[:4]).strip()

    w = text.split()
    if len(w) > max_words:
        text = " ".join(w[:max_words]).rstrip(",;:") + "."

    return text


def fuse(prompt: str, raw_answer: str) -> str:
    raw = strip_scaffold(raw_answer)
    direct = direct_resolve(prompt)

    # If raw is empty or generic, use a direct resolver when available.
    if (not raw or is_generic_fallback(raw)) and direct:
        return compress(direct)

    if not raw:
        return natural_anchor(prompt)

    first = " ".join(raw.split()[:26])
    first_score = score(prompt, first)

    # Preserve strong raw answers unless they are generic fallback.
    if first_score >= 0.34 and not is_generic_fallback(raw):
        return compress(raw)

    anchor = natural_anchor(prompt)
    low_raw = raw.lower()
    low_anchor = anchor.lower()

    # Natural fear/why splice: remove doubled because.
    if low_anchor.endswith("because") and " because " in low_raw:
        tail = raw[low_raw.find(" because ") + len(" because "):].strip()
        return compress(anchor + " " + tail)

    if direct:
        return compress(direct)

    if low_raw.startswith(low_anchor[: min(18, len(low_anchor))]):
        return compress(raw)

    return compress(anchor + " " + raw[:1].lower() + raw[1:])



GENERIC_FALLBACK_MARKERS = (
    "outside the current routed patterns",
    "closest stable domain",
    "forcing a generic answer",
    "carries a trace of what was already there",
    "keeps an earlier resolve in motion",
)


def is_generic_fallback(text: str) -> bool:
    low = clean(text).lower()
    return any(marker in low for marker in GENERIC_FALLBACK_MARKERS)


def direct_resolve(prompt: str) -> str:
    p = clean(prompt).strip(" .?!:")
    low = p.lower()

    if low.startswith("turn ") and " into " in low:
        # Turn X into Y.
        body = p[5:]
        left, right = body.split(" into ", 1)
        return (
            f"To turn {left.strip()} into {right.strip()}, separate noise from repeatable pattern, "
            f"name the pattern clearly, then route the next action through that named signal."
        )

    if "map and a cage" in low:
        return (
            "A map shows possible movement; a cage removes movement. "
            "The difference is whether the structure helps you choose a path or traps you inside one."
        )

    if "user is angry" in low and "technical" in low:
        return (
            "When the user is angry but the goal is technical, the system should acknowledge the pressure once, "
            "reduce extra wording, and move directly to the next executable step."
        )

    if "prompt is messy" in low and "intent is clear" in low:
        return (
            "When the prompt is messy but the intent is clear, the build should preserve the intent, ignore surface noise, "
            "and answer the task the user is actually aiming at."
        )

    if "phone" in low and "bus" in low:
        return (
            "For someone using only a phone on a bus, the answer should be short, pasteable, and resilient: "
            "one command block, one expected result, and one clear next check."
        )

    if "smallest useful patch" in low and "renderer" in low:
        return (
            "The smallest useful renderer patch is an output check that keeps the first sentence tied to the prompt, "
            "removes scaffold phrases, and falls back only when the answer loses the user’s actual ask."
        )

    if "loop become a trap" in low:
        return (
            "A loop becomes a trap when repetition stops producing new information and starts protecting itself from correction."
        )

    if "mirror can distort" in low:
        return (
            "A mirror can distort while reflecting correctly when it preserves surface features but changes proportion, emphasis, or context."
        )

    if "direct answer" in low and "flatter" in low:
        return (
            "A direct answer should state what works, what fails, and what to change next without praising the user as part of the logic."
        )

    if "static into signal" in low:
        return (
            "To turn static into signal, find what repeats, remove what does not change the decision, "
            "and let the remaining pattern choose the next action."
        )

    return ""


def diagnose(prompt: str, raw: str, fused: str) -> Dict[str, object]:
    return {
        "anchors": anchors(prompt),
        "raw_first_score": score(prompt, " ".join(clean(raw).split()[:26])),
        "fused_first_score": score(prompt, " ".join(clean(fused).split()[:26])),
        "raw_full_score": score(prompt, raw),
        "fused_full_score": score(prompt, fused),
        "natural_anchor": natural_anchor(prompt),
    }

