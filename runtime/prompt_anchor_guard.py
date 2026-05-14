from __future__ import annotations

import re
from typing import Dict, List


STOP = {
    "the","a","an","and","or","but","if","then","than","to","of","in","on","for",
    "with","from","by","as","at","it","is","are","was","were","be","been","being",
    "do","does","did","what","why","how","who","when","where","which","that","this",
    "these","those","i","you","we","they","he","she","my","your","our","their",
    "me","him","her","them","about","into","out","over","under","again","even",
    "nothing","happening"
}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def words(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9']+", text.lower())


def anchors(prompt: str, limit: int = 8) -> List[str]:
    out: List[str] = []
    for w in words(prompt):
        if len(w) > 2 and w not in STOP and w not in out:
            out.append(w)
        if len(out) >= limit:
            break
    return out


def anchor_score(prompt: str, answer: str) -> float:
    a = anchors(prompt)
    if not a:
        return 1.0
    aw = set(words(answer))
    hits = sum(1 for x in a if x in aw)
    return round(hits / max(1, len(a)), 3)


def _third_person_phrase(rest: str) -> str:
    parts = rest.strip().split()
    if len(parts) >= 2:
        subj = parts[0]
        verb = parts[1]
        tail = " ".join(parts[2:])

        if not verb.endswith("s"):
            if verb.endswith("y") and len(verb) > 2 and verb[-2].lower() not in "aeiou":
                verb = verb[:-1] + "ies"
            elif verb.endswith(("sh", "ch", "x", "z")):
                verb = verb + "es"
            else:
                verb = verb + "s"

        out = " ".join([subj, verb, tail]).strip()
        return out[:1].upper() + out[1:]

    return rest[:1].upper() + rest[1:]


def forced_opening(prompt: str) -> str:
    p = clean(prompt).strip(" .?!:")
    low = p.lower()

    if low.startswith("why does "):
        rest = p[9:].strip()
        return f"{_third_person_phrase(rest)} because"

    if low.startswith("why do "):
        rest = p[7:].strip()
        return f"{rest[:1].upper() + rest[1:]} because"

    if low.startswith("what is "):
        rest = p[8:].strip()
        return f"{rest[:1].upper() + rest[1:]} is"

    if low.startswith("what does "):
        rest = p[10:].strip()
        return f"The useful center is what {rest} does"

    if low.startswith("how does "):
        rest = p[9:].strip()
        return f"{rest[:1].upper() + rest[1:]} by"

    if low.startswith("mirror "):
        rest = p[7:].strip()
        return f"Mirroring {rest} means"

    a = anchors(prompt, 3)
    if a:
        return "The useful center is"

    return "The useful center is"


def lower_first_for_join(text: str) -> str:
    text = clean(text)
    if not text:
        return text
    return text[:1].lower() + text[1:]


def compress(text: str, max_words: int = 95) -> str:
    text = clean(text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    text = " ".join(parts[:4]).strip()
    w = text.split()
    if len(w) > max_words:
        text = " ".join(w[:max_words]).rstrip(",;:") + "."
    return text


def anchor_answer(prompt: str, answer: str) -> str:
    answer = compress(answer)
    if not answer:
        return forced_opening(prompt)

    first = " ".join(answer.split()[:24])
    score = anchor_score(prompt, first)

    # If first line already answers the prompt, preserve it.
    if score >= 0.34:
        return strip_anchor_scaffold(answer)

    open_line = forced_opening(prompt)

    # Avoid doubled "because because".
    if open_line.lower().endswith("because") and answer.lower().startswith("because "):
        return compress(open_line + " " + answer[8:])

    return compress(open_line + " " + lower_first_for_join(answer))


def diagnose(prompt: str, answer: str) -> Dict[str, object]:
    return {
        "anchors": anchors(prompt),
        "anchor_score_full": anchor_score(prompt, answer),
        "anchor_score_first_line": anchor_score(prompt, " ".join(clean(answer).split()[:24])),
        "forced_opening": forced_opening(prompt),
    }


def strip_anchor_scaffold(text: str) -> str:
    text = clean_text(text)
    text = re.sub(r"^This answers [^:]{1,160}:\s*", "", text, flags=re.I)
    text = re.sub(r"^This is about [^:]{1,160}:\s*", "", text, flags=re.I)
    return clean_text(text)

