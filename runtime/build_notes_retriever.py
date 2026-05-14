#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict

ROOT = Path(".").resolve()

SEARCH_DIRS = [
    "notes",
    "reports",
    "config",
    "kernel",
    "symbolic_memory",
    "symbolic_engine",
    "modules",
    "brain",
    "var",
    "runtime",
]

EXTS = {".txt", ".md", ".json", ".py", ".vl"}

PHRASE_WEIGHTS = {
    "apex matrix": 40,
    "chronifier": 40,
    "chronfire": 40,
    "temporal beads": 40,
    "temporal bead": 36,
    "objective subjective time": 44,
    "objective subjective": 38,
    "objective time": 28,
    "subjective time": 28,
    "lattice kernel glyphs": 42,
    "lattice kernel": 30,
    "kernel glyphs": 30,
    "kernel glyph": 26,
    "compounded reasoning": 42,
    "memory retrieval": 36,
    "shape compound": 30,
    "logical sequence": 28,
    "apex": 14,
    "temporal": 8,
    "lattice": 7,
    "kernel": 7,
    "glyph": 7,
    "retrieval": 8,
    "reasoning": 8,
    "memory": 4,
    "node44": 12,
    "savariel": 12,
    "white ash": 12,
    "virellion": 12,
}

EXCLUDE_PARTS = [
    "runtime/build_notes_retriever.py",
    "build_notes_retriever.before",
    "runtime/bak/",
    "__pycache__",
    ".bak",
    "turn_dumps.jsonl",
    "full_jsonl_readout",
    "latest_v129_full_jsonl_readout",
    "read_all",
    "unified_voice.py",
    "chatroom_tinyllama.log",
]


def _query_phrases(prompt: str) -> list[str]:
    q = (prompt or "").lower()
    phrases = []

    for phrase in PHRASE_WEIGHTS:
        if phrase in q:
            phrases.append(phrase)

    # Also add meaningful words from query, but do not let them dominate.
    words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_\-]{5,}", q)
    for w in words:
        if w not in phrases:
            phrases.append(w)

    return phrases


def _allowed(path: Path) -> bool:
    rel = str(path).replace("\\", "/").lower()

    if any(x in rel for x in EXCLUDE_PARTS):
        return False

    if path.suffix.lower() not in EXTS:
        return False

    try:
        size = path.stat().st_size
    except Exception:
        return False

    if size <= 0 or size > 300_000:
        return False

    return True


def _score(rel_path: Path, text: str, query_phrases: list[str]) -> int:
    low = text.lower()
    name = str(rel_path).lower()

    score = 0
    exact_hits = 0

    # Score only phrases actually requested by the prompt.
    for phrase in query_phrases:
        if phrase in low:
            weight = PHRASE_WEIGHTS.get(phrase, 4)
            # Cap counts so giant files don't win by repetition.
            count = min(low.count(phrase), 3)
            score += weight * count
            exact_hits += 1

        if phrase in name:
            score += PHRASE_WEIGHTS.get(phrase, 4) * 2
            exact_hits += 1

    # Prefer curated note/report/config names.
    if str(rel_path).startswith(("notes/", "reports/", "config/")):
        score += 8

    # Penalize generic code that only talks about retrieval machinery.
    generic_code_markers = [
        "private_patterns",
        "public_scrub",
        "retrieval_context",
        "shape_field",
        "message_sha256",
        "answer_sha256",
    ]
    if any(x in low for x in generic_code_markers):
        score -= 40

    # Require at least one exact user-query phrase hit.
    if exact_hits == 0:
        return 0

    return max(score, 0)


def _snippet(text: str, query_phrases: list[str], width: int = 620) -> str:
    low = text.lower()

    positions = []
    for phrase in query_phrases:
        pos = low.find(phrase)
        if pos >= 0:
            positions.append(pos)

    if positions:
        pos = min(positions)
        start = max(0, pos - width // 3)
        end = min(len(text), start + width)
        return text[start:end].replace("\n", " ").strip()

    return text[:width].replace("\n", " ").strip()


def retrieve_build_notes(prompt: str, limit: int = 5) -> List[Dict[str, str]]:
    query_phrases = _query_phrases(prompt)
    if not query_phrases:
        return []

    hits = []
    scanned = 0

    for d in SEARCH_DIRS:
        base = ROOT / d
        if not base.exists():
            continue

        for path in base.rglob("*"):
            if scanned > 2600:
                break

            if not path.is_file() or not _allowed(path):
                continue

            try:
                text = path.read_text(errors="ignore")
            except Exception:
                continue

            scanned += 1
            rel = path.relative_to(ROOT)
            score = _score(rel, text, query_phrases)

            if score <= 0:
                continue

            hits.append({
                "path": str(rel),
                "score": score,
                "snippet": _snippet(text, query_phrases),
            })

    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits[:limit]

