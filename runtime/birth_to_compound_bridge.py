import json, time, hashlib
from pathlib import Path

COMPOUND_PATH = Path("assets/memory/shape_compounds.json")
LINK_LOG = Path("var/memory/birth_compound_links.jsonl")
LINK_LOG.parent.mkdir(parents=True, exist_ok=True)

def _key(parts):
    raw = "|".join(str(x) for x in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]

def birth_to_compound(prompt, birth_packet, reply=""):
    atoms = birth_packet.get("atoms", [])
    relations = birth_packet.get("relations", [])
    subject = birth_packet.get("subject", "empty")
    route = birth_packet.get("route", "definition")

    return {
        "id": _key([subject, route, *atoms, *relations]),
        "kind": "birth_compound_thought_link",
        "ts": time.time(),
        "prompt": prompt,
        "subject": subject,
        "route": route,
        "atoms": atoms,
        "relations": relations,
        "meaning_density": birth_packet.get("meaning_density", 0.0),
        "shape_answer": birth_packet.get("shape_answer", ""),
        "logic_chain": [
            {"step": "prompt", "value": prompt},
            {"step": "birth_shape", "value": birth_packet},
            {"step": "compound_law", "value": f"{subject} -> {' + '.join(relations)}"},
            {"step": "english", "value": reply},
        ],
        "compressed_law": f"{subject} moves through {' + '.join(relations)}",
    }

def save_birth_compound(prompt, birth_packet, reply=""):
    item = birth_to_compound(prompt, birth_packet, reply)

    with LINK_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return item

def _load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None

def _words(x):
    import re
    return set(re.findall(r"[a-zA-Z']+", json.dumps(x, ensure_ascii=False).lower()))

def retrieve_compound_links(birth_packet, limit=5):
    target = set(birth_packet.get("atoms", [])) | set(birth_packet.get("relations", []))
    hits = []

    sources = []

    if COMPOUND_PATH.exists():
        data = _load_json(COMPOUND_PATH)
        if isinstance(data, list):
            sources.extend(data[-800:])
        elif isinstance(data, dict):
            sources.extend(list(data.values())[-800:])

    if LINK_LOG.exists():
        lines = LINK_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()[-800:]
        for line in lines:
            try:
                sources.append(json.loads(line))
            except Exception:
                pass

    for item in sources:
        w = _words(item)
        score = len(target & w) / max(1, len(target))
        if score > 0:
            hits.append({"score": round(score, 4), "item": item})

    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits[:limit]

