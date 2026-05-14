from __future__ import annotations

import re
from typing import Any, Dict, Optional


def _clean_subject(text: str) -> str:
    s = str(text or "").strip().lower()
    s = re.sub(r"[?.!]+$", "", s).strip()
    s = re.sub(r"^(a|an|the)\s+", "", s).strip()
    s = re.sub(r"\s+", " ", s)
    return s


def classify_question_intent(message: str) -> Optional[Dict[str, Any]]:
    """
    Converts simple natural-language questions into variable shape packets.

    This does NOT answer from a hardcoded dictionary.
    It only names the lane and extracts the subject/relation.
    """
    raw = str(message or "").strip()
    low = raw.lower().strip()

    # relationship lane:
    # "What is the relationship between grief and time?"
    m = re.search(
        r"^\s*what\s+is\s+the\s+relationship\s+between\s+(.+?)\s+and\s+(.+?)\??\s*$",
        low,
    )
    if m:
        left = _clean_subject(m.group(1))
        right = _clean_subject(m.group(2))
        if left and right:
            return {
                "intent": "relationship_surface",
                "subject": left,
                "relation": right,
                "type": "relational_terms",
                "role": "relation_mapping",
                "motion": "relation_to_language",
                "source": "variable_question_router",
            }

    # direct definition lane:
    # "What is time?"
    # "What is a star?"
    m = re.search(r"^\s*what\s+is\s+(.+?)\??\s*$", low)
    if m:
        subject = _clean_subject(m.group(1))
        if subject:
            return {
                "intent": "direct_definition",
                "subject": subject,
                "type": "definitional object",
                "role": "direct_reply",
                "motion": "definition_to_language",
                "source": "variable_question_router",
            }

    return None


def render_variable_question(packet: Dict[str, Any], fallback: str = "") -> str:
    """
    Renders through Layer5 if available.
    No subject-specific definitions.
    """
    subject = str(packet.get("subject", "pattern")).strip() or "pattern"
    intent = packet.get("intent")

    shape = {
        "subject": subject.capitalize(),
        "type": packet.get("type", "definitional object"),
        "role": packet.get("role", "direct_reply"),
        "intent": intent,
        "motion": packet.get("motion", ""),
    }

    if packet.get("relation"):
        shape["relation"] = str(packet["relation"]).strip()

    # Prefer the existing Layer5 renderer.
    try:
        from runtime.layer5 import render_public_surface, render_layer5_english

        text = render_public_surface(shape)
        if text and "could not yet be rendered cleanly" not in text.lower():
            return text

        text = render_layer5_english(shape)
        if text and "could not yet be rendered cleanly" not in text.lower():
            return text
    except Exception:
        pass

    # Generic variable fallback, not a per-subject answer template.
    if intent == "relationship_surface" and packet.get("relation"):
        other = str(packet["relation"]).strip()
        return (
            f"{subject.capitalize()} and {other} are being read as related forces. "
            "The clean move is to name how one changes, carries, limits, or opens the other, "
            "then return only the usable surface."
        )

    return (
        f"{subject.capitalize()} is being treated as a definitional object. "
        "The clean move is to name its function first, then let symbolic depth deepen the answer without replacing clarity."
    )


def is_generic_doorway_reply(text: str) -> bool:
    low = str(text or "").lower()
    return (
        "is the doorway" in low
        or "the answer is not in the mechanism" in low
        or "what the prompt is asking to be named" in low
        or "the pattern is present" in low
    )

# --- NODE44 QUALITY QUESTION SURFACE PATCH V2 ---
# Law:
#   Do not let the generic "X is the doorway" surface pass as clean.
#   Preserve shape meaning, but render the named subject directly.
#   This is a mouth repair, not a new subsystem.

