from __future__ import annotations
import re

DIAGNOSTIC_PATTERNS = [
    r"\bThe system is treating this as.*?(?:\n\n|$)",
    r"\bIt will answer plainly first.*?(?:\n\n|$)",
    r"\bthen attach the live mirror state.*?(?:\n\n|$)",
    r"\bShape read:\s*.*$",
    r"\bcontainment\s+[0-9.]+.*$",
]

def scrub_public_larynx(text: str) -> str:
    s = str(text or "").strip()

    for pat in DIAGNOSTIC_PATTERNS:
        s = re.sub(pat, "", s, flags=re.I | re.S).strip()

    s = re.sub(r"^'([^']+)'\.\s*", "", s).strip()
    s = re.sub(r"\n{3,}", "\n\n", s).strip()

    return s or text

