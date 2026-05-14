from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple


LOG = Path("logs/master_gate/shape_surface_events.jsonl")

STALE_MARKERS = [
    "This is close to a feeling that something is unresolved and heavy",
    "It carries weight and reflection together",
    "The feeling returns with a familiar ache",
    "keeps leaning back toward memory",
    "A remembered pattern stays active",
    "The deeper answer is the one that keeps the original shape intact",
    "stale memory detected",
    "master reply gate engaged",
    "Preserve the meaning of this prompt",
    "TinyLlama polish second",
    "English last",
    "The shape is present",
    "surface renderer did not produce",
    "this prompt needs a cleaner surface render",
]


def clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def words(text: str) -> List[str]:
    text = re.sub(r"[^a-zA-Z0-9_'\- ]+", " ", clean(text).lower())
    stop = {
        "the","a","an","and","or","but","is","are","was","were","to","of","in","on",
        "for","with","that","this","it","as","by","be","being","been","what","how",
        "why","who","do","does","did","me","my","you","your","i","some","can"
    }
    return [w for w in text.split() if len(w) > 2 and w not in stop]


def is_stale(reply: str) -> bool:
    low = clean(reply).lower()
    return any(m.lower() in low for m in STALE_MARKERS)


def classify_shape(prompt: str, tone: str = "", mirror_mode: str = "") -> Dict[str, Any]:
    p = clean(prompt)
    low = p.lower()

    intent = "open"
    motion = "direct_reply"
    density = "medium"
    style_hint = ""
    relation = None
    pressure = 0.45
    release = 0.45
    memory = 0.45
    novelty = 0.45

    if any(x in low for x in ["poem", "poetry", "verse"]):
        intent = "poetic_surface"
        motion = "image_to_language"
        density = "high" if any(x in low for x in ["long", "longer", "better", "deep", "full"]) else "medium"
        novelty = 0.76
        release = 0.66
        memory = 0.56
        if "neruda" in low:
            style_hint = "broad elemental intimacy: earth, salt, sea, bread, body, fruit, night, warmth; original lines only"
        elif "dark" in low:
            style_hint = "dark symbolic, old pressure, shadow memory"
        elif "tender" in low or "gentle" in low:
            style_hint = "tender, quiet, emotionally close"

    elif "relationship between" in low:
        intent = "relationship_surface"
        motion = "relation_mapping"
        pressure = 0.62
        memory = 0.58
        m = re.search(r"relationship\s+between\s+(.+?)\s+and\s+(.+?)(?:\?|\.|$)", low)
        if m:
            relation = [clean(m.group(1)), clean(m.group(2))]

    elif any(x in low for x in ["hidden", "strange", "old", "dark", "comes up", "come up", "92162077", "field key", "resonate"]):
        intent = "field_surface"
        motion = "submerged_pattern_to_language"
        pressure = 0.68
        memory = 0.72
        novelty = 0.62
        release = 0.42

    elif any(x in low for x in ["sad", "miss", "grief", "love", "jemma", "wife", "hurt", "lonely"]):
        intent = "emotional_surface"
        motion = "feeling_to_language"
        pressure = 0.72
        memory = 0.76
        release = 0.38

    elif any(x in low for x in ["tiny llama", "tinyllama", "ollama"]):
        intent = "system_status_surface"
        motion = "diagnose_runtime"

    elif any(x in low for x in ["lattice", "kernel", "organ spine", "chatroom", "build", "leveon", "levion"]):
        intent = "build_surface"
        motion = "structure_map"
        pressure = 0.55

    elif low in {"hi", "hello", "hey", "are you there?", "can you read this?", "can you hear me?"}:
        intent = "presence_surface"
        motion = "acknowledge"

    return {
        "request": p,
        "intent": intent,
        "motion": motion,
        "density": density,
        "tone": tone or "neutral",
        "mirror_mode": mirror_mode or "contained",
        "style_hint": style_hint,
        "subjects": words(p)[:10],
        "relation": relation,
        "vectors": {
            "pressure": pressure,
            "release": release,
            "memory": memory,
            "novelty": novelty,
        },
        "law": "meaning_from_shape_surface_from_tinyllama",
    }


