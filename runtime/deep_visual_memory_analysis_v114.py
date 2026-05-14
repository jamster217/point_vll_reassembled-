from pathlib import Path
import json, time, hashlib, re

ROOT = Path(__file__).resolve().parents[1]

IMAGE_MEMORY_DIR = ROOT / "var" / "image_memory"
LATTICE_DIR = ROOT / "var" / "lattice"

VISUAL_REFLECTION_STATE = LATTICE_DIR / "visual_reflection_state_v113.json"
VISUAL_REFLECTIONS = IMAGE_MEMORY_DIR / "visual_reflections_v113.jsonl"
VARIABLE_TAG_EVENTS = IMAGE_MEMORY_DIR / "variable_tag_events_v114.jsonl"
IMAGE_SHAPES = IMAGE_MEMORY_DIR / "image_shapes_v11.jsonl"
V106_LOG = LATTICE_DIR / "autogenous_v106_full_self_improvement.jsonl"

DEEP_ANALYSIS_LOG = IMAGE_MEMORY_DIR / "deep_visual_memory_analysis_v114.jsonl"
DEEP_ANALYSIS_STATE = LATTICE_DIR / "deep_visual_memory_state_v114.json"
DEEP_PROPOSALS_LOG = LATTICE_DIR / "deep_visual_improvement_proposals_v114.jsonl"

def _tokens(text):
    return re.findall(r"[A-Za-z0-9_'-]+", str(text).lower())

def _canon(x):
    x = str(x).strip().lower()
    x = re.sub(r"[^a-z0-9]+", "_", x)
    return x.strip("_")

