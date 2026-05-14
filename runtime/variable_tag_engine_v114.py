from pathlib import Path
import json, re, time, hashlib

ROOT = Path(__file__).resolve().parents[1]
TAG_MEMORY = ROOT / "var" / "image_memory" / "variable_tag_memory_v114.json"
TAG_EVENTS = ROOT / "var" / "image_memory" / "variable_tag_events_v114.jsonl"

STOP = {
    "the","a","an","and","or","of","in","on","under","over","with","without",
    "this","that","these","those","to","as","it","is","are","was","were","be",
    "being","been","for","from","into","through","show","store","analyze","render",
    "image","svg","picture","photo","description","latest","current","what","how",
    "build","system","use","using","your","you","itself","decide","look","looks",
    "clean","link","state","thing","old","hidden","include","possible","like",
    "only","keep","them","evidence","supports","supported","whatever","new",
    "create","let","fixed","variable","not","but","source","protected","future",
    "propose","one","safe","improvement","scores","score","text","prompt",
    "tags","tag","memory","topology","v10","v11","actually","any","them"
}

# These are allowed because they are structural/glyph/system tags, not random prompt debris.
ALLOW = {
    "92162077",
    "point_vll_reassembled",
    "termux_origin",
    "visual_memory",
    "state_inferred_image",
    "old_hidden_shape",
    "build_memory",
    "symbolic_visual_memory",
    "white_ash",
    "white_ash_containment",
    "echoforge",
    "echoforge_rendering",
    "thalveil",
    "thalveil_crossing",
    "virellion",
    "virellion_thread",
    "anchor",
    "co_creator_john",
    "contained_visual_state",
    "thread_preserved",
    "high_coherence_visual",
    "emotionally_coherent_image",
    "compounded_memory_image",
    "inferred_memory_pressure",
    "inferred_personal_memory_candidate",
}

def _tokens(text):
    return re.findall(r"[A-Za-z0-9_'-]+", str(text).lower())

def _canon(x):
    x = str(x).strip().lower()
    x = re.sub(r"[^a-z0-9]+", "_", x)
    return x.strip("_")

def _parts(tag):
    return [p for p in str(tag).split("_") if p]

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

def _is_noise(tag):
    tag = _canon(tag)
    if not tag:
        return True
    if tag in ALLOW:
        return False
    if tag.isdigit():
        return True
    ps = _parts(tag)
    if not ps:
        return True
    if len(ps) > 4:
        return True
    if len(tag) > 64:
        return True
    if any(p in STOP for p in ps):
        return True
    if any(p in {"0","3","10","11","015","090170"} for p in ps):
        return True
    return False

def _suggested_tags(prompt):
    """
    Pulls candidate tags from phrases like:
    'possible tags like buried_terminal_root, amber_recursion_fog...'
    These are suggestions only. They need supporting evidence to survive.
    """
    p = str(prompt or "")
    out = []

    m = re.search(r"possible tags like\s+(.+?)(?:,\s*but|\.|$)", p, re.I)
    if not m:
        return out

    chunk = m.group(1)
    chunk = chunk.replace(" and ", ",")
    for item in chunk.split(","):
        c = _canon(item)
        if c and not _is_noise(c) and c not in out:
            out.append(c)

    return out[:12]

def _add(candidates, tag, source, confidence=0.5, kind="variable"):
    tag = _canon(tag)
    if not tag:
        return

    # Prompt-only junk should not enter.
    if _is_noise(tag):
        return

    rec = candidates.setdefault(tag, {
        "tag": tag,
        "confidence": 0.0,
        "sources": [],
        "kind": kind,
    })

    rec["confidence"] = min(1.0, rec["confidence"] + confidence)

    if source not in rec["sources"]:
        rec["sources"].append(source)

    # Preserve strongest kind if score/system/user-confirmed appears.
    priority = {
        "user_confirmed": 5,
        "score_derived": 4,
        "topology_glyph": 3,
        "memory_retrieved": 2,
        "svg_observed": 2,
        "suggested_candidate": 1,
        "open_prompt_token": 0,
        "open_prompt_phrase": 0,
        "variable": 0,
    }
    if priority.get(kind, 0) > priority.get(rec.get("kind", "variable"), 0):
        rec["kind"] = kind

def _phrase_tags(words):
    """
    Conservative phrase generation.
    Only two-word phrases. No long chained prompt garbage.
    """
    out = []
    for a, b in zip(words, words[1:]):
        if a in STOP or b in STOP:
            continue
        tag = _canon(a + "_" + b)
        if tag and not _is_noise(tag) and tag not in out:
            out.append(tag)
    return out

def _passes_evidence_gate(rec):
    tag = rec["tag"]
    sources = set(rec.get("sources", []))
    confidence = float(rec.get("confidence", 0.0) or 0.0)

    if tag in ALLOW:
        return True

    evidence_sources = {
        "svg_text",
        "image_memory",
        "topology_glyph",
        "topology_score",
        "v106_score",
        "system_inferred",
        "user_confirmed",
    }

    # Suggested tags alone are not evidence.
    has_real_evidence = bool(sources & evidence_sources)

    if "user_confirmed" in sources:
        return True

    if has_real_evidence and confidence >= 0.45:
        return True

    # Prompt + SVG/memory agreement is enough.
    if "prompt" in sources and has_real_evidence and confidence >= 0.40:
        return True

    return False