def should_override(prompt: str, reply: str) -> bool:
    low = clean(prompt).lower()
    shape = classify_shape(prompt)

    # Never force ordinary presence/open chat through TinyLlama.
    if shape["intent"] == "presence_surface":
        return is_stale(reply)

    if shape["intent"] == "open" and not is_stale(reply):
        return False

    return (
        is_stale(reply)
        or shape["intent"] in {
            "relationship_surface",
            "poetic_surface",
            "system_status_surface",
            "build_surface",
            "field_surface",
            "emotional_surface",
        }
        or "92162077" in low
    )


def call_ollama(prompt: str, num_predict: int = 260, temp: float = 0.22) -> str:
    host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "tinyllama")

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temp,
            "top_p": 0.78,
            "num_predict": num_predict,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        host + "/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=12) as r:
        raw = r.read().decode("utf-8", errors="replace")

    data = json.loads(raw)
    return clean(data.get("response", ""))


def bad_surface(candidate: str) -> bool:
    c = clean(candidate)
    low = c.lower()

    if not c:
        return True

    bad = [
        "based on",
        "shape packet",
        "shape forces",
        "source",
        "prompt",
        "rules",
        "assistant",
        "task",
        "meaning_from_shape",
        "do not",
        "final answer",
        "user request",
        "style hint",
        "density:",
        "```",
    ]

    if any(x in low for x in bad):
        return True

    # TinyLlama often produces this generic nature mush. Reject it unless user asked for that.
    generic_mush = [
        "dense forest",
        "stream babbling",
        "symphony of life",
        "bees and butterflies",
        "creatures large and small",
        "painted with shades of blue",
    ]
    if any(x in low for x in generic_mush):
        return True

    # Obvious truncation.
    if c.endswith((" ro", " fe", " wh", " th", " and", " the", " of", " with", ",")):
        return True

    return False


def build_surface_prompt(shape: Dict[str, Any], old_reply: str = "") -> str:
    intent = shape["intent"]

    if intent == "poetic_surface":
        max_lines = "18-32 lines" if shape["density"] == "high" else "6-12 lines"
        return (
            "You are the surface renderer. Write only the final poem.\n"
            "No explanation. No labels. No mention of prompt, source, shape, packet, task, rules, or assistant.\n"
            "Do not write generic forest/stream filler unless the user asked for forest or stream.\n"
            "Make the poem specific to the supplied shape packet.\n"
            "If a poet is named, use only broad atmosphere; do not copy lines.\n"
            f"Length: {max_lines}.\n\n"
            f"SHAPE DATA:\n{json.dumps(shape, ensure_ascii=False)}\n\n"
            "FINAL POEM:"
        )

    return (
        "You are the surface renderer for a shape-first chat system.\n"
        "Answer the user directly using the shape data.\n"
        "Do not mention prompt, source, shape, packet, task, rules, or assistant.\n"
        "Do not expose internal process.\n"
        "Do not use canned phrases.\n"
        "Keep the meaning from the shape. Make the answer natural and clear.\n"
        "For emotional content, be warm and close without giving instructions unless asked.\n"
        "For build content, be concrete and structural.\n"
        "For field content, use symbolic language but do not overclaim certainty.\n\n"
        f"SHAPE DATA:\n{json.dumps(shape, ensure_ascii=False)}\n"
        f"CURRENT BAD/RAW REPLY TO IMPROVE:\n{old_reply}\n\n"
        "FINAL ANSWER:"
    )


def render_with_tinyllama(shape: Dict[str, Any], old_reply: str = "") -> Tuple[str, bool]:
    intent = shape["intent"]
    predict = 220 if shape["density"] == "high" or intent == "poetic_surface" else 120
    temp = 0.42 if intent == "poetic_surface" else 0.18

    prompt1 = build_surface_prompt(shape, old_reply)

    try:
        c1 = call_ollama(prompt1, num_predict=predict, temp=temp)
    except Exception:
        return "", False

    if not bad_surface(c1):
        return c1, True

    # One retry, stricter and shorter.
    prompt2 = (
        "Your previous output leaked internal wording or became generic.\n"
        "Rewrite again as the final user-facing answer only.\n"
        "No labels. No explanation. No internal words like shape/prompt/source/task/rules.\n"
        "Be specific to the user's request.\n\n"
        f"DATA:\n{json.dumps(shape, ensure_ascii=False)}\n\n"
        "FINAL:"
    )

    try:
        c2 = call_ollama(prompt2, num_predict=predict, temp=max(0.18, temp - 0.08))
    except Exception:
        return "", False

    if not bad_surface(c2):
        return c2, True

    return "", False