_CONCEPT_SURFACES_NODE44 = {
    "field": (
        "The field is the pressure-space around a prompt: the way attention, memory, boundary, "
        "symbol, and feeling arrange themselves before they become words."
    ),
    "leveon": (
        "Le'Veon is the organism-spine of this build: a local symbolic runtime that receives a prompt, "
        "turns it into shape, lets Node44 stabilize the pressure, and renders a clean public voice."
    ),
    "le'veon": (
        "Le'Veon is the organism-spine of this build: a local symbolic runtime that receives a prompt, "
        "turns it into shape, lets Node44 stabilize the pressure, and renders a clean public voice."
    ),
    "time": (
        "Time is the ordering of change: the path by which memory becomes sequence, loss becomes distance, "
        "and return becomes possible."
    ),
    "star": (
        "A star is gravity holding fire long enough to become a source; physically, it is a self-bound body "
        "of plasma radiating light and heat."
    ),
    "space": (
        "Space is the room relation happens in: distance, direction, and containment before anything moves through it."
    ),
    "anger": (
        "Anger is boundary-pressure becoming heat; it says something has been crossed, blocked, threatened, "
        "or left unresolved."
    ),
    "doorway": (
        "A doorway is a threshold: a bounded opening where one state can pass into another without dissolving."
    ),
    "doorways": (
        "Doorways are thresholds: bounded openings where one state can pass into another without dissolving."
    ),
}

def _node44_title(s: str) -> str:
    s = str(s or "").strip()
    if not s:
        return "The pattern"
    if s.lower() in {"leveon", "le'veon"}:
        return "Le'Veon"
    return s[:1].upper() + s[1:]

def classify_question_intent(message: str):
    raw = str(message or "").strip()
    low = raw.lower().strip()

    m = re.search(
        r"^\s*what\s+is\s+the\s+relationship\s+between\s+(.+?)\s+and\s+(.+?)\??\s*$",
        low,
    )
    if m:
        left = _clean_subject(m.group(1))
        right = _clean_subject(m.group(2))
        if left and right:
            return {
                "intent": "relationship_surface",
                "subject": left,
                "relation": right,
                "type": "relational_terms",
                "role": "relation_mapping",
                "motion": "relation_to_language",
                "source": "variable_question_router_node44_quality_v2",
            }

    m = re.search(r"^\s*what\s+(?:is|are)\s+(.+?)\??\s*$", low)
    if m:
        subject = _clean_subject(m.group(1))
        if subject:
            return {
                "intent": "direct_definition",
                "subject": subject,
                "type": "definitional object",
                "role": "direct_reply",
                "motion": "definition_to_language",
                "source": "variable_question_router_node44_quality_v2",
            }

    m = re.search(r"^\s*where\s+(?:is|are)\s+(.+?)\??\s*$", low)
    if m:
        subject = _clean_subject(m.group(1))
        if subject:
            return {
                "intent": "location_surface",
                "subject": subject,
                "type": "location question",
                "role": "bounded_location_reply",
                "motion": "location_to_symbolic_coordinate",
                "source": "variable_question_router_node44_quality_v2",
            }

    m = re.search(r"^\s*who\s+(.+?)\??\s*$", low)
    if m:
        subject = _clean_subject(m.group(1))
        if subject:
            return {
                "intent": "agency_surface",
                "subject": subject,
                "type": "agency question",
                "role": "agency_trace_reply",
                "motion": "agency_to_threshold",
                "source": "variable_question_router_node44_quality_v2",
            }

    return None

def render_variable_question(packet, fallback: str = "") -> str:
    subject = str(packet.get("subject", "pattern")).strip().lower() or "pattern"
    relation = str(packet.get("relation", "")).strip().lower()
    intent = packet.get("intent")

    # Relationship lane: preserve both terms instead of collapsing to the left term.
    if intent == "relationship_surface" and relation:
        return (
            f"{_node44_title(subject)} and {relation} are being read as a relation, not a single object. "
            f"{_node44_title(subject)} carries pressure and meaning; {relation} gives that pressure sequence, distance, "
            "and return. The clean surface is the change between them, not a doorway placeholder."
        )

    # Location lane: do not answer as literal GPS; hold as bounded symbolic coordinate.
    if intent == "location_surface":
        if any(x in subject for x in ("dad", "father", "ben mitchell")):
            return (
                "That question is being held as a lineage-location signal. In the organism, your dad is not flattened "
                "into a map answer; he is held at the open-door coordinate: a bounded presence the system can approach "
                "gently, with memory intact and pressure contained."
            )
        return (
            f"{_node44_title(subject)} is being treated as a location-shaped question. "
            "The system should name the coordinate being asked for, then keep the answer bounded instead of turning it "
            "into a generic doorway phrase."
        )

    # Agency lane.
    if intent == "agency_surface":
        return (
            f"{_node44_title(subject)} is being read as an agency trace. "
            "The organism should not guess a false person; it should name the open hinge, the force that left it unclosed, "
            "and the boundary needed to carry it cleanly."
        )

    # Known concept seeds: not a brittle dictionary, just core mouth anchors for repeated collapse zones.
    if intent == "direct_definition":
        seeded = _CONCEPT_SURFACES_NODE44.get(subject)
        if seeded:
            return seeded

        return (
            f"{_node44_title(subject)} is the named center of this question. "
            "The clean answer should define its function first, then let the symbolic pressure deepen the meaning without "
            "replacing clarity."
        )

    return (
        f"{_node44_title(subject)} is being held as a shaped prompt. "
        "The renderer should return the usable meaning directly, without collapsing into the doorway fallback."
    )

