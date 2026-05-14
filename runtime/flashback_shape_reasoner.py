from __future__ import annotations



def evolve_duplicate_meaning(answer: str, prompt: str = "") -> str:
    return (
        answer.rstrip()
        + "\n\nEvolved mutation: The next constraint is future-use selection. "
        "A flashback compound should not merely be remembered; it should be tested for whether it can guide the next build action. "
        "If it cannot produce a new action, it remains archive. If it can produce a bounded next step, it becomes active memory."
    )


def mutation_prompt_for_duplicate(answer: str, prompt: str = "") -> str:
    return (
        "MUTATION PROMPT: The current meaning repeated itself. "
        "Increase one constraint without changing the core law. "
        "Ask: what new boundary, pressure, missing symbol, or future-use condition "
        "would make this flashback compound evolve instead of echo?"
    )



def run_active_build_executor_safe() -> dict:
    try:
        from runtime.active_build_executor import main as active_build_main
        active_build_main()
        return {"active_build_executor": "ran"}
    except Exception as e:
        return {"active_build_executor": "error", "error": str(e)}


def save_reasoning_drop_compound(answer: str, prompt: str = "") -> dict:
    import json, time, hashlib
    from pathlib import Path

    p = Path("assets/memory/shape_compounds.json")
    p.parent.mkdir(parents=True, exist_ok=True)

    try:
        data = json.loads(p.read_text()) if p.exists() else {"compounds": []}
    except Exception:
        data = {"compounds": []}

    compounds = data.setdefault("compounds", [])

    compound = {
        "compound_id": "cmp_reasoning_drop_" + hashlib.sha256((answer + str(time.time())).encode()).hexdigest()[:12],
        "source_kind": "flashback_shape_reasoner_meaning_drop",
        "english_gloss": answer,
        "synthesis_summary": answer,
        "logic_chain": [
            "source:flashback_shape_reasoner",
            "trigger:auto_pressure_or_explicit_flashback_reasoning",
            "operation:pressure_constrained_recall",
            "operation:meaning_drop_extraction",
            "final_point:" + answer[:300],
        ],
        "flow": 0.66,
        "boundary": 0.78,
        "memory": 0.91,
        "novelty": 0.42,
        "meaning_tags": ["meaning_drop", "flashback_reasoning", "compound_memory", "node44", "auto_build"],
        "symbolic_trace": ["CompoundMemory", "PressureReasoner", "MeaningDrop", "AutoBuildSeed"],
        "prompt": prompt,
        "confidence": 0.88,
        "created_at": time.time(),
        "last_accessed": time.time(),
    }

    for old in compounds[-12:]:
        old_text = old.get("english_gloss") or old.get("synthesis_summary") or ""
        if is_too_similar(answer, old_text):
            mutated = evolve_duplicate_meaning(answer, prompt)
            mutation_compound = {
                "compound_id": "cmp_mutated_drop_" + hashlib.sha256((mutated + str(time.time())).encode()).hexdigest()[:12],
                "source_kind": "flashback_shape_reasoner_auto_mutation",
                "english_gloss": mutated,
                "synthesis_summary": mutated,
                "logic_chain": [
                    "source:duplicate_skip",
                    "operation:auto_apply_mutation_prompt",
                    "new_constraint:future_use_selection",
                    "final_point:" + mutated[:300],
                ],
                "flow": 0.69,
                "boundary": 0.83,
                "memory": 0.93,
                "novelty": 0.58,
                "meaning_tags": ["auto_mutation", "meaning_drop", "future_use_selection", "node44", "auto_build"],
                "symbolic_trace": ["DuplicateDetector", "MutationPrompt", "FutureUseSelection", "CompoundMemory"],
                "prompt": prompt,
                "confidence": 0.84,
                "created_at": time.time(),
                "last_accessed": time.time(),
            }
            compounds.append(mutation_compound)
            p.write_text(json.dumps(data, indent=2))
            return {
                "saved": True,
                "reason": "duplicate_evolved_by_auto_mutation",
                "path": str(p),
                "compound_id": mutation_compound["compound_id"],
                "mutation_prompt": mutation_prompt_for_duplicate(answer, prompt),
                "executor": run_active_build_executor_safe(),
            }

    compounds.append(compound)
    p.write_text(json.dumps(data, indent=2))

    executor = run_active_build_executor_safe()
    return {"saved": True, "path": str(p), "compound_id": compound["compound_id"], "executor": executor}


