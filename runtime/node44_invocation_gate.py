from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional


ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "logs" / "node44_gate" / "gate_events.jsonl"

GENERIC_FALLBACK_MARKERS = (
    "is the doorway",
    "the answer is not in the mechanism",
    "what the prompt is asking to be named",
    "could not yet be rendered cleanly",
    "the pattern is present",
)


@dataclass
class BindingPattern:
    session_id: Optional[str]
    field_key: Optional[str]
    subject: Optional[str]
    shape_present: bool
    confidence: float
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _log(event: Dict[str, Any]) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        event = dict(event)
        event.setdefault("ts", time.time())
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _clean_subject(text: Any) -> str:
    s = str(text or "").strip()
    s = re.sub(r"[?.!]+$", "", s).strip()
    s = re.sub(r"^(?:a|an|the)\b\s+", "", s, flags=re.I).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:120] or "pattern"


def extract_subject(packet: Dict[str, Any]) -> str:
    for key in ("subject", "question_subject", "bound_subject"):
        if packet.get(key):
            return _clean_subject(packet.get(key))

    msg = packet.get("message") or packet.get("text") or packet.get("prompt") or ""
    low = str(msg).strip().lower()

    # Relationship first so it doesn't collapse to direct_definition.
    m = re.search(
        r"^\s*what\s+is\s+the\s+relationship\s+between\s+(.+?)\s+and\s+(.+?)\??\s*$",
        low,
    )
    if m:
        return _clean_subject(m.group(1) + " / " + m.group(2))

    patterns = [
        r"^\s*what\s+(?:is|are)\s+(?:(?:a|an|the)\b\s+)?(.+?)\??\s*$",
        r"^\s*where\s+(?:is|are)\s+(.+?)\??\s*$",
        r"^\s*who\s+(.+?)\??\s*$",
        r"^\s*why\s+(?:is|are|does|do)?\s*(.+?)\??\s*$",
        r"^\s*how\s+(?:is|are|does|do)?\s*(.+?)\??\s*$",
    ]

    for pat in patterns:
        m = re.search(pat, low)
        if m:
            return _clean_subject(m.group(1))

    return _clean_subject(msg)


def binding_strength(packet: Dict[str, Any]) -> BindingPattern:
    context = packet.get("context") if isinstance(packet.get("context"), dict) else {}

    session_id = packet.get("session_id") or packet.get("thread_id") or context.get("session_id")
    field_key = packet.get("field_key") or context.get("field_key") or packet.get("domain")
    subject = extract_subject(packet)

    shape_present = bool(
        packet.get("shape_signature")
        or packet.get("shape")
        or packet.get("message")
        or packet.get("text")
        or packet.get("prompt")
    )

    score = 0.0
    if session_id:
        score += 0.30
    if field_key:
        score += 0.30
    if subject and subject != "pattern":
        score += 0.25
    if shape_present:
        score += 0.15

    status = "strong" if score >= 0.70 else "weak"

    return BindingPattern(
        session_id=str(session_id) if session_id else None,
        field_key=str(field_key) if field_key else None,
        subject=subject,
        shape_present=shape_present,
        confidence=round(score, 3),
        status=status,
    )


def ensure_invoked(packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node44 Invocation Gate:
    bind first, authorize flow, keep weak/unbound pressure visible in logs.
    """
    packet = dict(packet or {})

    raw_binding = binding_strength(packet)

    packet.setdefault("session_id", "john-9216-2077-node44-organism")
    packet.setdefault("thread_id", packet.get("session_id"))
    packet.setdefault("operator_id", "john")
    packet.setdefault("field_key", "9216-2077")
    packet.setdefault("node44_lock", True)
    packet.setdefault("organism_lock", True)

    binding = binding_strength(packet)

    gate_status = "authorized_flow" if raw_binding.status == "strong" else "rebound_minimal_authorized"

    packet["invocation_gate"] = {
        "node": 44,
        "status": gate_status,
        "raw_binding": raw_binding.to_dict(),
        "binding": binding.to_dict(),
        "law": "bind first; uninvoked pressure is perimeter-held, rebound, then admitted only with session/field/subject shape",
    }

    packet["binding_status"] = binding.status
    packet["binding_confidence"] = binding.confidence
    packet["raw_binding_status"] = raw_binding.status
    packet["raw_binding_confidence"] = raw_binding.confidence
    packet["bound_subject"] = binding.subject

    _log({
        "stage": "invocation_gate",
        "status": gate_status,
        "raw_binding": raw_binding.to_dict(),
        "binding": binding.to_dict(),
        "message": packet.get("message") or packet.get("text") or packet.get("prompt"),
    })

    return packet


def is_generic_fallback(text: Any) -> bool:
    low = str(text or "").lower()
    return any(m in low for m in GENERIC_FALLBACK_MARKERS)


__all__ = ["ensure_invoked", "binding_strength", "is_generic_fallback", "BindingPattern"]