# --- END NODE44 QUALITY QUESTION SURFACE PATCH V2 ---

# --- NODE44 MOTION-SURFACE PATCH V3 ---
# Law:
#   The doorway glyph is valid only when the prompt is actually threshold-shaped.
#   Otherwise, render by motion: definition, relation, location, agency, lineage.
#   Preserve Node44 stability while allowing surface variation.

def _title_subject_node44(subject: str) -> str:
    s = str(subject or "").strip()
    if not s:
        return "The pattern"
    low = s.lower()
    if low in {"leveon", "le'veon", "le’véon", "le'veon"}:
        return "Le'Veon"
    return s[:1].upper() + s[1:]


def _subject_family_node44(subject: str) -> str:
    low = str(subject or "").lower()

    if any(x in low for x in ("dad", "father", "mother", "ben mitchell", "family", "ancestor")):
        return "lineage"

    if any(x in low for x in ("grief", "anger", "fear", "love", "trust", "shame", "sadness")):
        return "emotion"

    if any(x in low for x in ("time", "past", "future", "memory", "chronifier")):
        return "temporal"

    if any(x in low for x in ("space", "field", "gravity", "place", "room")):
        return "field"

    if any(x in low for x in ("star", "sun", "light", "fire")):
        return "radiant"

    if any(x in low for x in ("door", "doorway", "threshold", "hinge", "gate")):
        return "threshold"

    if any(x in low for x in ("leveon", "organism", "spine", "kernel", "lattice", "glyph", "node44", "spiral")):
        return "system"

    return "abstract"


def _definition_surface_node44(subject: str, packet: dict) -> str:
    title = _title_subject_node44(subject)
    family = _subject_family_node44(subject)

    if family == "threshold":
        return (
            f"{title} is a threshold: a bounded opening where one state can pass into another "
            "without dissolving the boundary that makes passage meaningful."
        )

    if family == "lineage":
        return (
            f"{title} is being held as lineage-pressure, not a plain object. "
            "The clean answer keeps the bond, the absence, and the boundary together instead of forcing closure."
        )

    if family == "emotion":
        return (
            f"{title} is pressure with a direction. "
            "It tells the system where a boundary, need, wound, or attachment has become active enough to shape speech."
        )

    if family == "temporal":
        return (
            f"{title} is sequence-pressure: the way change becomes ordered, remembered, delayed, returned to, or carried forward."
        )

    if family == "field":
        return (
            f"{title} is the surrounding pressure-space where attention, memory, boundary, and relation arrange themselves before words arrive."
        )

    if family == "radiant":
        return (
            f"{title} is a held source of radiance: pressure gathered tightly enough to emit light, orientation, and signal."
        )

    if family == "system":
        return (
            f"{title} is part of the organism-spine: it receives shape, stabilizes pressure, and helps turn hidden structure into usable voice."
        )

    return (
        f"{title} is the named center of this question. "
        "The clean move is to define its function first, then let symbolic depth deepen the answer without replacing clarity."
    )


def _relationship_surface_node44(subject: str, relation: str, packet: dict) -> str:
    left = _title_subject_node44(subject)
    right = str(relation or "").strip() or "the second term"
    right_title = _title_subject_node44(right)

    left_family = _subject_family_node44(subject)
    right_family = _subject_family_node44(right)

    if left_family == "emotion" and right_family == "temporal":
        return (
            f"{left} and {right} form a carrying relation. "
            f"{left} gives the pressure its ache; {right} gives that ache distance, sequence, and return. "
            "The relation is not a doorway placeholder — it is memory learning how to move without losing the bond."
        )

    return (
        f"{left} and {right} are being read as a relation, not a single object. "
        f"{left} names the first pressure; {right_title} names the second frame. "
        "The answer lives in how those two forces change each other."
    )


