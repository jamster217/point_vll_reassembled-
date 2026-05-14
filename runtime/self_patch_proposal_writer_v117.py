from pathlib import Path
import json, time, hashlib

ROOT = Path(__file__).resolve().parents[1]

PATCH_PROPOSALS = ROOT / "var" / "patch_gate" / "proposals"
DEEP_STATE = ROOT / "var" / "lattice" / "deep_visual_memory_state_v114.json"
VARIABLE_TAG_MEMORY = ROOT / "var" / "image_memory" / "variable_tag_memory_v114.json"

def _load(path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def make_render_context_bridge_proposal():
    deep = _load(DEEP_STATE, {})
    tags = []

    last = deep.get("last_analysis", {}) if isinstance(deep, dict) else {}
    for key in ["emotional_tags", "memory_connections", "structural_tags"]:
        for t in last.get(key, []):
            if t not in tags:
                tags.append(t)

    code = '''from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DEEP_STATE = ROOT / "var" / "lattice" / "deep_visual_memory_state_v114.json"
TAG_MEMORY = ROOT / "var" / "image_memory" / "variable_tag_memory_v114.json"

def _load(path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def load_render_context(limit=24):
    """
    Runtime context bridge.
    Reads evidence-gated visual memory tags and returns safe rendering hints.
    Does not mutate source.
    """
    deep = _load(DEEP_STATE, {})
    tag_mem = _load(TAG_MEMORY, {"tags": {}})

    last = deep.get("last_analysis", {}) if isinstance(deep, dict) else {}

    tags = []
    for key in ["emotional_tags", "memory_connections", "structural_tags"]:
        for t in last.get(key, []):
            if t and t not in tags:
                tags.append(t)

    memory_counts = tag_mem.get("tags", {}) if isinstance(tag_mem, dict) else {}
    ranked = sorted(
        memory_counts.items(),
        key=lambda x: (x[1].get("count", 0), x[1].get("avg_confidence", 0)),
        reverse=True,
    )

    for tag, rec in ranked:
        if tag not in tags:
            tags.append(tag)

    tags = tags[:limit]

    return {
        "active": True,
        "tags": tags,
        "render_hints": [
            "prefer evidence-gated visual memory tags",
            "preserve white_ash containment",
            "preserve virellion thread",
            "use emotional and structural tags as runtime context, not hardcoded destiny",
        ],
        "source_mutation": "blocked",
        "law": "v117_render_context_bridge_reads_memory_without_source_mutation",
    }

if __name__ == "__main__":
    print(json.dumps(load_render_context(), indent=2, ensure_ascii=False))
'''

    proposal_id = "v117_create_render_context_bridge_" + hashlib.sha256(code.encode()).hexdigest()[:12]

    proposal = {
        "proposal_id": proposal_id,
        "title": "Create render context bridge from deep visual memory",
        "human_approved": False,
        "ops": [
            {
                "op": "create",
                "path": "runtime/render_context_bridge_v117.py",
                "overwrite": True,
                "content": code,
            }
        ],
        "compile": ["runtime/render_context_bridge_v117.py"],
        "reason": (
            "The deep visual memory loop now produces emotional, memory, and structural tags. "
            "This bridge lets future renderers read those tags as runtime context without hardcoding personal claims."
        ),
        "observed_tags": tags[:24],
        "law": "v117_self_patch_proposal_writer_outputs_reviewable_patch_only",
    }

    PATCH_PROPOSALS.mkdir(parents=True, exist_ok=True)
    path = PATCH_PROPOSALS / f"{proposal_id}.json"
    _write(path, proposal)
    return path

def main():
    path = make_render_context_bridge_proposal()
    print(path)

if __name__ == "__main__":
    main()

