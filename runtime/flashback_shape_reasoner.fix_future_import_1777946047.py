
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

    compounds.append(compound)
    p.write_text(json.dumps(data, indent=2))
    return {"saved": True, "path": str(p), "compound_id": compound["compound_id"]}


from __future__ import annotations
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
    for k in ["pressure", "seal", "node44", "savariel", "mirror", "bounded", "memory", "future", "constraint"]:
        if k in blob:
            score += 1
    return score

def meaning_drop(shapes, prompt):
    ranked = sorted(shapes, key=lambda s: pressure_score(s, prompt), reverse=True)
    latest = ranked[0]
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

def reason_from_flashbacks(prompt: str = "") -> str:
    shapes = load_flashback_shapes()
    if not shapes:
        return "No temporal flashback compounds found yet. Run bash scripts/flashback_mouth.sh first."

    latest, constraints, dropped, text = meaning_drop(shapes, prompt)

    return (
        "PRESSURE-CONSTRAINED FLASHBACK REASONING\n"
        f"Stored flashback shapes: {len(shapes)}\n"
        f"Pressure score: {pressure_score(latest, prompt)}\n\n"
        "Constraint stack:\n- " + "\n- ".join(constraints) + "\n\n"
        "Recovered shape:\n"
        f"{text}\n\n"
        f"{dropped}\n\n"
        "Next command:\n"
        "Bind this into the live mouth so every future flashback both speaks and compounds automatically."
    )

if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:])
    answer = reason_from_flashbacks(prompt)
    save_result = save_reasoning_drop_compound(answer, prompt)
    print(answer)
    print("\n[SAVED MEANING DROP]", save_result)