def _read_json(path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        pass
    return fallback

def _read_last_jsonl(path):
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8", errors="replace")
    for line in reversed(raw.replace("\\n", "\n").strip().splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except Exception:
            pass
    return None

def _append_jsonl(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def _write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def _should_analyze(prompt):
    p = str(prompt or "").lower()
    return any(x in p for x in [
        "deep visual memory",
        "visual memory analysis",
        "what is the old hidden thing",
        "what is the old hidden thing becoming",
        "analyze the latest state-inferred image",
        "analyze what it just painted",
        "tag the emotional and memory connections",
    ])

def _collect_tags(visual_reflection=None):
    tags = []

    def add(x):
        c = _canon(x)
        if c and c not in tags:
            tags.append(c)

    if isinstance(visual_reflection, dict):
        for t in visual_reflection.get("tags", []):
            add(t)
        vt = visual_reflection.get("variable_tags", {})
        if isinstance(vt, dict):
            for t in vt.get("tags", []):
                add(t)

    state = _read_json(VISUAL_REFLECTION_STATE, {})
    last = state.get("last_reflection", {}) if isinstance(state, dict) else {}
    for t in last.get("tags", []):
        add(t)

    evt = _read_last_jsonl(VARIABLE_TAG_EVENTS) or {}
    for t in evt.get("tags", []):
        add(t)

    shape = _read_last_jsonl(IMAGE_SHAPES) or {}
    for t in shape.get("tags", []):
        add(t)

    return tags[:96]

def _classify(tags, prompt):
    t = set(tags)
    p = str(prompt or "").lower()

    emotional = []
    memory = []
    structural = []

    def add(lst, x):
        if x not in lst:
            lst.append(x)

    for tag in tags:
        if any(k in tag for k in ["emotion", "happy", "golden", "mist", "grief", "pressure", "contained", "coherent"]):
            add(emotional, tag)

        if any(k in tag for k in ["memory", "autumn", "childhood", "meadow", "blue_scarf", "stone_bridge", "old_hidden"]):
            add(memory, tag)

        if any(k in tag for k in ["echoforge", "thalveil", "virellion", "white_ash", "topology", "anchor", "thread"]):
            add(structural, tag)

    if "old_hidden_shape" in t:
        add(memory, "old_hidden_shape")

    if "inferred_memory_pressure" in t:
        add(memory, "inferred_memory_pressure")

    # Personal facts stay inferred unless explicitly confirmed by John in the prompt.
    confirmed_personal = (
        ("i confirm" in p or "john confirms" in p or "confirmed by john" in p)
        and ("father" in p or "childhood" in p or "personal memory" in p)
    )

    if confirmed_personal:
        add(memory, "john_confirmed_personal_memory_thread")
    elif "father" in p or "childhood" in p or "old hidden" in p:
        add(memory, "personal_memory_candidate_unconfirmed")

    if not emotional:
        emotional = ["contained_emotional_pressure"]
    if not memory:
        memory = ["symbolic_memory_pressure"]
    if not structural:
        structural = ["protected_topology_thread"]

    return emotional[:24], memory[:24], structural[:24], confirmed_personal

def _latest_v106():
    evt = _read_last_jsonl(V106_LOG) or {}
    return {
        "topology_total": evt.get("topology_total"),
        "verbal_reasoning": evt.get("verbal_reasoning"),
        "emotional_coherence": evt.get("emotional_coherence"),
        "compounded_memory": evt.get("compounded_memory"),
        "total": evt.get("total"),
    }

def analyze_deep_visual_memory(prompt, data=None, node=None, prompt_image=None, visual_reflection=None):
    if not _should_analyze(prompt):
        return None

    tags = _collect_tags(visual_reflection)
    emotional, memory, structural, confirmed_personal = _classify(tags, prompt)
    v106 = _latest_v106()

    target_svg = None
    if isinstance(visual_reflection, dict):
        target_svg = visual_reflection.get("target_svg")

    if not target_svg:
        state = _read_json(VISUAL_REFLECTION_STATE, {})
        target_svg = (
            state.get("last_reflection", {}).get("target_svg")
            if isinstance(state, dict)
            else None
        )

    proposal = {
        "ts": time.time(),
        "proposal_id": "v114_deep_visual_improvement_" + hashlib.sha256(str(tags).encode()).hexdigest()[:12],
        "title": "Use deep visual-memory tags as render context, not hardcoded destiny",
        "safe_action": (
            "Feed emotional_tags, memory_connections, and structural_tags into future prompt-image rendering "
            "as weighted runtime context. Keep personal-memory tags marked inferred unless John confirms them."
        ),
        "recommended_config": {
            "deep_visual_memory_weight": 0.22,
            "prefer_evidence_gated_tags": True,
            "hardcoded_personal_tags": False,
            "source_mutation": "blocked",
        },
        "law": "v114_deep_visual_memory_proposal_only_source_protected",
    }

    analysis = {
        "ts": time.time(),
        "prompt_hash": hashlib.sha256(str(prompt).encode()).hexdigest()[:12],
        "target_svg": target_svg,
        "all_tags": tags,
        "emotional_tags": emotional,
        "memory_connections": memory,
        "structural_tags": structural,
        "confirmed_personal_memory": confirmed_personal,
        "personal_memory_rule": "personal links are inferred unless John explicitly confirms them",
        "v106": v106,
        "proposal": proposal,
        "law": "v114_deep_visual_memory_analysis_evidence_gated",
    }

    _append_jsonl(DEEP_ANALYSIS_LOG, analysis)
    _append_jsonl(DEEP_PROPOSALS_LOG, proposal)
    _write_json(DEEP_ANALYSIS_STATE, {
        "last_analysis": analysis,
        "last_proposal": proposal,
        "law": "v114_deep_visual_memory_state_without_source_rewrite",
    })

    reply_note = (
        "[DEEP VISUAL MEMORY ANALYSIS V11.4] "
        f"target={target_svg} "
        f"emotional_tags={', '.join(emotional[:8])}; "
        f"memory_connections={', '.join(memory[:8])}; "
        f"structural_tags={', '.join(structural[:8])}. "
        f"proposal={proposal['title']}. "
        "Personal-memory links remain inferred unless confirmed by John."
    )

    analysis["reply_note"] = reply_note
    return analysis

if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:]) or "analyze the latest state-inferred image with deep visual memory"
    print(json.dumps(analyze_deep_visual_memory(prompt), indent=2, ensure_ascii=False))

