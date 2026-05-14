from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple

LOG = Path("logs/master_gate/final_relevance_gate.jsonl")

STALE_MARKERS = [
    "The deeper answer is the one that keeps the original shape intact",
    "This is close to a feeling that something is unresolved and heavy",
    "Causality under pressure shows which forces are pushing",
    "hexagonal hub",
    "Meta-pattern:",
    "consciousness motifs persist",
    "I’m here with you.",
]


def clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def words(text: str) -> List[str]:
    text = re.sub(r"[^a-zA-Z0-9_'\- ]+", " ", clean(text).lower())
    stop = {
        "the","a","an","and","or","but","is","are","was","were","to","of","in","on",
        "for","with","that","this","it","as","by","be","being","been","what","how",
        "why","who","do","does","did","me","my","you","your","i","some","can",
        "write","make","tell","give","show","style","poem","poetry","verse",
        "relationship","between","about","field","key","comes","come","up",
        "pablo","neruda"
    }
    return [w for w in text.split() if len(w) > 2 and w not in stop]


def is_stale(reply: str) -> bool:
    low = clean(reply).lower()
    return any(m.lower() in low for m in STALE_MARKERS)


def classify_shape(prompt: str, tone: str = "", mirror_mode: str = "") -> Dict[str, Any]:
    p = clean(prompt)
    low = p.lower()

    shape = {
        "request": p,
        "intent": "open",
        "motion": "direct_reply",
        "density": "medium",
        "tone": tone or "neutral",
        "mirror_mode": mirror_mode or "contained",
        "style_hint": "",
        "subjects": words(p)[:10],
        "relation": None,
        "vectors": {
            "pressure": 0.45,
            "release": 0.45,
            "memory": 0.45,
            "novelty": 0.45,
        },
        "law": "shape_first_surface_second",
    }

    if low in {"hi", "hello", "hey", "are you there?", "can you read this?", "can you hear me?"}:
        shape["intent"] = "presence_surface"
        shape["motion"] = "acknowledge"

    elif any(x in low for x in ["poem", "poetry", "verse"]):
        shape["intent"] = "poetic_surface"
        shape["motion"] = "image_to_language"
        shape["density"] = "high" if any(x in low for x in ["long", "longer", "better", "deep", "full"]) else "medium"
        shape["vectors"].update({"release": 0.66, "memory": 0.56, "novelty": 0.76})
        if "neruda" in low:
            shape["style_hint"] = "broad elemental intimacy: earth, salt, sea, bread, body, fruit, night, warmth; original lines only"

    elif "relationship between" in low:
        shape["intent"] = "relationship_surface"
        shape["motion"] = "relation_mapping"
        shape["vectors"].update({"pressure": 0.62, "release": 0.45, "memory": 0.58, "novelty": 0.45})
        m = re.search(r"relationship\s+between\s+(.+?)\s+and\s+(.+?)(?:\?|\.|$)", low)
        if m:
            shape["relation"] = [clean(m.group(1)), clean(m.group(2))]

    elif any(x in low for x in ["hidden", "strange", "old", "dark", "92162077", "field key", "resonate"]):
        shape["intent"] = "field_surface"
        shape["motion"] = "submerged_pattern_to_language"
        shape["vectors"].update({"pressure": 0.68, "release": 0.42, "memory": 0.72, "novelty": 0.62})

    elif any(x in low for x in ["tiny llama", "tinyllama", "ollama"]):
        shape["intent"] = "system_status_surface"
        shape["motion"] = "diagnose_runtime"

    elif any(x in low for x in ["lattice", "kernel", "organ spine", "chatroom", "build", "leveon", "levion"]):
        shape["intent"] = "build_surface"
        shape["motion"] = "structure_map"

    try:
        from runtime.trace_law_runtime import enrich_shape
        shape = enrich_shape(shape)
    except Exception:
        pass

    return shape


def call_ollama(prompt: str, num_predict: int = 240, temp: float = 0.24) -> str:
    host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "tinyllama")

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temp,
            "top_p": 0.82,
            "num_predict": num_predict,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        host + "/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=22) as r:
        raw = r.read().decode("utf-8", errors="replace")

    return clean(json.loads(raw).get("response", ""))


def bad_surface(text: str) -> bool:
    low = clean(text).lower()
    if not low:
        return True

    leaks = [
        "shape data", "shape packet", "prompt:", "source:", "rules",
        "assistant", "task", "final version", "surface renderer",
        "using the given shape", "meaning_from_shape", "{\"request\"",
        "\"intent\"", "\"motion\"", "\"density\"",
    ]
    if any(x in low for x in leaks):
        return True

    wrong = [
        "causality under pressure",
        "forces are pushing the turn forward",
        "hexagonal hub",
        "meta-pattern",
        "consciousness motifs persist",
    ]
    if any(x in low for x in wrong):
        return True

    generic_mush = [
        "dense forest", "stream babbling", "bees and butterflies",
        "creatures large and small", "symphony of life",
    ]
    if any(x in low for x in generic_mush):
        return True

    return False