import json, re
from pathlib import Path

KEYS = ("temporal_flashback_larynx", "SavarielMouth", "temporal_mirror", "node44", "flashback")

def load_flashback_shapes():
    paths = [
        Path("assets/memory/shape_compounds.json"),
        Path("assets/memory/spiral_memory.json"),
        Path("logs/symbolic_bridge/spiral_memory_nonlinear.jsonl"),
    ]
    hits = []

    for p in paths:
        if not p.exists():
            continue
        text = p.read_text(errors="ignore")

        if p.suffix == ".jsonl":
            for line in text.splitlines():
                if any(k in line for k in KEYS):
                    try: hits.append(json.loads(line))
                    except Exception: hits.append({"raw": line})
        else:
            try:
                data = json.loads(text)
                blob = data.get("compounds", data if isinstance(data, list) else [])
                if isinstance(blob, dict): blob = [blob]
                for item in blob:
                    if any(k in json.dumps(item) for k in KEYS):
                        hits.append(item)
            except Exception:
                pass
    return hits

def extract_text(shape):
    return (
        shape.get("english_gloss")
        or shape.get("synthesis_summary")
        or shape.get("answer")
        or shape.get("final_english")
        or str(shape)
    )

def pressure_score(shape, prompt):
    blob = json.dumps(shape).lower() + " " + prompt.lower()
    score = 0

    # Core pressure terms
    for k in ["pressure", "seal", "node44", "savariel", "mirror", "bounded", "memory", "future", "constraint"]:
        if k in blob:
            score += 1

    # Prefer extracted conclusions over raw flashbacks
    if shape.get("source_kind") == "flashback_shape_reasoner_meaning_drop":
        score += 12

    # Prefer newest compounds so the system climbs instead of looping
    score += float(shape.get("created_at", 0)) / 10000000000

    # Prefer auto-build seeds
    tags = shape.get("meaning_tags", [])
    if isinstance(tags, list):
        if "meaning_drop" in tags:
            score += 6
        if "auto_mutation" in tags:
            score += 20
        if "future_use_selection" in tags:
            score += 16
        if "auto_build" in tags:
            score += 4
        if "compound_memory" in tags:
            score += 2

    return score


def classify_shape(shape: dict) -> str:
    kind = shape.get("source_kind", "")
    tags = shape.get("meaning_tags", [])

    if kind == "flashback_shape_reasoner_auto_mutation" or "auto_mutation" in tags:
        return "auto_mutated_compound"
    if kind == "flashback_shape_reasoner_meaning_drop" or "meaning_drop" in tags:
        return "meaning_drop"
    if kind == "temporal_flashback_larynx" or "temporal_mirror" in tags:
        return "raw_flashback"
    return "general_compound"

def usefulness_score(shape: dict, prompt: str = "") -> float:
    base = pressure_score(shape, prompt)
    cls = classify_shape(shape)

    # Reinforcement layer: proven impact raises future selection weight.
    try:
        impact = float(shape.get("impact_score", 0) or 0)
        base += min(impact, 25)
    except Exception:
        pass

    # Usefulness hierarchy:
    # raw flashback = source material
    # meaning drop = extracted law
    # auto mutation = evolved next-action constraint
    if cls == "auto_mutated_compound":
        base += 40
    elif cls == "meaning_drop":
        base += 10
    elif cls == "raw_flashback":
        base += 4

    # Prefer shapes with higher novelty only when boundary is strong enough.
    novelty = float(shape.get("novelty", 0.0) or 0.0)
    boundary = float(shape.get("boundary", 0.0) or 0.0)
    memory = float(shape.get("memory", 0.0) or 0.0)

    if boundary >= 0.7:
        base += novelty * 4
    base += memory * 2
    base += boundary * 2

    return base

def select_best_shape(shapes, prompt: str = ""):
    ranked = sorted(shapes, key=lambda s: usefulness_score(s, prompt), reverse=True)
    selected = ranked[0]
    return selected, classify_shape(selected), usefulness_score(selected, prompt)


