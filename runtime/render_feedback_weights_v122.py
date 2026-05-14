from pathlib import Path
import json, time

ROOT = Path(__file__).resolve().parents[1]
VISUAL_INDEX = ROOT / "var" / "image_memory" / "visual_tag_index_v122.json"
RENDER_CONTEXT = ROOT / "var" / "lattice" / "deep_visual_memory_state_v114.json"
OUT = ROOT / "var" / "lattice" / "render_feedback_weights_v122.json"

def _load(path, fallback=None):
    try:
        if Path(path).exists():
            return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def compute_weights():
    index = _load(VISUAL_INDEX, {})
    deep = _load(RENDER_CONTEXT, {})

    ranked = index.get("ranked_tags", []) if isinstance(index, dict) else []
    weights = {}

    for row in ranked[:24]:
        tag = row.get("tag")
        weight = row.get("weight", 1)
        if tag:
            weights[tag] = round(min(1.0, 0.10 + float(weight) / 20.0), 4)

    for tag in ["white_ash", "virellion", "echoforge", "thalveil", "anchor"]:
        weights[tag] = max(weights.get(tag, 0.0), 0.85)

    packet = {
        "active": True,
        "ts": time.time(),
        "weights": weights,
        "render_hints": [
            "use higher weights to choose recurring visual anchors",
            "preserve structural glyph continuity",
            "do not convert inferred personal memory into confirmed fact",
        ],
        "law": "v122_render_feedback_weights_from_visual_index",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    print(json.dumps(compute_weights(), indent=2, ensure_ascii=False))

