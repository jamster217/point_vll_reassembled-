from __future__ import annotations

print("[TRACE] entering runtime/real_reply_loop.py", flush=True)
from typing import Any, Dict, List


GENERIC_FALLBACK_LINES = [
    "The prompt is outside the current routed patterns, so the next step is to map it to the closest stable domain instead of forcing a generic answer.",
    "It carries a trace of what was already there.",
]

CIRCLING_PATTERNS = [
    "it is circling something that has not fully left.",
    "it seems to be circling something that has not fully left.",
]


def _split_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    parts = [p.strip() for p in text.replace("\n", " ").split(".")]
    return [p for p in parts if p]


def _join_sentences(parts: List[str]) -> str:
    cleaned = []
    for part in parts:
        part = (part or "").strip()
        if not part:
            continue
        if not part.endswith((".", "!", "?")):
            part += "."
        cleaned.append(part)
    return " ".join(cleaned).strip()


def _dedupe(parts: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    circling_seen = False

    for part in parts:
        norm = " ".join(part.strip().lower().split())
        if not norm:
            continue

        if any(pattern in norm for pattern in CIRCLING_PATTERNS):
            if circling_seen:
                continue
            circling_seen = True
            norm = "circling_something_not_fully_left"

        if norm in seen:
            continue

        seen.add(norm)
        out.append(part.strip())

    return out


def force_real_reply(
    input_text: str,
    reply_text: str,
    retrieval_context: Dict[str, Any] | None = None,
    emotional_bias: str = "neutral",
) -> str:
    retrieval_context = retrieval_context or {}
    episodic_memories = retrieval_context.get("episodic_memories", []) or []
    relevant_nodes = retrieval_context.get("relevant_nodes", []) or []
    previous_state = str(retrieval_context.get("previous_emotional_state", "") or "").strip()

    base_parts = _split_sentences(reply_text)
    base_parts = [
        p for p in base_parts
        if p.strip() not in GENERIC_FALLBACK_LINES
    ]
    base_parts = _dedupe(base_parts)

    anchored_parts: List[str] = []

    # 1. strongest anchor: episodic memory text
    if episodic_memories:
        top_memory = episodic_memories[0]
        excerpt = str(top_memory.get("excerpt_text", "") or "").strip()
        if excerpt:
            anchored_parts.append(f"This carries the weight of: \"{excerpt}\"")

    # 2. fallback anchor: relevant knowledge node
    if not anchored_parts and relevant_nodes:
        top_node = relevant_nodes[0]
        gloss = str(top_node.get("gloss", "") or "").strip()
        motifs = list(top_node.get("motifs", []) or [])
        if gloss:
            anchored_parts.append(f"This is close to {gloss}")
        if motifs:
            if len(motifs) >= 2:
                anchored_parts.append(f"It carries {motifs[0]} and {motifs[1]} together")
            elif len(motifs) == 1:
                anchored_parts.append(f"It carries {motifs[0]} directly")

    # 3. emotional continuity
    if previous_state and previous_state not in {"", "neutral"}:
        lowered = (input_text or "").lower()
        if previous_state in {"grief", "awe", "love", "hope", "rage"}:
            if previous_state in lowered or previous_state == emotional_bias:
                anchored_parts.append(f"There is still some {previous_state} under it")

    # 4. keep strongest remaining non-generic lines
    preserved: List[str] = []
    for part in base_parts:
        lowered = part.lower().strip()
        if lowered in [g.lower().strip(".") for g in GENERIC_FALLBACK_LINES]:
            continue
        preserved.append(part)

    final_parts = _dedupe(anchored_parts + preserved)

    # If we have a real anchor, suppress circling filler unless it's the only useful tail
    if anchored_parts:
        final_parts = [
            p for p in final_parts
            if "circling something that has not fully left" not in p.lower()
        ]

    # keep it strong and short
    return _join_sentences(final_parts[:4])

