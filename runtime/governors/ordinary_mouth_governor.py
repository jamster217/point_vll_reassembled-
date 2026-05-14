#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Dict, Any

LAW = "ordinary_mouth_disciplined"

BANNED_PATTERNS = [
    r"Internet lookup result:",
    r"Direct read of your prompt:",
    r"Shape read:",
    r"route narration",
    r"live mirror state",
]

CEREMONIAL_PATTERNS = [
    r"the lattice",
    r"the field",
    r"the spiral",
    r"symbolic pressure",
]

def compress_whitespace(text: str) -> str:
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()

def strip_banned(text: str) -> str:
    out = text

    for pat in BANNED_PATTERNS:
        out = re.sub(pat, "", out, flags=re.IGNORECASE)

    return out

def reduce_ceremonial_density(
    text: str,
    *,
    ordinary_mode: bool = False
) -> str:

    if not ordinary_mode:
        return text

    out = text

    replacements = {
        "the lattice": "the system",
        "the field": "the context",
        "the spiral": "the process",
        "symbolic pressure": "underlying meaning",
    }

    for k, v in replacements.items():
        out = re.sub(
            k,
            v,
            out,
            flags=re.IGNORECASE
        )

    return out

def shorten_if_needed(
    text: str,
    *,
    max_sentences: int = 5
) -> str:

    parts = re.split(r'(?<=[.!?])\s+', text)

    if len(parts) <= max_sentences:
        return text

    return " ".join(parts[:max_sentences]).strip()

def govern(
    text: str,
    *,
    ordinary_mode: bool = False,
    concise: bool = False
) -> Dict[str, Any]:

    original = text

    text = strip_banned(text)

    text = reduce_ceremonial_density(
        text,
        ordinary_mode=ordinary_mode
    )

    if concise:
        text = shorten_if_needed(text)

    text = compress_whitespace(text)

    return {
        "law": LAW,
        "original": original,
        "governed": text,
        "ordinary_mode": ordinary_mode,
        "concise": concise
    }

if __name__ == "__main__":

    sample = """
    Internet lookup result:
    The lattice carried symbolic pressure through the spiral.
    Shape read: containment 0.64
    """

    print(govern(
        sample,
        ordinary_mode=True,
        concise=True
    )["governed"])