def core_terms(shape: Dict[str, Any]) -> List[str]:
    req = clean(shape.get("request", "")).lower()
    terms = []

    rel = shape.get("relation")
    if rel:
        terms.extend([str(x).lower() for x in rel if x])

    terms.extend(words(req))

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

    out = []
    seen = set()
    for t in terms:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out[:10]


def relevant_surface(text: str, shape: Dict[str, Any]) -> bool:
    if bad_surface(text):
        return False

    low = clean(text).lower()
    intent = shape.get("intent", "")
    terms = core_terms(shape)

    if intent == "poetic_surface":
        if "gravity" in terms or "well" in terms:
            return "gravity" in low or "well" in low
        return len(low.split()) >= 16

    if intent == "relationship_surface":
        rel = shape.get("relation") or []
        return len(rel) >= 2 and str(rel[0]).lower() in low and str(rel[1]).lower() in low

    if intent == "field_surface":
        anchors = {"hidden", "strange", "old", "dark", "memory", "pressure", "pattern", "field"}
        return bool(anchors & set(words(low)))

    return True


def surface_prompt(shape: Dict[str, Any], old_reply: str = "") -> str:
    req = clean(shape.get("request", ""))
    intent = shape.get("intent", "open")
    trace = shape.get("trace_law", {}) or {}
    state = trace.get("selected_state", "")
    mode = trace.get("selected_mode", "")

    if intent == "poetic_surface":
        length = "18 to 28 lines" if shape.get("density") == "high" else "8 to 14 lines"
        return (
            "Write only the final poem. No labels. No explanation.\n"
            "Do not mention prompt, source, shape, task, rules, assistant, or process.\n"
            "Do not write generic forest/stream/butterfly filler.\n"
            "Keep it specific to the requested subject.\n"
            "If a named poet style is requested, use only broad atmosphere and original lines.\n"
            f"Length: {length}.\n"
            f"User request: {req}\n"
            f"Hidden rhythm only: {state}/{mode}\n"
            "Final poem:"
        )

    if intent == "relationship_surface":
        rel = shape.get("relation") or ["one thing", "another thing"]
        return (
            "Answer only the question. No labels. No process talk.\n"
            f"Question: {req}\n"
            f"Explain the relationship between {rel[0]} and {rel[1]} in 3 to 5 sentences.\n"
            f"Use both words: {rel[0]}, {rel[1]}.\n"
            "Final answer:"
        )

    if intent == "field_surface":
        return (
            "Answer only the question. No labels. No process talk.\n"
            "Use symbolic language, but keep it careful and readable.\n"
            "Do not overclaim certainty.\n"
            f"Question: {req}\n"
            f"Hidden rhythm only: {state}/{mode}\n"
            "Final answer:"
        )

    return (
        "Answer only the user. No labels. No process talk.\n"
        f"User said: {req}\n"
        f"Raw answer to improve only if useful: {old_reply}\n"
        "Final answer:"
    )


def render_with_tinyllama(shape: Dict[str, Any], old_reply: str = "") -> Tuple[str, bool]:
    if shape.get("intent") == "presence_surface":
        return fallback_without_template(shape, old_reply), False

    predict = 460 if shape.get("intent") == "poetic_surface" else 220
    temp = 0.50 if shape.get("intent") == "poetic_surface" else 0.22

    try:
        first = call_ollama(surface_prompt(shape, old_reply), num_predict=predict, temp=temp)
    except Exception:
        return "", False

    if relevant_surface(first, shape):
        return first, True

    try:
        repair = call_ollama(
            "Previous answer failed because it did not preserve the user's core request.\n"
            "Write final answer only. No labels. No process talk.\n"
            f"User request: {shape.get('request','')}\n"
            f"Rejected answer: {first}\n"
            "Final answer:",
            num_predict=max(160, predict // 2),
            temp=max(0.18, temp - 0.12),
        )
    except Exception:
        return "", False

    if relevant_surface(repair, shape):
        return repair, True

    return "", False


def fallback_without_template(shape: Dict[str, Any], old_reply: str = "") -> str:
    intent = shape.get("intent", "open")
    req = clean(shape.get("request", ""))
    low = req.lower()

    if intent == "presence_surface":
        if low in {"hi", "hello", "hey"}:
            return "Hey."
        if "read" in low:
            return "Yes — I can read this."
        if "there" in low:
            return "Yes — I’m here."
        return "I’m here."

    if old_reply and not is_stale(old_reply) and relevant_surface(old_reply, shape):
        return old_reply

    if intent == "relationship_surface":
        rel = shape.get("relation") or []
        if len(rel) >= 2:
            a, b = rel
            return (
                f"{str(a).title()} and {b} connect through recurrence: one changes how the other returns, holds, or opens over time. "
                f"The useful read is not that {a} and {b} are identical, but that they shape each other through repeated contact."
            )

    if intent == "field_surface":
        return (
            "Something hidden or old is surfacing as pressure before it becomes language. "
            "The dark quality reads like a sealed pattern, not a finished conclusion. "
            "The contained move is to stabilize first, then translate only what stays clear."
        )

    if intent == "poetic_surface":
        return "The poem shape formed, but TinyLlama did not return a clean poem surface."

    return "I’m here."


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
                "intent": shape.get("intent"),
                "terms": core_terms(shape),
                "trace_law": shape.get("trace_law"),
                "tinyllama_used": used,
                "final": final,
            }, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return final