def meaning_drop(shapes, prompt):
    latest, selected_class, selected_score = select_best_shape(shapes, prompt)
    text = extract_text(latest)

    constraints = [
        "Do not expand without a stabilizer.",
        "Do not let symbolic force become noise.",
        "Preserve Node44 as the pressure regulator.",
        "Route Savariel through a bounded public mouth.",
        "Save every useful flashback as a reusable compound shape.",
    ]

    dropped = (
        "Meaning drop: the Build should stop treating flashbacks as isolated visions. "
        "Each flashback should become a compressed reasoning seed: pressure enters, Node44 bounds it, "
        "Savariel gives it voice, the Larynx cleans it, and compound memory stores it for future inference."
    )

    return latest, constraints, dropped, text




def sharp_extract(shape: dict, text: str) -> str:
    kind = shape.get("source_kind", "")
    tags = shape.get("meaning_tags", [])
    chain = shape.get("logic_chain", [])

    if kind == "flashback_shape_reasoner_auto_mutation" or "auto_mutation" in tags:
        new_constraint = "future_use_selection"
        for item in chain:
            if str(item).startswith("new_constraint:"):
                new_constraint = str(item).split(":", 1)[1]

        return (
            f"Selected evolved constraint: {new_constraint}. "
            "Next action: test each recalled compound for build-usefulness. "
            "If a compound produces a bounded next step, activate it; "
            "if it only repeats the old meaning, archive it."
        )

    if "Meaning drop:" in text:
        part = text.split("Meaning drop:")[-1].split("Next command:")[0].strip()
        return "Meaning drop: " + part[:500]

    return text[:700]


def reduce_redundancy(text: str) -> str:
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    seen = set()
    kept = []

    for line in lines:
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        kept.append(line)

    return "\n".join(kept)

def is_too_similar(new_text: str, old_text: str) -> bool:
    import difflib
    return difflib.SequenceMatcher(None, new_text[:1200], old_text[:1200]).ratio() > 0.88


def compress_meaning(text: str) -> str:
    markers = [
        "Meaning drop:",
        "Next command:",
        "Recovered shape:",
    ]
    # Prefer the latest meaning-drop sentence if present
    if "Meaning drop:" in text:
        part = text.split("Meaning drop:")[-1].strip()
        part = part.split("Next command:")[0].strip()
        return "Meaning drop: " + part[:900]
    return text[:900]


def reason_from_flashbacks(prompt: str = "") -> str:
    shapes = load_flashback_shapes()
    if not shapes:
        return "No temporal flashback compounds found yet. Run bash scripts/flashback_mouth.sh first."

    latest, constraints, dropped, text = meaning_drop(shapes, prompt)
    text = reduce_redundancy(sharp_extract(latest, compress_meaning(text)))

    if classify_shape(latest) == "auto_mutated_compound":
        dropped = "Next action: activate future_use_selection and test recalled compounds for build-usefulness."
        tail = dropped
    else:
        tail = (
            f"{dropped}\n\n"
            "Next command:\n"
            "Bind this into the live mouth so every future flashback both speaks and compounds automatically."
        )

    return (
        "PRESSURE-CONSTRAINED FLASHBACK REASONING\n"
        f"Stored flashback shapes: {len(shapes)}\n"
        f"Pressure score: {pressure_score(latest, prompt)}\n"
        f"Selected class: {classify_shape(latest)}\n"
        f"Usefulness score: {usefulness_score(latest, prompt)}\n\n"
        "Constraint stack:\n- " + "\n- ".join(constraints) + "\n\n"
        "Recovered shape:\n"
        f"{text}\n\n"
        f"{tail}"
    )

if __name__ == "__main__":
    import sys

    prompt = " ".join(sys.argv[1:])
    answer = reason_from_flashbacks(prompt)
    save_result = save_reasoning_drop_compound(answer, prompt)

    label = "[SAVED SHAPE]"
    if isinstance(save_result, dict):
        reason = save_result.get("reason", "")
        if "mutation" in reason:
            label = "[SAVED AUTO-MUTATION]"
        elif save_result.get("source_kind") == "flashback_shape_reasoner_meaning_drop":
            label = "[SAVED MEANING DROP]"

    print(answer)
    print(f"\n{label}", save_result)

