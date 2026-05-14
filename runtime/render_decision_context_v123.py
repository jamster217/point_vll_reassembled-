from pathlib import Path
import json, time

ROOT = Path(__file__).resolve().parents[1]

def _load(path, fallback=None):
    try:
        p = Path(path)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def _call_bridge():
    try:
        from runtime.render_context_bridge_v117 import load_render_context
        return load_render_context()
    except Exception as e:
        return {"active": False, "error": repr(e)}

def build_render_decision_context(limit=32):
    bridge = _call_bridge()

    visual_index = _load(ROOT / "var/image_memory/visual_tag_index_v122.json", {})
    patch_health = _load(ROOT / "var/patch_gate/patch_health_summary_v122.json", {})
    weights = _load(ROOT / "var/lattice/render_feedback_weights_v122.json", {})
    topology = _load(ROOT / "var/lattice/topology_score_history_v122.json", {})

    weighted = weights.get("weights", {}) if isinstance(weights, dict) else {}
    ranked_weights = sorted(weighted.items(), key=lambda x: x[1], reverse=True)

    tags = []

    def add(tag):
        if tag and tag not in tags:
            tags.append(tag)

    for tag, weight in ranked_weights:
        if weight >= 0.7:
            add(tag)

    if isinstance(bridge, dict):
        for tag in bridge.get("tags", []):
            add(tag)

    buckets = visual_index.get("buckets", {}) if isinstance(visual_index, dict) else {}
    for key in ["structural", "emotional", "memory"]:
        for tag in buckets.get(key, [])[:8]:
            add(tag)

    tags = tags[:limit]

    latest_topology = topology.get("latest") if isinstance(topology, dict) else None
    trend = topology.get("trend") if isinstance(topology, dict) else "unknown"
    avg_total = topology.get("avg_total") if isinstance(topology, dict) else None

    source_protected = bool(patch_health.get("source_protected", True)) if isinstance(patch_health, dict) else True

    if latest_topology and isinstance(latest_topology, dict):
        latest_total = latest_topology.get("total")
        containment = latest_topology.get("containment")
    else:
        latest_total = None
        containment = None

    if isinstance(latest_total, (int, float)) and latest_total < 0.88:
        complexity_mode = "simplify_next_render"
    elif containment is not None and containment < 0.75:
        complexity_mode = "increase_boundary_clarity"
    else:
        complexity_mode = "preserve_and_refine"

    decision = {
        "active": True,
        "ts": time.time(),
        "tags": tags,
        "weights": {k: weighted.get(k) for k in tags if k in weighted},
        "render_policy": {
            "complexity_mode": complexity_mode,
            "prefer_weighted_tags": True,
            "preserve_white_ash_containment": "white_ash" in tags,
            "preserve_virellion_thread": "virellion" in tags or "thread_preserved" in tags,
            "personal_memory_confirmation_required": True,
            "source_protected": source_protected,
        },
        "topology": {
            "trend": trend,
            "avg_total": avg_total,
            "latest": latest_topology,
        },
        "patch_health": patch_health,
        "render_hints": [
            "choose recurring high-weight visual anchors first",
            "keep inferred personal-memory tags marked inferred",
            "preserve structural glyph continuity across render cycles",
            "if topology trend falls or latest score is low, simplify the next image instead of adding complexity",
            "if containment is low, add clearer boundary rings and reduce noisy glyph density",
        ],
        "law": "v123_render_decision_context_fuses_memory_weights_topology_and_patch_health",
    }

    out = ROOT / "var/lattice/render_decision_context_v123.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(decision, indent=2, ensure_ascii=False), encoding="utf-8")

    return decision

if __name__ == "__main__":
    print(json.dumps(build_render_decision_context(), indent=2, ensure_ascii=False))

