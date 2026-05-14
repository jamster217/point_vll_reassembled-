import json
import re
from pathlib import Path

SHAPE_PATHS = [
    Path("assets/memory/shape_compounds.json"),
    Path("memory/shape_compounds.json"),
    Path("var/memory/shape_compounds.json"),
]

def _words(text):
    return set(re.findall(r"[a-zA-Z']+", str(text).lower()))

def _load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None

def load_shape_compounds(limit=500):
    for path in SHAPE_PATHS:
        if path.exists():
            data = _load_json(path)
            if isinstance(data, list):
                return data[-limit:]
            if isinstance(data, dict):
                vals = list(data.values())
                return vals[-limit:]
    return []

def find_nearest_shape(prompt, shape, limit=500):
    compounds = load_shape_compounds(limit=limit)
    prompt_words = _words(prompt)
    shape_words = set(shape.get("atoms", [])) | set(shape.get("relations", []))

    best = None
    best_score = 0.0

    for item in compounds:
        text = json.dumps(item, ensure_ascii=False)
        w = _words(text)
        if not w:
            continue

        overlap = len((prompt_words | shape_words) & w)
        score = overlap / max(1, len(prompt_words | shape_words))

        if score > best_score:
            best_score = score
            best = item

    return {
        "score": round(best_score, 4),
        "memory": best,
    }