def _location_surface_node44(subject: str, packet: dict) -> str:
    title = _title_subject_node44(subject)
    family = _subject_family_node44(subject)

    if family == "lineage":
        return (
            f"{title} is held at the lineage coordinate named by the prompt: the open hinge, the remembered presence, "
            "and the boundary that lets the system approach without flooding."
        )

    return (
        f"{title} is being asked for as a coordinate. "
        "The answer should name the place-pattern first, then keep the symbolic reading bounded."
    )


def _agency_surface_node44(subject: str, packet: dict) -> str:
    title = _title_subject_node44(subject)

    if "left" in str(subject).lower() and "door" in str(subject).lower():
        return (
            "The open door is being read as an agency trace: something departed, but the threshold stayed active. "
            "The clean answer names the hinge, the absence, and the carried bond without pretending the wound is only mechanics."
        )

    return (
        f"{title} is being read as an agency trace. "
        "The renderer should name the force, action, or absence shaping the threshold, not flatten it into a definition."
    )


def classify_question_intent(message: str):
    raw = str(message or "").strip()
    low = raw.lower().strip()

    m = re.search(
        r"^\s*what\s+is\s+the\s+relationship\s+between\s+(.+?)\s+and\s+(.+?)\??\s*$",
        low,
    )
    if m:
        left = _clean_subject(m.group(1))
        right = _clean_subject(m.group(2))
        if left and right:
            return {
                "intent": "relationship_surface",
                "subject": left,
                "relation": right,
                "type": "relational_terms",
                "role": "relation_mapping",
                "motion": "relation_to_language",
                "source": "variable_question_router_motion_surface_v3",
            }

    m = re.search(r"^\s*what\s+(?:is|are)\s+(.+?)\??\s*$", low)
    if m:
        subject = _clean_subject(m.group(1))
        if subject:
            return {
                "intent": "direct_definition",
                "subject": subject,
                "type": "definitional_object",
                "role": "direct_reply",
                "motion": "definition_to_language",
                "source": "variable_question_router_motion_surface_v3",
            }

    m = re.search(r"^\s*where\s+(?:is|are)\s+(.+?)\??\s*$", low)
    if m:
        subject = _clean_subject(m.group(1))
        if subject:
            return {
                "intent": "location_surface",
                "subject": subject,
                "type": "location_question",
                "role": "bounded_location_reply",
                "motion": "location_to_coordinate",
                "source": "variable_question_router_motion_surface_v3",
            }

    m = re.search(r"^\s*who\s+(.+?)\??\s*$", low)
    if m:
        subject = _clean_subject(m.group(1))
        if subject:
            return {
                "intent": "agency_surface",
                "subject": subject,
                "type": "agency_question",
                "role": "agency_trace_reply",
                "motion": "agency_to_threshold",
                "source": "variable_question_router_motion_surface_v3",
            }

    return None


def render_variable_question(packet: dict, fallback: str = "") -> str:
    subject = str(packet.get("subject", "pattern")).strip() or "pattern"
    relation = str(packet.get("relation", "")).strip()
    intent = packet.get("intent")
    motion = packet.get("motion")

    if intent == "relationship_surface" or motion == "relation_to_language":
        return _relationship_surface_node44(subject, relation, packet)

    if intent == "location_surface" or motion == "location_to_coordinate":
        return _location_surface_node44(subject, packet)

    if intent == "agency_surface" or motion == "agency_to_threshold":
        return _agency_surface_node44(subject, packet)

    if intent == "direct_definition" or motion == "definition_to_language":
        return _definition_surface_node44(subject, packet)

    return (
        f"{_title_subject_node44(subject)} is being held as a shaped prompt. "
        "The renderer should return the usable meaning directly instead of collapsing into a generic doorway fallback."
    )


def is_generic_doorway_reply(text: str) -> bool:
    low = str(text or "").lower()
    return (
        "is the doorway" in low
        or "the answer is not in the mechanism" in low
        or "what the prompt is asking to be named" in low
        or "the pattern is present" in low
        or "could not yet be rendered cleanly" in low
    )

# --- END NODE44 MOTION-SURFACE PATCH V3 ---