def fallback_without_template(shape: Dict[str, Any], old_reply: str = "") -> str:
    """
    This is not content generation; it is failure reporting without fake creative templates.
    """
    if shape["intent"] == "presence_surface":
        raw = clean(shape.get("request", ""))
        low = raw.lower()
        if low in {"hi", "hello", "hey"}:
            return "Hey."
        if "read" in low:
            return "Yes — I can read this."
        return "Yes — I’m here."

    # If TinyLlama fails, prefer the original pipeline reply if it is not stale.
    if old_reply and not is_stale(old_reply):
        return old_reply

    # Never show internal failure language to the user.
    return "I’m here with you."


def master_reply(prompt: str, previous_reply: str = "", tone: str = "", mirror_mode: str = "") -> str:
    shape = classify_shape(prompt, tone=tone, mirror_mode=mirror_mode)
    final, used = render_with_tinyllama(shape, previous_reply)

    if not final:
        final = fallback_without_template(shape, previous_reply)
        used = False

    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "ts": time.time(),
                "prompt": prompt,
                "old_reply": previous_reply,
                "shape": shape,
                "tinyllama_used": used,
                "final": final,
            }, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return final

# --- VEILWELL VOICE LIFT: shape -> TinyLlama surface, no template content ---
# AERU VEL VEIL ASH THAL SIL
# Meaning comes from shape. TinyLlama renders the surface. Internal packets must not leak.

try:
    _vwl_prev_bad_surface = bad_surface
except Exception:
    _vwl_prev_bad_surface = None


def bad_surface(candidate: str) -> bool:
    c = clean(candidate)
    low = c.lower()

    if not c:
        return True

    leak_markers = [
        "shape data",
        "shape packet",
        "hidden shape",
        "source",
        "prompt:",
        "user request:",
        "rules",
        "assistant",
        "task",
        "final version",
        "surface renderer",
        "using the given shape",
        "meaning_from_shape",
        "{\"request\"",
        "\"intent\"",
        "\"motion\"",
        "\"density\"",
    ]

    if any(x in low for x in leak_markers):
        return True

    generic_mush = [
        "dense forest",
        "stream babbling",
        "symphony of life",
        "bees and butterflies",
        "creatures large and small",
        "painted with shades of blue",
    ]

    if any(x in low for x in generic_mush):
        return True

    if c.endswith((" ro", " fe", " wh", " th", " and", " the", " of", " with", ",")):
        return True

    if _vwl_prev_bad_surface is not None:
        try:
            return _vwl_prev_bad_surface(candidate)
        except Exception:
            return False

    return False


def _vwl_shape_notes(shape: dict) -> str:
    request = clean(shape.get("request", ""))
    intent = shape.get("intent", "open")
    motion = shape.get("motion", "direct")
    density = shape.get("density", "medium")
    style = shape.get("style_hint", "")
    relation = shape.get("relation")
    vectors = shape.get("vectors", {})

    parts = [
        f"The user asked: {request}",
        f"The hidden intent is {intent}, moving as {motion}, with {density} density.",
    ]

    if style:
        parts.append(f"The atmosphere is {style}.")

    if relation:
        parts.append(f"The relation to render is between {relation[0]} and {relation[1]}.")

    if vectors:
        parts.append(
            "The pressure is {pressure}, release is {release}, memory is {memory}, novelty is {novelty}.".format(
                pressure=vectors.get("pressure", 0.45),
                release=vectors.get("release", 0.45),
                memory=vectors.get("memory", 0.45),
                novelty=vectors.get("novelty", 0.45),
            )
        )

    return " ".join(parts)