def propose_variable_tags(prompt, svg_info=None, memory_tags=None, topology=None, v106=None, limit=64):
    svg_info = svg_info or {}
    memory_tags = memory_tags or []
    topology = topology or {}
    v106 = v106 or {}

    candidates = {}

    words = [_canon(w) for w in _tokens(prompt)]
    words = [w for w in words if w and w not in STOP and len(w) >= 3]

    # Prompt words can support, but should not dominate.
    for w in words:
        _add(candidates, w, "prompt", 0.18, "open_prompt_token")

    for ph in _phrase_tags(words):
        _add(candidates, ph, "prompt_phrase", 0.22, "open_prompt_phrase")

    # Explicit possible tags are candidate suggestions, not truth.
    for tag in _suggested_tags(prompt):
        _add(candidates, tag, "suggested_candidate", 0.25, "suggested_candidate")

    # SVG visible text is stronger evidence.
    for t in svg_info.get("tokens", [])[:100]:
        _add(candidates, t, "svg_text", 0.55, "svg_observed")

    # Prior image memory is strong evidence.
    for t in memory_tags[:100]:
        _add(candidates, t, "image_memory", 0.60, "memory_retrieved")

    # Topology glyphs are structural evidence.
    for g in topology.get("glyphs", [])[:40]:
        _add(candidates, g, "topology_glyph", 0.70, "topology_glyph")

    score = topology.get("score", {})
    if isinstance(score, dict):
        if float(score.get("containment", 0) or 0) >= 0.5:
            _add(candidates, "contained_visual_state", "topology_score", 0.75, "score_derived")
        if float(score.get("thread", 0) or 0) >= 0.9:
            _add(candidates, "thread_preserved", "topology_score", 0.75, "score_derived")
        if float(score.get("coherence", 0) or 0) >= 0.75:
            _add(candidates, "high_coherence_visual", "topology_score", 0.75, "score_derived")

    if isinstance(v106, dict):
        if float(v106.get("emotional_coherence", 0) or 0) >= 0.8:
            _add(candidates, "emotionally_coherent_image", "v106_score", 0.75, "score_derived")
        if float(v106.get("compounded_memory", 0) or 0) >= 0.8:
            _add(candidates, "compounded_memory_image", "v106_score", 0.75, "score_derived")

    prompt_l = str(prompt).lower()

    # Confirmation must be explicit. Mentioning "childhood_pressure_candidate" is not confirmation.
    if (
        ("i confirm" in prompt_l or "confirmed by john" in prompt_l or "john confirms" in prompt_l)
        and ("father" in prompt_l or "childhood" in prompt_l or "personal memory" in prompt_l)
    ):
        _add(candidates, "user_confirmed_personal_memory_reference", "user_confirmed", 0.95, "user_confirmed")
    elif "old" in prompt_l or "hidden" in prompt_l or "childhood_pressure_candidate" in prompt_l:
        _add(candidates, "inferred_memory_pressure", "system_inferred", 0.55, "inferred_not_confirmed")
        _add(candidates, "inferred_personal_memory_candidate", "system_inferred", 0.50, "inferred_not_confirmed")

    records = []
    for rec in candidates.values():
        rec["confidence"] = round(min(float(rec.get("confidence", 0.0) or 0.0), 1.0), 4)
        if _passes_evidence_gate(rec):
            records.append(rec)

    records.sort(key=lambda r: (r["confidence"], len(r.get("sources", []))), reverse=True)
    records = records[:limit]
    tags = [r["tag"] for r in records]

    # Relations should not explode. Only use strong semantic tags.
    relation_candidates = [
        r for r in records
        if r["confidence"] >= 0.65
        and r["tag"] not in {"svg", "v10", "topology", "tags", "prompt"}
        and not _is_noise(r["tag"])
    ][:12]

    relations = []
    for i, a in enumerate(relation_candidates):
        for b in relation_candidates[i+1:]:
            relations.append({
                "a": a["tag"],
                "b": b["tag"],
                "relation": "co_present_in_visual_reflection",
                "weight": round(min((a["confidence"] + b["confidence"]) / 2, 1.0), 4),
            })
            if len(relations) >= 36:
                break
        if len(relations) >= 36:
            break

    packet = {
        "ts": time.time(),
        "prompt_hash": hashlib.sha256(str(prompt).encode()).hexdigest()[:12],
        "tags": tags,
        "tag_records": records,
        "relations": relations,
        "rejected_noise_policy": "prompt mechanics, long phrase chains, and unsupported suggestions are filtered",
        "law": "v114b_variable_tags_evidence_gated_not_brittle_not_noisy",
    }

    memory = _load(TAG_MEMORY, {"tags": {}, "relations": {}, "events": 0})
    memory["events"] = int(memory.get("events", 0)) + 1

    for rec in records:
        tag = rec["tag"]
        old = memory["tags"].get(tag, {"count": 0, "confidence_total": 0.0, "sources": []})
        old["count"] += 1
        old["confidence_total"] += rec["confidence"]
        old["avg_confidence"] = round(old["confidence_total"] / old["count"], 4)
        for s in rec.get("sources", []):
            if s not in old["sources"]:
                old["sources"].append(s)
        memory["tags"][tag] = old

    for rel in relations:
        key = rel["a"] + "|" + rel["b"]
        memory["relations"][key] = int(memory["relations"].get(key, 0)) + 1

    _write(TAG_MEMORY, memory)

    TAG_EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with TAG_EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")

    return packet