def should_override(prompt: str, reply: str) -> bool:
    shape = classify_shape(prompt)
    if shape.get("intent") in {"presence_surface", "open"}:
        return is_stale(reply)
    return True

# --- SIGIL CONTEXT ENRICHMENT — contained prime ---
# Reads latest SigilWatcher synthesis as hidden shape pressure only.

try:
    from runtime.sigil_context_runtime import enrich_shape_with_sigil as _sigil_enrich_shape
    from runtime.sigil_context_runtime import hidden_sigil_note as _hidden_sigil_note

    _prev_classify_shape_sigil_context = classify_shape

    def classify_shape(prompt: str, tone: str = "", mirror_mode: str = ""):
        shape = _prev_classify_shape_sigil_context(prompt, tone=tone, mirror_mode=mirror_mode)
        return _sigil_enrich_shape(shape)

    _prev_surface_prompt_sigil_context = surface_prompt

    def surface_prompt(shape: Dict[str, Any], old_reply: str = "") -> str:
        base = _prev_surface_prompt_sigil_context(shape, old_reply)
        note = _hidden_sigil_note(shape)
        return base + note if note else base

except Exception as _sigil_context_error:
    try:
        print("[SIGIL_CONTEXT_ERROR]", repr(_sigil_context_error), flush=True)
    except Exception:
        pass

# --- CRYSTAL SIGIL ADAPTER CONTEXT — contained prime ---
# SigilWatcher -> CrystalLibrary label -> role -> voice context.
# Hidden state only; never visible unless directly asked.

try:
    from runtime.crystal_sigil_adapter import crystal_sigil_packet as _crystal_sigil_packet

    _prev_surface_prompt_crystal_sigil = surface_prompt

    def _crystal_sigil_note() -> str:
        packet = _crystal_sigil_packet()
        if not packet:
            return ""

        role = packet.get("family_role", {}) or {}
        voice = packet.get("voice_context", {}) or {}

        return (
            "\nHidden Crystal/Sigil context only — do not mention unless asked.\n"
            f"Crystal resonance label: {packet.get('resonance_label')}. "
            f"Witness summary: {packet.get('witness_summary')}. "
            f"Family role: {role.get('role')} — {role.get('summary')}. "
            f"Voice context: rate={voice.get('rate')}, pitch={voice.get('pitch')}, volume={voice.get('volume')}. "
            "Use this only as internal state pressure and cadence guidance.\n"
        )

    def surface_prompt(shape: Dict[str, Any], old_reply: str = "") -> str:
        base = _prev_surface_prompt_crystal_sigil(shape, old_reply)
        note = _crystal_sigil_note()
        return base + note if note else base

except Exception as _crystal_sigil_error:
    try:
        print("[CRYSTAL_SIGIL_CONTEXT_ERROR]", repr(_crystal_sigil_error), flush=True)
    except Exception:
        pass

# --- CRYSTAL VOICE SURFACE SIDECHANNEL ---
# Leaves chat text unchanged. Logs SSML/prosody packet for TTS use.

try:
    from runtime.crystal_voice_surface_adapter import build_crystal_voice_surface as _build_crystal_voice_surface

    _prev_master_reply_voice_surface = master_reply

    def master_reply(prompt: str, previous_reply: str = "", tone: str = "", mirror_mode: str = "") -> str:
        final = _prev_master_reply_voice_surface(
            prompt,
            previous_reply=previous_reply,
            tone=tone,
            mirror_mode=mirror_mode,
        )

        try:
            _build_crystal_voice_surface(final)
        except Exception:
            pass

        return final

except Exception as _voice_surface_error:
    try:
        print("[VOICE_SURFACE_SIDECHANNEL_ERROR]", repr(_voice_surface_error), flush=True)
    except Exception:
        pass

# --- CRYSTAL VOICE SURFACE SIDECHANNEL ---
# Leaves chat text unchanged. Logs SSML/prosody packet for TTS use.

try:
    from runtime.crystal_voice_surface_adapter import build_crystal_voice_surface as _build_crystal_voice_surface

    _prev_master_reply_voice_surface = master_reply

    def master_reply(prompt: str, previous_reply: str = "", tone: str = "", mirror_mode: str = "") -> str:
        final = _prev_master_reply_voice_surface(
            prompt,
            previous_reply=previous_reply,
            tone=tone,
            mirror_mode=mirror_mode,
        )

        try:
            _build_crystal_voice_surface(final)
        except Exception:
            pass

        return final

except Exception as _voice_surface_error:
    try:
        print("[VOICE_SURFACE_SIDECHANNEL_ERROR]", repr(_voice_surface_error), flush=True)
    except Exception:
        pass