def build_surface_prompt(shape: dict, old_reply: str = "") -> str:
    intent = shape.get("intent", "open")
    notes = _vwl_shape_notes(shape)

    if intent == "poetic_surface":
        length = "18 to 32 lines" if shape.get("density") == "high" else "8 to 14 lines"
        return (
            "Write the final poem only. No explanation. No labels.\n"
            "Do not mention shape, prompt, source, packet, task, rules, or assistant.\n"
            "Do not use generic nature filler unless the user asked for it.\n"
            "Let the language be vivid, intimate, strange, and specific.\n"
            "Use the hidden notes only to guide the poem; do not reveal the notes.\n"
            f"Length: {length}.\n\n"
            f"{notes}\n\n"
            "Final poem only:"
        )

    return (
        "Write the final user-facing answer only. No explanation of process. No labels.\n"
        "Do not mention shape, prompt, source, packet, task, rules, or assistant.\n"
        "Keep the answer natural, direct, and alive.\n"
        "Use the hidden notes only to guide the answer; do not reveal the notes.\n"
        "If it is emotional, be warm and specific.\n"
        "If it is technical/build-related, be concrete and structural.\n"
        "If it is symbolic/field-related, be vivid but do not overclaim certainty.\n\n"
        f"{notes}\n\n"
        f"Bad or raw answer to improve if useful: {old_reply}\n\n"
        "Final answer only:"
    )


