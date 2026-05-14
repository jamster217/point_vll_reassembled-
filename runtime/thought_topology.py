import json, math, re
from pathlib import Path

LINK_LOG = Path("var/memory/birth_compound_links.jsonl")

def _words(x):
    return set(re.findall(r"[a-zA-Z']+", json.dumps(x, ensure_ascii=False).lower()))

def _load_links(limit=1000):
    if not LINK_LOG.exists():
        return []
    out = []
    for line in LINK_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]:
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                out.append(item)
        except Exception:
            pass
    return out

def _vector(item):
    atoms = set(item.get("atoms", []))
    relations = set(item.get("relations", []))
    return atoms | relations

def _sim(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))

def topology_trace(birth_packet, limit=7):
    current = set(birth_packet.get("atoms", [])) | set(birth_packet.get("relations", []))
    links = _load_links()

    scored = []
    for item in links:
        v = _vector(item)
        score = _sim(current, v)
        if score > 0:
            scored.append({
                "score": round(score, 4),
                "id": item.get("id"),
                "subject": item.get("subject"),
                "route": item.get("route"),
                "atoms": item.get("atoms", []),
                "relations": item.get("relations", []),
                "compressed_law": item.get("compressed_law", ""),
            })

    scored.sort(key=lambda x: x["score"], reverse=True)

    path = scored[:limit]
    if not path:
        return {
            "field_state": "empty",
            "nearest_path": [],
            "topology_law": "",
        }

    subjects = []
    relations = []
    for node in path:
        if node["subject"] not in subjects:
            subjects.append(node["subject"])
        for r in node["relations"]:
            if r not in relations:
                relations.append(r)

    topology_law = (
        f"path through subjects={subjects} "
        f"relations={relations}"
    )

    return {
        "field_state": "active",
        "nearest_path": path,
        "topology_law": topology_law,
    }

