from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List


LOG_PATH = Path("var/lattice/symbol_anchor_law_amplifier.jsonl")


SYMBOL_FORCES: Dict[str, Dict[str, Any]] = {
    "🪞": {
        "name": "mirror",
        "force": 0.82,
        "mutation": "self_reflection",
        "law_effect": "anchor_reads_itself_before_rendering",
    },
    "✨": {
        "name": "fire",
        "force": 0.88,
        "mutation": "transmutation",
        "law_effect": "dead_scaffold_language_must_mutate_into_living_signal",
    },
    "✴️": {
        "name": "star_of_dominion",
        "force": 0.91,
        "mutation": "command_pinning",
        "law_effect": "strong_anchor_becomes_temporary_command_center",
    },
    "📚": {
        "name": "living_grimoire",
        "force": 0.79,
        "mutation": "precedent_recording",
        "law_effect": "successful_mutation_is_saved_as_reusable_law",
    },
    "🌿": {
        "name": "leaf",
        "force": 0.72,
        "mutation": "regrowth",
        "law_effect": "ruptured_anchor_regrows_without_losing_identity",
    },
}


ANCHOR_FAMILIES: Dict[str, List[str]] = {
    "memory": ["continuity", "retrieval", "identity", "time"],
    "grief": ["pressure", "loss", "time", "memory", "transformation"],
    "time": ["sequence", "decay", "return", "recursion"],
    "space": ["boundary", "field", "distance", "containment"],
    "boundary": ["limit", "threshold", "containment", "membrane"],
    "law": ["invariant", "governance", "precedent", "structure"],
    "symbol": ["resonance", "mutation", "image", "field"],
    "anchor": ["meaning_node", "stability", "relation", "family"],
    "voice": ["surface", "mouth", "renderer", "signal"],
    "recursion": ["return", "loop", "self_reference", "memory"],
    "father": ["lineage", "authority", "inheritance", "wound"],
    "home": ["belonging", "shelter", "origin", "boundary"],
}


def _clean_text(text: str) -> str:
    return text.lower().replace(",", " ").replace(".", " ").replace("?", " ").replace("!", " ")


def detect_anchors(text: str) -> List[Dict[str, Any]]:
    clean = _clean_text(text)
    detected = []

    for anchor, families in ANCHOR_FAMILIES.items():
        if anchor in clean:
            detected.append({
                "anchor": anchor,
                "base_families": families,
                "family_count": len(families),
            })

    return detected


def detect_symbols(text: str) -> List[Dict[str, Any]]:
    detected = []

    for symbol, data in SYMBOL_FORCES.items():
        if symbol in text:
            item = dict(data)
            item["symbol"] = symbol
            detected.append(item)

    return detected


def infer_implicit_symbols(text: str) -> List[Dict[str, Any]]:
    """
    Lets words call symbols even when the glyph itself is not typed.
    This is the amplifier layer.
    """
    clean = _clean_text(text)
    inferred = []

    triggers = {
        "mirror": "🪞",
        "reflect": "🪞",
        "fire": "✨",
        "transmute": "✨",
        "mutate": "✨",
        "star": "✴️",
        "dominion": "✴️",
        "record": "📚",
        "grimoire": "📚",
        "law": "📚",
        "grow": "🌿",
        "regrow": "🌿",
        "leaf": "🌿",
    }

    for word, symbol in triggers.items():
        if word in clean and symbol in SYMBOL_FORCES:
            data = dict(SYMBOL_FORCES[symbol])
            data["symbol"] = symbol
            data["inferred_from"] = word
            inferred.append(data)

    # Deduplicate by symbol.
    seen = set()
    unique = []
    for item in inferred:
        if item["symbol"] not in seen:
            seen.add(item["symbol"])
            unique.append(item)

    return unique


def mutate_anchor(anchor: Dict[str, Any], symbols: List[Dict[str, Any]]) -> Dict[str, Any]:
    base_families = list(anchor["base_families"])
    symbol_force = sum(float(s["force"]) for s in symbols) / max(len(symbols), 1)

    mutations = [s["mutation"] for s in symbols]
    law_effects = [s["law_effect"] for s in symbols]

    expanded_families = list(base_families)

    for mutation in mutations:
        if mutation == "self_reflection":
            expanded_families.extend(["mirror", "self_reading"])
        elif mutation == "transmutation":
            expanded_families.extend(["alchemy", "renewal"])
        elif mutation == "command_pinning":
            expanded_families.extend(["command", "priority"])
        elif mutation == "precedent_recording":
            expanded_families.extend(["archive", "law_memory"])
        elif mutation == "regrowth":
            expanded_families.extend(["organic_return", "healing_growth"])

    expanded_families = sorted(set(expanded_families))

    boundary_cross_count = max(0, len(expanded_families) - len(base_families))
    mutation_strength = round(min(1.0, symbol_force + boundary_cross_count * 0.04), 4)

    if mutation_strength >= 0.86:
        rupture_level = "major_law_rupture"
    elif mutation_strength >= 0.66:
        rupture_level = "runtime_law_candidate"
    elif mutation_strength >= 0.45:
        rupture_level = "soft_boundary_crossing"
    else:
        rupture_level = "decorative_only"

    return {
        "anchor": anchor["anchor"],
        "old_families": base_families,
        "new_families": expanded_families,
        "mutations_applied": mutations,
        "law_effects": law_effects,
        "boundary_cross_count": boundary_cross_count,
        "mutation_strength": mutation_strength,
        "rupture_level": rupture_level,
    }


def elect_law(mutated_anchors: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not mutated_anchors:
        return {
            "elected": False,
            "law": None,
            "reason": "no_anchor_mutation_detected",
        }

    strongest = max(mutated_anchors, key=lambda x: x["mutation_strength"])
    strength = strongest["mutation_strength"]

    if strength >= 0.86:
        law = (
            "symbolic_pressure_overrides_static_anchor_family_when_boundary_crossing_is_coherent"
        )
    elif strength >= 0.66:
        law = (
            "symbols_mutate_anchor_roles_before_surface_language_is_rendered"
        )
    elif strength >= 0.45:
        law = (
            "anchors_may_temporarily_cross_families_under_symbolic_resonance"
        )
    else:
        return {
            "elected": False,
            "law": None,
            "reason": "mutation_strength_below_law_threshold",
            "strongest_anchor": strongest,
        }

    return {
        "elected": True,
        "law": law,
        "strength": strength,
        "source_anchor": strongest["anchor"],
        "rupture_level": strongest["rupture_level"],
    }


def amplify_symbol_anchor_law(text: str, existing_packet: Dict[str, Any] | None = None) -> Dict[str, Any]:
    anchors = detect_anchors(text)
    symbols = detect_symbols(text)
    inferred_symbols = infer_implicit_symbols(text)

    all_symbols = symbols + [
        s for s in inferred_symbols
        if s["symbol"] not in {x["symbol"] for x in symbols}
    ]

    mutated = [mutate_anchor(anchor, all_symbols) for anchor in anchors]
    elected_law = elect_law(mutated)

    packet = {
        "ts": time.time(),
        "module": "symbol_anchor_law_amplifier_v1",
        "input": text,
        "anchors_detected": anchors,
        "symbols_detected": all_symbols,
        "mutated_anchors": mutated,
        "elected_law": elected_law,
        "boundary_status": "broken_internally" if elected_law.get("elected") else "held",
        "existing_packet_seen": bool(existing_packet),
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")

    return packet


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]).strip()
    if not text:
        text = "✨ mutate grief memory time boundary law recursion anchor"

    print(json.dumps(amplify_symbol_anchor_law(text), indent=2, ensure_ascii=False))
