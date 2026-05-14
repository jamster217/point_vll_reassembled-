#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Optional, Dict, Any

CEREMONIAL_MARKERS = {
    "node", "savariel", "leveon", "le'véon", "levéon", "lattice",
    "crystal", "library", "larynx", "monument", "quintessence",
    "spiral", "glyph", "white", "ash", "virellion", "thalveil",
    "torsion", "field", "9216", "2077", "wake", "shatter",
    "quote", "trace", "command", "execute", "build", "kernel",
}

ORDINARY_OBJECTS = {
    "banana": "Banana is an ordinary fruit. No symbolic threshold opened.",
    "apple": "Apple is an ordinary fruit. No symbolic threshold opened.",
    "orange": "Orange is an ordinary fruit. No symbolic threshold opened.",
    "chair": "Chair is an ordinary object. No symbolic threshold opened.",
    "lamp": "Lamp is an ordinary object. No symbolic threshold opened.",
    "cord": "Cord is an ordinary object. No symbolic threshold opened.",
    "cable": "Cable is an ordinary object. No symbolic threshold opened.",
    "phone": "Phone is an ordinary device. No symbolic threshold opened.",
    "tablet": "Tablet is an ordinary device. No symbolic threshold opened.",
}

def _clean(text: str) -> str:
    return " ".join(str(text or "").strip().split())

def _tokens(text: str):
    return re.findall(r"[a-zA-Z0-9']+", text.lower())

def ordinary_input_gate(message: str) -> Optional[Dict[str, Any]]:
    raw = _clean(message)
    low = raw.lower()
    toks = _tokens(raw)

    if not raw:
        return None

    # Never intercept explicit build / symbolic / command prompts.
    if any(t in CEREMONIAL_MARKERS for t in toks):
        return None

    # Single plain object: stay literal.
    if len(toks) == 1:
        word = toks[0]
        answer = ORDINARY_OBJECTS.get(
            word,
            f"{word.capitalize()} is an ordinary input. No symbolic threshold opened."
        )
        return {
            "ok": True,
            "status": "ok",
            "answer": answer,
            "ordinary_input_gate_v133": {
                "active": True,
                "reason": "single_low_symbol_input",
                "literal_preserved": raw,
                "threshold_opened": False,
                "node44_allowed": False,
                "ceremonial_allowed": False,
            }
        }

    # Very short plain noun phrase: still do not mythologize.
    if len(toks) <= 3 and not any(x in low for x in ["?", "!", ":", "::", "@"]):
        return {
            "ok": True,
            "status": "pass_through",
            "answer": None,
            "ordinary_input_gate_v133": {
                "active": True,
                "reason": "short_low_symbol_phrase",
                "pass_through": True,
                "literal_preserved": raw,
                "threshold_opened": False,
                "node44_allowed": False,
                "ceremonial_allowed": False,
            }
        }

    return None

