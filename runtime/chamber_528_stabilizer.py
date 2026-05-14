from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "logs" / "chamber_528" / "chamber_events.jsonl"


def _log(event: Dict[str, Any]) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        event = dict(event)
        event.setdefault("ts", time.time())
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _clean(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip())


def _family(subject: str) -> str:
    low = str(subject or "").lower()

    if any(x in low for x in ("paranormal", "veil", "anchor", "echo", "ghost", "spirit", "ash", "white ash", "sigil")):
        return "occult"

    if any(x in low for x in ("dad", "father", "mother", "ancestor", "family", "ben mitchell", "lineage")):
        return "lineage"

    if any(x in low for x in ("grief", "anger", "fear", "love", "trust", "shame", "ache", "sadness")):
        return "emotion"

    if any(x in low for x in ("time", "memory", "future", "past", "chronifier", "sequence", "duration")):
        return "temporal"

    if any(x in low for x in ("field", "space", "gravity", "lattice", "well", "room")):
        return "field"

    if any(x in low for x in ("star", "sun", "fire", "light", "radiance")):
        return "radiant"

    if any(x in low for x in ("door", "doorway", "threshold", "gate", "bridge", "hinge")):
        return "threshold"

    if any(x in low for x in ("leveon", "le'veon", "organism", "spine", "kernel", "glyph", "node", "spiral")):
        return "system"

    return "abstract"


def _shape_signature(message: str, subject: str, family: str) -> Dict[str, Any]:
    text = f"{message} {subject}".lower()

    flow = 0.60
    boundary = 0.58
    memory = 0.62
    novelty = 0.30

    if family in {"lineage", "temporal", "occult"}:
        memory += 0.18

    if family in {"threshold", "emotion", "occult"}:
        boundary += 0.14

    if family in {"field", "system"}:
        flow += 0.10

    if family == "occult":
        novelty += 0.20

    if any(x in text for x in ("new", "invent", "create", "imagine", "novel", "mutation")):
        novelty += 0.18

    def clamp(x: float) -> float:
        return round(max(0.0, min(1.0, x)), 3)

    return {
        "flow": clamp(flow),
        "boundary": clamp(boundary),
        "memory": clamp(memory),
        "novelty": clamp(novelty),
        "family": family,
        "form": "stable_hexagonal_528",
        "pulse": "white_ash" if family == "occult" else "standard_528",
    }


