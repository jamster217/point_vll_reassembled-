from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATTERN_FILES = [
    ROOT / "runtime" / "crystal_patterns.json",
    ROOT / "runtime" / "crystal_patterns_balancing.json",
]


def _norm(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("gri3f", "grief").replace("groef", "grief").replace("groe", "grief")
    s = re.sub(r"\s+", " ", s)
    return s


def is_concept_prompt(p: str) -> bool:
    p = _norm(p)
    return p.startswith(("what is", "what are", "how is", "how does", "why does", "why do"))


def concept_match(concepts, prompt: str) -> float:
    if not concepts:
        return 0.0
    p = _norm(prompt)
    hits = sum(1 for c in concepts if c in p)
    return hits / max(len(concepts), 1)


def keyword_overlap_score(keywords, text: str) -> float:
    if not keywords:
        return 0.0
    t = _norm(text)
    hits = sum(1 for k in keywords if _norm(k) in t)
    return hits / max(len(keywords), 1)


def template_match(pat: dict, text: str) -> float:
    t = (text or "").strip().lower()

    for template in pat.get("templates", []) or []:
        temp = template.lower()

        if temp.startswith("in relation to") and t.startswith("in relation to"):
            return 1.0

        if " is a " in temp and " is a " in t:
            return 1.0

        if temp.startswith("a tradeoff appears when") and t.startswith("a tradeoff appears when"):
            return 1.0

        if temp.startswith("stability comes from") and t.startswith("stability comes from"):
            return 1.0

        if temp.startswith("the answer stays stable when") and t.startswith("the answer stays stable when"):
            return 1.0

    if pat.get("type") == "definition":
        return 1.0 if " is " in t else 0.0

    if pat.get("type") == "relation":
        return 1.0 if t.startswith("in relation to") else 0.0

    if pat.get("type") == "balancing":
        balancing_starts = (
            "a tradeoff appears when",
            "stability comes from",
            "the answer stays stable when",
        )
        return 1.0 if t.startswith(balancing_starts) else 0.0

    return 0.0


def _specificity(pat: dict) -> tuple:
    return (
        1 if pat.get("generic") else 0,
        -(len(pat.get("concept", []) or [])),
        -(len(pat.get("keywords", []) or [])),
        pat.get("id", ""),
    )


def load_patterns(paths=None):
    files = [Path(p) for p in (paths or DEFAULT_PATTERN_FILES)]
    patterns = []

    for path in files:
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, list):
            patterns.extend(x for x in loaded if isinstance(x, dict))

    patterns.sort(key=_specificity)
    return patterns


def crystal_match(prompt: str, output: str, patterns, threshold: float = 2.0):
    best = (False, "", 0.0)

    for pat in patterns:
        c = concept_match(pat.get("concept", []), prompt)

        if c == 0.0 and not pat.get("generic"):
            continue

        k = keyword_overlap_score(pat.get("keywords", []), output)
        tm = template_match(pat, output)
        score = c + k + tm

        if score >= threshold:
            if (not best[0]) or score > best[2]:
                best = (True, pat.get("id", ""), score)

    return best