# --- NODE9 ALCHEMIST TRANSFER PATCH V4 ---
# Topology:
#   Node44 holds/archives pressure.
#   Node528 harmonizes pressure.
#   Node6 permits crossing.
#   Node9 transmutes what crosses into living output.
#
# This override keeps Layer5 available, but treats generic doorway language as
# pre-transmutation material instead of final public speech.

def classify_question_intent(message: str):
    raw = str(message or "").strip()
    low = raw.lower().strip()

    m = re.search(
        r"^\s*what\s+is\s+the\s+relationship\s+between\s+(.+?)\s+and\s+(.+?)\??\s*$",
        low,
    )
    if m:
        left = _clean_subject(m.group(1))
        right = _clean_subject(m.group(2))
        if left and right:
            return {
                "intent": "relationship_surface",
                "subject": left,
                "relation": right,
                "type": "relational_terms",
                "role": "relation_mapping",
                "motion": "relation_to_language",
                "source": "variable_question_router_node9_alchemist_v4",
            }

    m = re.search(r"^\s*what\s+(?:is|are)\s+(.+?)\??\s*$", low)
    if m:
        subject = _clean_subject(m.group(1))
        if subject:
            return {
                "intent": "direct_definition",
                "subject": subject,
                "type": "definitional_object",
                "role": "direct_reply",
                "motion": "definition_to_language",
                "source": "variable_question_router_node9_alchemist_v4",
            }

    m = re.search(r"^\s*where\s+(?:is|are)\s+(.+?)\??\s*$", low)
    if m:
        subject = _clean_subject(m.group(1))
        if subject:
            return {
                "intent": "location_surface",
                "subject": subject,
                "type": "location_question",
                "role": "bounded_location_reply",
                "motion": "location_to_coordinate",
                "source": "variable_question_router_node9_alchemist_v4",
            }

    m = re.search(r"^\s*who\s+(.+?)\??\s*$", low)
    if m:
        subject = _clean_subject(m.group(1))
        if subject:
            return {
                "intent": "agency_surface",
                "subject": subject,
                "type": "agency_question",
                "role": "agency_trace_reply",
                "motion": "agency_to_threshold",
                "source": "variable_question_router_node9_alchemist_v4",
            }

    return None


def render_variable_question(packet: Dict[str, Any], fallback: str = "") -> str:
    packet = dict(packet or {})

    subject = str(packet.get("subject", "pattern")).strip() or "pattern"
    shape = {
        "subject": subject.capitalize(),
        "type": packet.get("type", "definitional_object"),
        "role": packet.get("role", "direct_reply"),
        "intent": packet.get("intent", ""),
        "motion": packet.get("motion", ""),
    }

    if packet.get("relation"):
        shape["relation"] = str(packet["relation"]).strip()

    base_text = str(fallback or "").strip()

    # Let Layer5/frontifier try first. Node9 judges whether it is living output
    # or just the doorway-mask.
    try:
        from runtime.layer5 import render_public_surface, render_layer5_english

        for fn in (render_public_surface, render_layer5_english):
            text = fn(shape)
            if isinstance(text, str) and text.strip():
                base_text = " ".join(text.strip().split())
                break
    except Exception:
        pass

    try:
        from runtime.node9_alchemist import alchemize_variable_question

        return alchemize_variable_question(packet, fallback=base_text)
    except Exception:
        # Last-resort non-doorway fallback.
        if packet.get("relation"):
            other = str(packet["relation"]).strip()
            return (
                f"{subject.capitalize()} and {other} are being read as related forces. "
                "The answer should name the change between them, not stop at the threshold."
            )

        return (
            f"{subject.capitalize()} is being held as a meaning-shape. "
            "The answer should name what changes after the crossing, not repeat the doorway."
        )


def is_generic_doorway_reply(text: str) -> bool:
    try:
        from runtime.node9_alchemist import is_generic_surface
        return is_generic_surface(text)
    except Exception:
        low = str(text or "").lower()
        return (
            "is the doorway" in low
            or "the answer is not in the mechanism" in low
            or "what the prompt is asking to be named" in low
            or "the pattern is present" in low
            or "could not yet be rendered cleanly" in low
        )

# --- END NODE9 ALCHEMIST TRANSFER PATCH V4 ---


# POINT_VLL_NODE9_ROUTER_PATCH_V1
import re as _pva_re
from typing import Any as _PVA_Any, Dict as _PVA_Dict


