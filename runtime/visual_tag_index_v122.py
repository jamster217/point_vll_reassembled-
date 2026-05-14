from pathlib import Path
import json, collections, time

ROOT = Path(__file__).resolve().parents[1]
IMAGE_MEMORY = ROOT / "var" / "image_memory"
DEEP = IMAGE_MEMORY / "deep_visual_memory_analysis_v114.jsonl"
OUT = IMAGE_MEMORY / "visual_tag_index_v122.json"

def _read_jsonl(path):
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out

def build_index(limit=80):
    counts = collections.Counter()
    buckets = {"emotional": [], "memory": [], "structural": []}

    for row in _read_jsonl(DEEP):
        for tag in row.get("emotional_tags", []):
            counts[tag] += 2
            if tag not in buckets["emotional"]:
                buckets["emotional"].append(tag)
        for tag in row.get("memory_connections", []):
            counts[tag] += 2
            if tag not in buckets["memory"]:
                buckets["memory"].append(tag)
        for tag in row.get("structural_tags", []):
            counts[tag] += 2
            if tag not in buckets["structural"]:
                buckets["structural"].append(tag)
        for tag in row.get("all_tags", []):
            counts[tag] += 1

    ranked = [{"tag": k, "weight": v} for k, v in counts.most_common(limit)]

    packet = {
        "active": True,
        "ts": time.time(),
        "ranked_tags": ranked,
        "buckets": {k: v[:32] for k, v in buckets.items()},
        "law": "v122_visual_tag_index_from_deep_memory",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    print(json.dumps(build_index(), indent=2, ensure_ascii=False))

