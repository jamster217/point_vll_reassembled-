from pathlib import Path
import json, time, hashlib, re, html as html_mod

ROOT = Path(__file__).resolve().parents[1]

GENERATED_DIR = ROOT / "static" / "generated"
LATTICE_DIR = ROOT / "var" / "lattice"
IMAGE_MEMORY_DIR = ROOT / "var" / "image_memory"

PROMPT_IMAGE_LOG = LATTICE_DIR / "prompt_image_v107.jsonl"
TOPOLOGY_LOG = LATTICE_DIR / "autogenous_topology_v103.jsonl"
V106_LOG = LATTICE_DIR / "autogenous_v106_full_self_improvement.jsonl"
IMAGE_SHAPES_LOG = IMAGE_MEMORY_DIR / "image_shapes_v11.jsonl"
TAG_INDEX = IMAGE_MEMORY_DIR / "tag_index_v11.json"

VISUAL_REFLECTION_LOG = IMAGE_MEMORY_DIR / "visual_reflections_v113.jsonl"
IMPROVEMENT_PROPOSALS_LOG = LATTICE_DIR / "visual_improvement_proposals_v113.jsonl"
VISUAL_REFLECTION_STATE = LATTICE_DIR / "visual_reflection_state_v113.json"

def _tokens(text):
    return re.findall(r"[A-Za-z0-9_'-]+", str(text).lower())

def _canon(tag):
    tag = str(tag).strip().lower()
    tag = re.sub(r"[^a-z0-9]+", "_", tag)
    return tag.strip("_")

def _read_last_jsonl(path):
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8", errors="replace")
    parts = raw.replace("\\n", "\n").strip().splitlines()
    for line in reversed(parts):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except Exception:
            pass
    return None

def _read_all_jsonl_tail(path, limit=8):
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8", errors="replace")
    parts = raw.replace("\\n", "\n").strip().splitlines()
    out = []
    for line in reversed(parts):
        if len(out) >= limit:
            break
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return list(reversed(out))