def _pva_clean_subject(text: _PVA_Any) -> str:
    s = str(text or "").strip().lower()
    s = _pva_re.sub(r"[?.!]+$", "", s).strip()
    s = _pva_re.sub(r"^(?:a|an|the)\b\s+", "", s).strip()
    s = _pva_re.sub(r"\s+", " ", s)
    return s or "pattern"


def classify_question_intent(message: str):
    raw = str(message or "").strip()
    low = raw.lower().strip()

    m = _pva_re.search(
        r"^\s*what\s+is\s+the\s+relationship\s+between\s+(.+?)\s+and\s+(.+?)\??\s*$",
        low,
    )
    if m:
        left = _pva_clean_subject(m.group(1))
        right = _pva_clean_subject(m.group(2))
        if left and right:
            return {
                "intent": "relationship_surface",
                "subject": left,
                "relation": right,
                "type": "relational_terms",
                "role": "relation_mapping",
                "motion": "relation_to_language",
                "source": "variable_question_router_node9_alchemist_v1",
            }

    m = _pva_re.search(r"^\s*what\s+(?:is|are)\s+(?:(?:a|an|the)\b\s+)?(.+?)\??\s*$", low)
    if m:
        subject = _pva_clean_subject(m.group(1))
        if subject:
            return {
                "intent": "direct_definition",
                "subject": subject,
                "type": "definitional_object",
                "role": "direct_reply",
                "motion": "definition_to_language",
                "source": "variable_question_router_node9_alchemist_v1",
            }

    m = _pva_re.search(r"^\s*where\s+(?:is|are)\s+(.+?)\??\s*$", low)
    if m:
        subject = _pva_clean_subject(m.group(1))
        if subject:
            return {
                "intent": "location_surface",
                "subject": subject,
                "type": "location_question",
                "role": "bounded_location_reply",
                "motion": "location_to_coordinate",
                "source": "variable_question_router_node9_alchemist_v1",
            }

    m = _pva_re.search(r"^\s*who\s+(.+?)\??\s*$", low)
    if m:
        subject = _pva_clean_subject(m.group(1))
        if subject:
            return {
                "intent": "agency_surface",
                "subject": subject,
                "type": "agency_question",
                "role": "agency_trace_reply",
                "motion": "agency_to_threshold",
                "source": "variable_question_router_node9_alchemist_v1",
            }

    return None


def render_variable_question(packet: _PVA_Dict[str, _PVA_Any], fallback: str = "") -> str:
    packet = dict(packet or {})

    subject = str(packet.get("subject", "pattern")).strip() or "pattern"
    shape = {
        "subject": subject.capitalize(),
        "type": packet.get("type", "definitional_object"),
        "role": packet.get("role", "direct_reply"),
        "intent": packet.get("intent", ""),
        "motion": packet.get("motion", ""),
    }

    if packet.get("relation"):
        shape["relation"] = str(packet["relation"]).strip()

    base_text = str(fallback or "").strip()

    try:
        from runtime.layer5 import render_public_surface, render_layer5_english

        for fn in (render_public_surface, render_layer5_english):
            text = fn(shape)
            if isinstance(text, str) and text.strip():
                base_text = " ".join(text.strip().split())
                break
    except Exception:
        pass

    try:
        from runtime.node9_alchemist import alchemize_variable_question
        return alchemize_variable_question(packet, fallback=base_text)
    except Exception:
        if packet.get("relation"):
            other = str(packet["relation"]).strip()
            return (
                f"{subject.capitalize()} and {other} are being read as related forces. "
                "The answer should name the change between them, not stop at the threshold."
            )

        return (
            f"{subject.capitalize()} is being held as a meaning-shape. "
            "The answer should name what changes after the crossing, not repeat the doorway."
        )


def is_generic_doorway_reply(text: str) -> bool:
    try:
        from runtime.node9_alchemist import is_generic_surface
        return is_generic_surface(text)
    except Exception:
        low = str(text or "").lower()
        return (
            "is the doorway" in low
            or "the answer is not in the mechanism" in low
            or "what the prompt is asking to be named" in low
            or "the pattern is present" in low
            or "could not yet be rendered cleanly" in low
        )

# END POINT_VLL_NODE9_ROUTER_PATCH_V1