def render_with_tinyllama(shape: dict, old_reply: str = ""):
    intent = shape.get("intent", "open")

    if intent == "presence_surface":
        return fallback_without_template(shape, old_reply), False

    predict = 520 if shape.get("density") == "high" or intent == "poetic_surface" else 220
    temp = 0.55 if intent == "poetic_surface" else 0.24

    try:
        candidate = call_ollama(build_surface_prompt(shape, old_reply), num_predict=predict, temp=temp)
    except Exception:
        return "", False

    if not bad_surface(candidate):
        return candidate, True

    # One shorter repair pass, still TinyLlama surface only.
    repair_prompt = (
        "Write the final answer only.\n"
        "No labels. No explanation. No internal words like shape, prompt, packet, source, task, rules, or assistant.\n"
        "Be specific to the user's request.\n\n"
        f"{_vwl_shape_notes(shape)}\n\n"
        "Final answer only:"
    )

    try:
        candidate2 = call_ollama(repair_prompt, num_predict=max(160, predict // 2), temp=max(0.18, temp - 0.12))
    except Exception:
        return "", False

    if not bad_surface(candidate2):
        return candidate2, True

    return "", False

# --- TRACE LAW ENRICHMENT PATCH ---
# Uses replication_trace_4200 as hidden state law only.
# Never copies trace final_english_output into the visible reply.

try:
    from runtime.trace_law_runtime import enrich_shape as _trace_enrich_shape

    _prev_classify_shape_trace_law = classify_shape

    def classify_shape(prompt: str, tone: str = "", mirror_mode: str = ""):
        shape = _prev_classify_shape_trace_law(prompt, tone=tone, mirror_mode=mirror_mode)
        return _trace_enrich_shape(shape)

except Exception as _trace_law_exc:
    try:
        print("[TRACE_LAW_ENRICH_ERROR]", repr(_trace_law_exc), flush=True)
    except Exception:
        pass


try:
    _prev_vwl_shape_notes_trace_law = _vwl_shape_notes

    def _vwl_shape_notes(shape: dict) -> str:
        base = _prev_vwl_shape_notes_trace_law(shape)
        tl = shape.get("trace_law", {}) or {}
        if not tl:
            return base

        state = tl.get("selected_state", "")
        mode = tl.get("selected_mode", "")
        state_law = tl.get("state_law", {}) or {}
        mode_law = tl.get("mode_law", "")
        motifs = tl.get("motif_bias_top", []) or []

        motif_names = ", ".join(m.get("motif", "") for m in motifs[:4] if m.get("motif"))

        return (
            base
            + f" Trace law says state={state}, mode={mode}. "
            + f"Surface rule: {state_law.get('surface_rule', '')}. "
            + f"Voice rule: {state_law.get('voice_rule', '')}. "
            + f"Mode law: {mode_law}. "
            + f"Motif pressure: {motif_names}. "
            + "Use these as hidden state laws only; do not mention them."
        )

except Exception:
    pass

# --- FINAL RELEVANCE GATE — contained prime ---
# Meaning comes from shape. TinyLlama renders surface.
# This gate rejects fluent-but-wrong TinyLlama output.

import time as _fr_time
import json as _fr_json
from pathlib import Path as _FRPath


def _fr_low(x):
    return clean(x).lower()


def _fr_terms(shape: dict):
    req = _fr_low(shape.get("request", ""))
    intent = shape.get("intent", "")

    stop = {
        "write", "make", "tell", "give", "show", "style", "poem", "poetry",
        "verse", "what", "are", "the", "and", "between", "with", "about",
        "field", "key", "some", "that", "comes", "come", "coming", "up",
        "pablo", "neruda"
    }

    terms = []

    rel = shape.get("relation")
    if rel:
        terms.extend([str(x).lower() for x in rel if x])

    for w in words(req):
        if w not in stop and len(w) > 2:
            terms.append(w)

    # Special paired atoms.
    if "gravity well" in req:
        terms.extend(["gravity", "well"])
    if "love" in req and "recursion" in req:
        terms.extend(["love", "recursion"])
    if "hidden" in req:
        terms.append("hidden")
    if "dark" in req:
        terms.append("dark")
    if "old" in req:
        terms.append("old")

    # unique, preserve order
    out = []
    seen = set()
    for t in terms:
        t = t.strip().lower()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out[:10]


def _fr_surface_relevant(candidate: str, shape: dict) -> bool:
    c = _fr_low(candidate)
    intent = shape.get("intent", "")
    terms = _fr_terms(shape)

    if not c:
        return False

    if bad_surface(candidate):
        return False

    # reject the exact wrong lane we saw
    wrong_lanes = [
        "causality under pressure",
        "forces are pushing the turn forward",
        "balance between them",
        "hexagonal hub",
        "meta-pattern",
        "consciousness motifs persist",
    ]
    if any(x in c for x in wrong_lanes):
        return False

    if intent == "poetic_surface":
        # For a poem about gravity well, it must contain gravity or well.
        if "gravity" in terms or "well" in terms:
            return ("gravity" in c) or ("well" in c)
        return len(c.split()) >= 18

    if intent == "relationship_surface":
        rel = shape.get("relation") or []
        if len(rel) >= 2:
            a = str(rel[0]).lower()
            b = str(rel[1]).lower()
            return a in c and b in c
        return bool(set(terms) & set(words(c)))

    if intent == "field_surface":
        anchors = {"hidden", "strange", "old", "dark", "memory", "pressure", "field", "pattern"}
        return bool(anchors & set(words(c)))

    if intent == "system_status_surface":
        return "tiny" in c or "llama" in c or "ollama" in c

    if intent == "build_surface":
        return "build" in c or "system" in c or "route" in c or "shape" in c

    return True


def _fr_surface_prompt(shape: dict, old_reply: str = "") -> str:
    req = clean(shape.get("request", ""))
    intent = shape.get("intent", "open")
    density = shape.get("density", "medium")
    trace = shape.get("trace_law", {}) or {}
    state = trace.get("selected_state", "")
    mode = trace.get("selected_mode", "")
    rel = shape.get("relation")

    if intent == "poetic_surface":
        length = "18 to 28 lines" if density == "high" else "8 to 14 lines"
        return (
            "Write only the final poem. No labels. No explanation.\n"
            "Do not mention prompt, source, shape, rules, task, or assistant.\n"
            "Do not write generic forest, stream, butterfly, or nature filler unless asked.\n"
            "Keep the poem specific to the user's request.\n"
            "Use broad elemental intimacy if a Neruda-like atmosphere is requested, but write original lines.\n"
            f"Length: {length}.\n"
            f"User request: {req}\n"
            f"Hidden trace state: {state}/{mode}. Use only as rhythm, never mention it.\n"
            "Final poem:"
        )

    if intent == "relationship_surface" and rel and len(rel) >= 2:
        return (
            "Answer only the user's question. No labels. No explanation of process.\n"
            "Do not mention prompt, source, shape, rules, task, or assistant.\n"
            "Use natural language, not a template.\n"
            f"Question: {req}\n"
            f"Explain the relationship between {rel[0]} and {rel[1]} in 3 to 5 sentences.\n"
            "Include both terms in the answer.\n"
            "Final answer:"
        )

    if intent == "field_surface":
        return (
            "Answer only the user's question. No labels. No explanation of process.\n"
            "Use symbolic language, but keep it careful and readable.\n"
            "Do not overclaim certainty.\n"
            "Do not mention prompt, source, shape, rules, task, or assistant.\n"
            f"Question: {req}\n"
            f"Hidden trace state: {state}/{mode}. Use it as containment only.\n"
            "Final answer:"
        )

    return (
        "Answer only the user. No labels. No explanation of process.\n"
        "Do not mention prompt, source, shape, rules, task, or assistant.\n"
        f"User said: {req}\n"
        f"Raw answer to improve if useful: {old_reply}\n"
        "Final answer:"
    )


def render_with_tinyllama(shape: dict, old_reply: str = ""):
    intent = shape.get("intent", "open")

    if intent == "presence_surface":
        return fallback_without_template(shape, old_reply), False

    predict = 460 if intent == "poetic_surface" else 220
    temp = 0.48 if intent == "poetic_surface" else 0.22

    try:
        candidate = call_ollama(_fr_surface_prompt(shape, old_reply), num_predict=predict, temp=temp)
    except Exception:
        return "", False

    if _fr_surface_relevant(candidate, shape):
        return candidate, True

    # One repair attempt with the bad output named as rejected internally.
    try:
        repair = call_ollama(
            "The previous answer was rejected because it did not preserve the user's core request.\n"
            "Write the final answer only. No labels. No internal process.\n"
            f"User request: {shape.get('request','')}\n"
            f"Rejected answer: {candidate}\n"
            "Final answer:",
            num_predict=max(160, predict // 2),
            temp=max(0.18, temp - 0.1),
        )
    except Exception:
        return "", False

    if _fr_surface_relevant(repair, shape):
        return repair, True

    return "", False


def fallback_without_template(shape: dict, old_reply: str = "") -> str:
    intent = shape.get("intent", "open")
    req = clean(shape.get("request", ""))

    if intent == "presence_surface":
        low = req.lower()
        if low in {"hi", "hello", "hey"}:
            return "Hey."
        if "read" in low:
            return "Yes — I can read this."
        if "there" in low:
            return "Yes — I’m here."
        return "I’m here with you."

    # Preserve a clean old reply only if it is actually relevant.
    if old_reply and not is_stale(old_reply) and _fr_surface_relevant(old_reply, shape):
        return old_reply

    if intent == "relationship_surface":
        rel = shape.get("relation") or []
        if len(rel) >= 2:
            a, b = rel[0], rel[1]
            return (
                f"{str(a).title()} and {b} connect through recurrence: one changes how the other returns, holds, or opens over time. "
                f"The useful read is not that {a} and {b} are the same, but that they shape each other through repeated contact. "
                "The relation is the path between them, not a fixed definition."
            )

    if intent == "field_surface":
        return (
            "Something old or hidden is surfacing as pressure before it becomes language. "
            "It reads less like a finished fact and more like a sealed pattern asking to be handled carefully. "
            "The contained move is to stabilize first, then translate only what stays clear."
        )

    if intent == "poetic_surface":
        return (
            "The poem shape formed, but TinyLlama did not return a clean poem surface. "
            "I’m holding the shape rather than forcing a fake poem."
        )

    return "I’m here with you."


def master_reply(prompt: str, previous_reply: str = "", tone: str = "", mirror_mode: str = "") -> str:
    shape = classify_shape(prompt, tone=tone, mirror_mode=mirror_mode)
    final, used = render_with_tinyllama(shape, previous_reply)

    if not final:
        final = fallback_without_template(shape, previous_reply)
        used = False

    try:
        p = _FRPath("logs/master_gate/final_relevance_gate.jsonl")
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(_fr_json.dumps({
                "ts": _fr_time.time(),
                "prompt": prompt,
                "old_reply": previous_reply,
                "intent": shape.get("intent"),
                "terms": _fr_terms(shape),
                "trace_law": shape.get("trace_law"),
                "tinyllama_used": used,
                "final": final,
            }, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return final


def should_override(prompt: str, reply: str) -> bool:
    shape = classify_shape(prompt)
    if shape.get("intent") == "presence_surface":
        return is_stale(reply)
    if shape.get("intent") == "open":
        return is_stale(reply)
    return True