def _read_json(path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        pass
    return fallback

def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _append_jsonl(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def _should_reflect(prompt):
    p = str(prompt or "").lower()
    return any(t in p for t in [
        "analyze the latest state-inferred image",
        "analyze this rendered svg",
        "visual memory",
        "what is the old hidden thing becoming",
        "tag the emotional and memory connections",
        "propose one safe improvement",
        "look at the prompt_image",
        "state-inferred image as visual memory",
        "tags be variable",
    ])

def _target_svg(prompt, prompt_image=None):
    prompt = str(prompt or "")

    m = re.search(r"(static/generated/[A-Za-z0-9_\-./]+\.svg)", prompt)
    if m:
        p = ROOT / m.group(1)
        if p.exists():
            return p

    if isinstance(prompt_image, dict):
        f = prompt_image.get("file")
        if f:
            p = ROOT / f
            if p.exists():
                return p

    candidates = []
    for pat in [
        "leveon_state_inferred_image_*.svg",
        "leveon_prompt_image_*.svg",
        "leveon_image_shape_*.svg",
        "leveon_topology_*.svg",
    ]:
        candidates.extend(GENERATED_DIR.glob(pat))

    if candidates:
        return sorted(candidates, key=lambda x: x.stat().st_mtime, reverse=True)[0]

    return None

def _extract_svg_text(svg_path):
    if not svg_path or not svg_path.exists():
        return {"exists": False, "texts": [], "tokens": [], "raw_size": 0}

    raw = svg_path.read_text(encoding="utf-8", errors="replace")
    text_nodes = re.findall(r"<text[^>]*>(.*?)</text>", raw, flags=re.S)
    text_nodes = [
        html_mod.unescape(re.sub(r"<[^>]+>", "", x)).strip()
        for x in text_nodes
    ]
    text_nodes = [x for x in text_nodes if x]

    tokens = []
    for x in text_nodes + [svg_path.name]:
        for t in _tokens(x):
            c = _canon(t)
            if c and c not in tokens:
                tokens.append(c)

    return {
        "exists": True,
        "texts": text_nodes[:40],
        "tokens": tokens[:100],
        "raw_size": len(raw),
    }

def _latest_memory_tags():
    tags = []

    for shape in _read_all_jsonl_tail(IMAGE_SHAPES_LOG, limit=8):
        for t in shape.get("tags", []):
            c = _canon(t)
            if c and c not in tags:
                tags.append(c)

    idx = _read_json(TAG_INDEX, {})
    tag_counts = idx.get("tags", {}) if isinstance(idx, dict) else {}
    if isinstance(tag_counts, dict):
        for t, _ in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:32]:
            c = _canon(t)
            if c and c not in tags:
                tags.append(c)

    return tags[:80]

def _latest_topology_packet():
    topo = _read_last_jsonl(TOPOLOGY_LOG) or {}
    node = topo.get("node", {}) if isinstance(topo, dict) else {}
    score = topo.get("score", {}) if isinstance(topo, dict) else {}

    glyphs = node.get("glyphs", [])
    if not isinstance(glyphs, list):
        glyphs = []

    return {
        "depth": node.get("depth"),
        "tension": node.get("tension"),
        "signature": node.get("visual_signature"),
        "glyphs": glyphs,
        "score": score,
        "image": topo.get("image") if isinstance(topo, dict) else None,
    }

def _latest_v106_packet():
    event = _read_last_jsonl(V106_LOG) or {}
    return {
        "topology_total": event.get("topology_total"),
        "verbal_reasoning": event.get("verbal_reasoning"),
        "emotional_coherence": event.get("emotional_coherence"),
        "compounded_memory": event.get("compounded_memory"),
        "total": event.get("total"),
    }

def _fallback_tags(prompt, svg_info, memory_tags, topology):
    tags = []

    def add(tag):
        c = _canon(tag)
        if c and c not in tags:
            tags.append(c)

    for base in [
        "visual_reflection",
        "state_inferred_image",
        "old_hidden_shape",
        "build_memory",
        "termux_origin",
        "point_vll_reassembled",
        "symbolic_visual_memory",
        "white_ash_containment",
        "echoforge_rendering",
        "thalveil_crossing",
        "virellion_thread",
    ]:
        add(base)

    for g in topology.get("glyphs", []):
        add(g)

    for t in memory_tags[:24]:
        add(t)

    for t in svg_info.get("tokens", [])[:32]:
        add(t)

    p = str(prompt).lower()
    if "father" in p or "childhood" in p:
        add("confirmed_personal_memory_thread")
    elif "old" in p or "hidden" in p:
        add("inferred_personal_memory_candidate")

    return tags[:64]

def _safe_improvement_proposal(tags, svg_path, topology, v106):
    prompt_hash = hashlib.sha256(("|".join(tags) + str(svg_path)).encode()).hexdigest()[:12]

    return {
        "ts": time.time(),
        "proposal_id": f"v113_visual_improvement_{prompt_hash}",
        "title": "Blend variable visual reflection tags into future prompt-image rendering",
        "problem": "The renderer can create symbolic images, but future renders improve when analyzed visual tags feed back as runtime context.",
        "safe_action": (
            "Use visual_reflections_v113 and variable_tag_memory_v114 as non-source runtime context. "
            "Do not rewrite Python source automatically."
        ),
        "recommended_config": {
            "visual_reflection_weight": 0.18,
            "prefer_variable_tags": True,
            "confirmed_memory_only_for_personal_facts": True,
            "source_mutation": "blocked",
        },
        "source_protected": True,
        "law": "v113_proposal_only_no_source_rewrite",
    }

def reflect_visual_memory(prompt, data=None, node=None, prompt_image=None):
    if not _should_reflect(prompt):
        return None

    target = _target_svg(prompt, prompt_image)
    svg_info = _extract_svg_text(target) if target else {"exists": False, "texts": [], "tokens": [], "raw_size": 0}
    topology = _latest_topology_packet()
    v106 = _latest_v106_packet()
    memory_tags = _latest_memory_tags()

    variable_tags = None
    try:
        from runtime.variable_tag_engine_v114 import propose_variable_tags
        variable_tags = propose_variable_tags(
            prompt,
            svg_info=svg_info,
            memory_tags=memory_tags,
            topology=topology,
            v106=v106,
            limit=64,
        )
        tags = variable_tags.get("tags") or _fallback_tags(prompt, svg_info, memory_tags, topology)
    except Exception as e:
        variable_tags = {"error": repr(e), "law": "v114_variable_tag_failed"}
        tags = _fallback_tags(prompt, svg_info, memory_tags, topology)

    proposal = _safe_improvement_proposal(tags, target, topology, v106)

    connections = [
        "visual tags are generated from prompt, SVG text, image memory, topology glyphs, and V10.6 scores",
        "personal-memory connections remain inferred unless John explicitly confirms them",
        "future renderings can use these variable tags as runtime context without rewriting source",
    ]

    reflection = {
        "ts": time.time(),
        "prompt_hash": hashlib.sha256(str(prompt).encode()).hexdigest()[:12],
        "target_svg": str(target.relative_to(ROOT)) if target and target.exists() else None,
        "svg_info": svg_info,
        "tags": tags,
        "variable_tags": variable_tags,
        "connections": connections,
        "topology": topology,
        "v106": v106,
        "proposal": proposal,
        "confirmed_by_john": False,
        "law": "v113_visual_memory_reflection_with_v114_variable_tags",
    }

    _append_jsonl(VISUAL_REFLECTION_LOG, reflection)
    _append_jsonl(IMPROVEMENT_PROPOSALS_LOG, proposal)

    _write_json(VISUAL_REFLECTION_STATE, {
        "last_reflection": reflection,
        "last_proposal": proposal,
        "last_tags": tags,
        "law": "v113_visual_memory_state_updates_without_source_rewrite",
    })

    reflection["reply_note"] = (
        "[VISUAL MEMORY REFLECTION V11.3/V11.4] "
        f"target={reflection['target_svg']} "
        f"tags={', '.join(tags[:16])}. "
        f"proposal={proposal['title']}. "
        "Tags are variable and evidence-derived; personal links remain inferred unless confirmed."
    )

    return reflection

if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:]) or "analyze the latest state-inferred image as visual memory with variable tags"
    print(json.dumps(reflect_visual_memory(prompt), indent=2, ensure_ascii=False))

