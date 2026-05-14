import re
import json
from pathlib import Path

STOP = {
    "what","is","are","the","a","an","of","to","and","or","in","on","for","with",
    "how","why","does","do","it","this","that","my","your","you","me","i","as",
    "can","could","would","should","be","been","being","am"
}

CORRECTIONS = {
    "grafity": "gravity",
    "conwpsciousness": "consciousness",
    "consciosness": "consciousness",
    "consiousness": "consciousness",
    "conciousness": "consciousness",
}

RELATIONS = {
    "grief": "bond-under-absence",
    "love": "bond",
    "joy": "release",
    "family": "belonging",
    "memory": "continuity",
    "time": "change",
    "recursion": "return",
    "gravity": "attraction",
    "well": "depth",
    "consciousness": "awareness",
    "coherence": "alignment",
    "ethics": "judgment",
    "good": "value",
    "goodness": "value",
    "evil": "distortion",
    "intelligence": "pattern-use",
    "build": "structure",
    "lattice": "structure",
    "glyph": "compressed-meaning",
    "kernel": "logic",
}

def _words(text):
    raw = re.findall(r"[A-Za-z']+", text.lower())
    fixed = [CORRECTIONS.get(w, w) for w in raw]
    return fixed

def atoms_from_prompt(text):
    return [w for w in _words(text) if w not in STOP][:16]

def infer_route(text, atoms):
    q = text.lower()

    if "same as" in q or "difference" in q or "relationship between" in q or "relation to" in q:
        return "relationship"

    if q.startswith("how"):
        return "mechanism"

    if "state" in atoms or "status" in atoms or "doing" in atoms:
        return "status"

    if "why" in q:
        return "cause"

    if len(atoms) >= 2:
        return "relationship"

    return "definition"

def relation_for(atom):
    return RELATIONS.get(atom, "meaning")

def build_birth_packet(prompt, pulse_context="", memory_match=None):
    atoms = atoms_from_prompt(prompt)
    subject = atoms[0] if atoms else "empty"

    route = infer_route(prompt, atoms)

    relation_map = []
    unique_relations = []
    for atom in atoms:
        rel = relation_for(atom)
        relation_map.append({"atom": atom, "relation": rel})
        if rel not in unique_relations:
            unique_relations.append(rel)

    memory_score = 0.0
    if isinstance(memory_match, dict):
        memory_score = float(memory_match.get("score") or 0.0)

    density_base = 0.25
    density_base += min(0.35, len(atoms) * 0.055)
    density_base += min(0.20, len(unique_relations) * 0.06)
    density_base += min(0.20, memory_score * 0.20)

    if "line stays itself" in pulse_context.lower():
        density_base += 0.08

    meaning_density = round(min(1.0, density_base), 3)
    high_speed = meaning_density >= 0.85

    object_atom = atoms[1] if len(atoms) > 1 else ""
    shape_answer = {
        "definition": f"{subject} = {relation_for(subject)}",
        "relationship": f"{subject} relates through {' + '.join(unique_relations)}",
        "mechanism": f"{subject} acts by moving through {' + '.join(unique_relations)}",
        "status": f"{subject} currently expresses {' + '.join(unique_relations)}",
        "cause": f"{subject} arises through {' + '.join(unique_relations)}",
    }.get(route, f"{subject} = {' + '.join(unique_relations)}")

    return {
        "prompt": prompt,
        "route": route,
        "subject": subject,
        "object": object_atom,
        "atoms": atoms,
        "relations": unique_relations,
        "relation_map": relation_map,
        "meaning_density": meaning_density,
        "high_speed_realization": high_speed,
        "shape_answer": shape_answer,
        "memory_score": memory_score,
        "pulse_continuity": "line stays itself" in pulse_context.lower(),
    }

