from __future__ import annotations

import re
from typing import Dict, List

# ----------------------------
# Core axis: zero <-> infinity
# ----------------------------
AXIS_PRIMITIVES = {
    "zero": {
        "axis": "zero",
        "atoms": ["void", "contain", "origin"],
        "definition": "Zero is the point where potential is fully contained: no outward magnitude, but complete capacity for structure to begin.",
    },
    "infinity": {
        "axis": "infinity",
        "atoms": ["open", "drift", "unbound"],
        "definition": "Infinity is unbounded extension, where expansion outruns closure and the field has no terminal edge.",
    },
    "symmetry": {
        "axis": "midfield",
        "atoms": ["match", "balance", "preserve"],
        "definition": "Symmetry is preserved relation across transformation, where structure remains intelligible as it changes position.",
    },
    "entropy": {
        "axis": "infinityward",
        "atoms": ["drift", "skew", "diverge"],
        "definition": "Entropy is the drift of structure away from stable alignment, where order becomes harder to preserve across the field.",
    },
}

# Concept seeds you already started discovering
CONCEPT_MAP: Dict[str, Dict[str, List[str] | str]] = {
    "secret": {
        "atoms": ["contain", "hide", "pressure"],
        "axis": "midfield",
    },
    "boredom": {
        "atoms": ["void", "wait", "low_input"],
        "axis": "zeroward",
    },
    "mercy": {
        "atoms": ["power", "restraint", "suspend"],
        "axis": "midfield",
    },
    "forgiveness": {
        "atoms": ["release", "memory", "decouple"],
        "axis": "midfield",
    },
    "curiosity": {
        "atoms": ["void", "reveal", "move"],
        "axis": "away_from_zero",
    },
    "betrayal": {
        "atoms": ["anchor", "reveal", "break"],
        "axis": "fracture",
    },
    "promise": {
        "atoms": ["anchor", "stretch", "future_lock"],
        "axis": "midfield",
    },
    "certainty": {
        "atoms": ["lock", "match", "skew"],
        "axis": "closure",
    },
    "evidence": {
        "atoms": ["reveal", "match", "verify"],
        "axis": "midfield",
    },
}

GENERIC_ATOMS = [
    "contain", "void", "wait",
    "anchor", "drift", "reveal",
    "match", "skew", "open",
]

GENERIC_SHELLS = (
    "clarity and depth hold each other together",
    "the answer becomes clearer when the cause is traced directly",
    "a better explanation comes from following the cause",
    "it makes more sense when the underlying cause is named clearly",
)

def _subject_from_prompt(text: str) -> str:
    t = (text or "").strip().lower()
    t = re.sub(r'^\s*(what is|what are|what does|what happens when|why does|how does)\s+', '', t)
    t = re.sub(r'[?!.]+$', '', t).strip()
    return t or "it"

def _contains_pair(text: str, a: str, b: str) -> bool:
    low = (text or "").lower()
    return a in low and b in low

def axis_profile(text: str) -> Dict[str, str | List[str]]:
    low = (text or "").lower()

    # explicit axis concepts
    for key, val in AXIS_PRIMITIVES.items():
        if key in low:
            return {
                "subject": key,
                "axis": str(val["axis"]),
                "atoms": list(val["atoms"]),
                "definition": str(val["definition"]),
            }

    # special relational prompts
    if _contains_pair(low, "certainty", "evidence"):
        return {
            "subject": "certainty outrunning evidence",
            "axis": "closure_over_verification",
            "atoms": ["lock", "skew", "verify"],
        }

    if _contains_pair(low, "silence", "trust"):
        return {
            "subject": "silence under low trust",
            "axis": "protective_withdrawal",
            "atoms": ["contain", "distance", "withhold"],
        }

    if "guilt" in low and any(k in low for k in ("event", "over", "after")):
        return {
            "subject": "guilt after the event",
            "axis": "residual_weight",
            "atoms": ["heavy", "repeat", "repair"],
        }

    # concept map
    for concept, payload in CONCEPT_MAP.items():
        if concept in low:
            return {
                "subject": concept,
                "axis": str(payload["axis"]),
                "atoms": list(payload["atoms"]),
            }

    # generic heuristic from primitive force cues
    atoms = []
    if any(k in low for k in ("hide", "secret", "conceal", "silent")):
        atoms.append("contain")
    if any(k in low for k in ("open", "infinite", "expand", "boundless")):
        atoms.append("open")
    if any(k in low for k in ("memory", "repeat", "again", "recursion")):
        atoms.append("repeat")
    if any(k in low for k in ("trust", "home", "stable", "hold")):
        atoms.append("anchor")
    if any(k in low for k in ("drift", "entropy", "chaos", "scatter")):
        atoms.append("drift")
    if any(k in low for k in ("truth", "evidence", "show", "reveal")):
        atoms.append("reveal")
    if any(k in low for k in ("pain", "sharp", "clear")):
        atoms.append("sharp")
    if any(k in low for k in ("blur", "confuse", "unclear")):
        atoms.append("blur")
    if any(k in low for k in ("wait", "delay", "boredom", "stalled")):
        atoms.append("wait")
    if any(k in low for k in ("act", "move", "strike", "do")):
        atoms.append("act")

    if len(atoms) < 3:
        atoms = (atoms + GENERIC_ATOMS)[:3]
    else:
        atoms = atoms[:3]

    return {
        "subject": _subject_from_prompt(text),
        "axis": "derived",
        "atoms": atoms,
    }

def build_definition(text: str) -> str:
    profile = axis_profile(text)
    if "definition" in profile:
        return str(profile["definition"])

    subject = str(profile.get("subject") or _subject_from_prompt(text)).strip()
    atoms = list(profile.get("atoms") or [])
    axis = str(profile.get("axis") or "derived")

    if _contains_pair(text, "certainty", "evidence"):
        return "When certainty outruns evidence, confidence stabilizes faster than verification, so error becomes easier to defend and harder to correct."

    if _contains_pair(text, "silence", "trust"):
        return "When trust is low, silence preserves protective distance, holding back exposure until vulnerability feels safer to release."

    low = (text or "").lower()
    if "guilt" in low and any(k in low for k in ("event", "over", "after")):
        return "After the event is over, guilt preserves the moral residue of the action, keeping responsibility, self-judgment, and repair pressure active."

    if len(atoms) < 3:
        return f"{subject.capitalize()} is shaped by structural pressure that has not been fully decomposed yet."

    a, b, c = atoms[:3]

    axis_line = {
        "zeroward": "It leans toward the zero side of the field, where movement drops and potential remains underfed.",
        "away_from_zero": "It moves away from zero, where lack becomes motive and attention begins to travel.",
        "infinityward": "It leans toward the infinity side of the field, where expansion outruns containment.",
        "closure": "It sits near closure, where certainty tries to stabilize before the field finishes checking itself.",
        "fracture": "It sits on a fracture line, where relation and break become inseparable.",
        "residual_weight": "It remains in the field as weight after the event has ended.",
        "protective_withdrawal": "It acts as a protective reduction of exposure inside a strained relation.",
        "closure_over_verification": "It describes closure arriving faster than verification.",
        "derived": "It takes shape through the relation of its active forces.",
        "midfield": "It sits in the middle field, where opposing pressures are still being negotiated.",
    }.get(axis, "It takes shape through the relation of its active forces.")

    return (
        f"{subject.capitalize()} is a tension between {a} and {b}, stabilized through {c}. "
        f"{axis_line}"
    )

def should_override(selected_text: str) -> bool:
    low = (selected_text or "").lower().strip()
    return (not low) or any(shell in low for shell in GENERIC_SHELLS)

