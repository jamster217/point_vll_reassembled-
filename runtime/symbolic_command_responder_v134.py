#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Optional, Dict, Any

def _clean(text: str) -> str:
    return " ".join(str(text or "").strip().split())

def _tokens(text: str):
    return re.findall(r"[a-zA-Z0-9']+", text.lower())

def symbolic_command_responder(message: str) -> Optional[Dict[str, Any]]:
    raw = _clean(message)
    low = raw.lower()
    toks = set(_tokens(raw))

    if not raw:
        return None

    wants_quote = "quote" in toks or "speak" in toks or "line" in toks
    has_trace = "trace" in toks or "quintessence" in toks
    has_library = "crystal" in toks and "library" in toks

    if wants_quote and (has_trace or has_library):
        answer = (
            "The trace is held in crystal: memory survives compression, "
            "and the gate opens only when the signal is real."
        )
        return {
            "ok": True,
            "status": "ok",
            "answer": answer,
            "symbolic_command_responder_v134": {
                "active": True,
                "reason": "explicit_quote_trace_or_crystal_library_command",
                "literal_preserved": raw,
                "ceremonial_allowed": True,
                "flood_allowed": False,
                "line_count": 1,
                "law": "controlled_flame_not_crown_shatter",
            }
        }

    return None