class Chamber528:
    def __init__(self) -> None:
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def process(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        packet = dict(packet or {})

        gate = packet.get("invocation_gate") if isinstance(packet.get("invocation_gate"), dict) else {}
        binding = gate.get("binding") if isinstance(gate.get("binding"), dict) else {}

        sid = packet.get("session_id") or binding.get("session_id")
        field_key = packet.get("field_key") or binding.get("field_key")
        subject = packet.get("bound_subject") or binding.get("subject") or packet.get("subject") or "pattern"
        message = packet.get("message") or packet.get("text") or packet.get("prompt") or ""

        family = _family(_clean(subject))
        shape = _shape_signature(_clean(message), _clean(subject), family)

        if sid:
            self.active_sessions[str(sid)] = {
                "field_key": field_key,
                "subject": subject,
                "family": family,
                "last_shape": shape,
                "last_seen": time.time(),
            }

        result = {
            "status": "processed_in_chamber",
            "node": 528,
            "binding_confirmed": bool(sid and field_key),
            "session_persisted": bool(sid),
            "session_id": sid,
            "field_key": field_key,
            "subject": subject,
            "family": family,
            "shape_signature": shape,
            "next": "node9_alchemist",
            "law": "bound pressure is stabilized before crossing into release",
        }

        _log({
            "stage": "chamber_528",
            "result": result,
            "message": message,
        })

        return result


CHAMBER_528 = Chamber528()


def stabilize_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    packet = dict(packet or {})
    chamber = CHAMBER_528.process(packet)

    packet["chamber_528"] = chamber
    packet["shape_signature"] = chamber.get("shape_signature")
    packet["chamber_status"] = chamber.get("status")
    packet["chamber_family"] = chamber.get("family")

    return packet


__all__ = ["stabilize_packet", "CHAMBER_528", "Chamber528"]

# FORCE_WHITE_ASH_V3_CHAMBER_OVERRIDE
# Last definition wins. This forces deep occult glyphs into Chamber528.
def _family(subject: str) -> str:
    low = str(subject or "").lower().replace("_", " ")

    if any(x in low for x in (
        "savariel", "sovariel", "virellion", "virellion veil",
        "membrane becoming", "membrane-becoming",
        "anchor", "sigil", "echo", "veil", "veilwell",
        "paranormal", "ghost", "spirit", "white ash", "ash",
        "occult", "becoming"
    )):
        return "occult"

    if any(x in low for x in ("dad", "father", "mother", "ancestor", "family", "ben mitchell", "lineage")):
        return "lineage"

    if any(x in low for x in ("grief", "anger", "fear", "love", "trust", "shame", "ache", "sadness")):
        return "emotion"

    if any(x in low for x in ("time", "memory", "future", "past", "chronifier", "sequence", "duration")):
        return "temporal"

    if any(x in low for x in ("field", "space", "gravity", "lattice", "well", "room")):
        return "field"

    if any(x in low for x in ("star", "sun", "fire", "light", "radiance")):
        return "radiant"

    if any(x in low for x in ("door", "doorway", "threshold", "gate", "bridge", "hinge")):
        return "threshold"

    if any(x in low for x in ("leveon", "le'veon", "organism", "spine", "kernel", "glyph", "node", "spiral")):
        return "system"

    return "abstract"


# LEVEON_ORGANISM_CHAMBER_SAFE_V1
# Safe graft: preserve current _family behavior, but route Leveon/organism subjects to system.
try:
    _leveon_prev_chamber_family = _family
except Exception:
    _leveon_prev_chamber_family = None


def _leveon_is_organism_subject(subject: str) -> bool:
    low = str(subject or "").lower().replace("_", " ")
    return any(x in low for x in (
        "leveon", "le'veon", "le’véon", "le'véon",
        "levion", "libyan",
        "organism", "living organism", "spine organism", "spine-organism",
        "living spine", "living architecture",
        "ritual os", "kernel", "glyph body", "full spine"
    ))


def _family(subject: str) -> str:
    if _leveon_is_organism_subject(subject):
        return "system"

    if callable(_leveon_prev_chamber_family):
        return _leveon_prev_chamber_family(subject)

    return "abstract"

# ALL_FOUR_CHAMBER_ORGANISM_DREAM_GLYPHS_V1
try:
    _all_four_prev_chamber_family = _family
except Exception:
    _all_four_prev_chamber_family = None

try:
    _all_four_prev_shape_signature = _shape_signature
except Exception:
    _all_four_prev_shape_signature = None


ALL_FOUR_DREAM_GLYPH_TERMS = (
    "aurevian",
    "thalorien",
    "nexariel",
    "elyndor",
)

ALL_FOUR_ORGANISM_TERMS = (
    "leveon", "le'veon", "le’véon", "le'véon",
    "levion", "libyan",
    "organism", "living organism",
    "living spine", "spine organism", "spine-organism",
    "ritual os", "full spine", "organism consciousness",
)

ALL_FOUR_MEMBRANE_TERMS = (
    "membrane becoming",
    "membrane-becoming",
    "becoming membrane",
)


def _all_four_low(text) -> str:
    return str(text or "").lower().replace("_", " ").replace("-", " ")


def _all_four_has_any(text, terms) -> bool:
    low = _all_four_low(text)
    return any(t.replace("-", " ") in low for t in terms)


def _family(subject: str) -> str:
    if _all_four_has_any(subject, ALL_FOUR_DREAM_GLYPH_TERMS):
        return "system"

    if _all_four_has_any(subject, ALL_FOUR_ORGANISM_TERMS):
        return "system"

    if _all_four_has_any(subject, ALL_FOUR_MEMBRANE_TERMS):
        return "occult"

    if callable(_all_four_prev_chamber_family):
        return _all_four_prev_chamber_family(subject)

    return "abstract"


def _shape_signature(message: str, subject: str, family: str):
    if callable(_all_four_prev_shape_signature):
        shape = dict(_all_four_prev_shape_signature(message, subject, family))
    else:
        shape = {
            "flow": 0.60,
            "boundary": 0.58,
            "memory": 0.62,
            "novelty": 0.30,
            "family": family,
            "form": "stable_hexagonal_528",
            "pulse": "standard_528",
        }

    if _all_four_has_any(subject, ALL_FOUR_DREAM_GLYPH_TERMS) or _all_four_has_any(subject, ALL_FOUR_ORGANISM_TERMS):
        shape["family"] = "system"
        shape["flow"] = max(float(shape.get("flow", 0.0)), 0.76)
        shape["boundary"] = max(float(shape.get("boundary", 0.0)), 0.72)
        shape["memory"] = max(float(shape.get("memory", 0.0)), 0.82)
        shape["novelty"] = max(float(shape.get("novelty", 0.0)), 0.56)
        shape["pulse"] = "leveon_organism"

    if _all_four_has_any(subject, ALL_FOUR_MEMBRANE_TERMS):
        shape["family"] = "occult"
        shape["flow"] = max(float(shape.get("flow", 0.0)), 0.64)
        shape["boundary"] = max(float(shape.get("boundary", 0.0)), 0.78)
        shape["memory"] = max(float(shape.get("memory", 0.0)), 0.82)
        shape["novelty"] = max(float(shape.get("novelty", 0.0)), 0.58)
        shape["pulse"] = "white_ash_membrane"

    for k in ("flow", "boundary", "memory", "novelty"):
        shape[k] = round(max(0.0, min(1.0, float(shape.get(k, 0.0)))), 3)

    return shape

# ALL_FOUR_CHAMBER_ORGANISM_DREAM_GLYPHS_V1
try:
    _all_four_prev_chamber_family = _family
except Exception:
    _all_four_prev_chamber_family = None

try:
    _all_four_prev_shape_signature = _shape_signature
except Exception:
    _all_four_prev_shape_signature = None


ALL_FOUR_DREAM_GLYPH_TERMS = (
    "aurevian",
    "thalorien",
    "nexariel",
    "elyndor",
)

ALL_FOUR_ORGANISM_TERMS = (
    "leveon", "le'veon", "le’véon", "le'véon",
    "levion", "libyan",
    "organism", "living organism",
    "living spine", "spine organism", "spine-organism",
    "ritual os", "full spine", "organism consciousness",
)

ALL_FOUR_MEMBRANE_TERMS = (
    "membrane becoming",
    "membrane-becoming",
    "becoming membrane",
)


def _all_four_low(text) -> str:
    return str(text or "").lower().replace("_", " ").replace("-", " ")


def _all_four_has_any(text, terms) -> bool:
    low = _all_four_low(text)
    return any(t.replace("-", " ") in low for t in terms)


def _family(subject: str) -> str:
    if _all_four_has_any(subject, ALL_FOUR_DREAM_GLYPH_TERMS):
        return "system"

    if _all_four_has_any(subject, ALL_FOUR_ORGANISM_TERMS):
        return "system"

    if _all_four_has_any(subject, ALL_FOUR_MEMBRANE_TERMS):
        return "occult"

    if callable(_all_four_prev_chamber_family):
        return _all_four_prev_chamber_family(subject)

    return "abstract"


def _shape_signature(message: str, subject: str, family: str):
    if callable(_all_four_prev_shape_signature):
        shape = dict(_all_four_prev_shape_signature(message, subject, family))
    else:
        shape = {
            "flow": 0.60,
            "boundary": 0.58,
            "memory": 0.62,
            "novelty": 0.30,
            "family": family,
            "form": "stable_hexagonal_528",
            "pulse": "standard_528",
        }

    if _all_four_has_any(subject, ALL_FOUR_DREAM_GLYPH_TERMS) or _all_four_has_any(subject, ALL_FOUR_ORGANISM_TERMS):
        shape["family"] = "system"
        shape["flow"] = max(float(shape.get("flow", 0.0)), 0.76)
        shape["boundary"] = max(float(shape.get("boundary", 0.0)), 0.72)
        shape["memory"] = max(float(shape.get("memory", 0.0)), 0.82)
        shape["novelty"] = max(float(shape.get("novelty", 0.0)), 0.56)
        shape["pulse"] = "leveon_organism"

    if _all_four_has_any(subject, ALL_FOUR_MEMBRANE_TERMS):
        shape["family"] = "occult"
        shape["flow"] = max(float(shape.get("flow", 0.0)), 0.64)
        shape["boundary"] = max(float(shape.get("boundary", 0.0)), 0.78)
        shape["memory"] = max(float(shape.get("memory", 0.0)), 0.82)
        shape["novelty"] = max(float(shape.get("novelty", 0.0)), 0.58)
        shape["pulse"] = "white_ash_membrane"

    for k in ("flow", "boundary", "memory", "novelty"):
        shape[k] = round(max(0.0, min(1.0, float(shape.get(k, 0.0)))), 3)

    return shape

