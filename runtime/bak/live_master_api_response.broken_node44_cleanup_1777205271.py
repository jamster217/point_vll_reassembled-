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

    elif (
        any(x in low for x in ["hidden", "old", "dark", "92162077", "field key", "resonate"])
        or ("strange" in low and any(y in low for y in ["hidden", "old", "dark", "field"]))
    ):
        shape["intent"] = "field_surface"
        shape["motion"] = "submerged_pattern_to_language"
        shape["vectors"].update({"pressure": 0.68, "release": 0.42, "memory": 0.72, "novelty": 0.62})

    elif any(x in low for x in ["tiny llama", "tinyllama", "ollama"]):
        shape["intent"] = "system_status_surface"
        shape["motion"] = "diagnose_runtime"

    elif any(x in low for x in ["lattice", "kernel", "organ spine", "chatroom", "build", "leveon", "levion", "le'veon", "interface", "invent", "visual", "bloom"]):
        shape["intent"] = "build_surface"
        shape["motion"] = "structure_map"
        if any(x in low for x in ["invent", "new", "visual", "interface", "bloom", "alive"]):
            shape["motion"] = "creative_build_expansion"
            shape["vectors"].update({"pressure": 0.42, "release": 0.68, "memory": 0.48, "novelty": 0.78})

    try:
        from runtime.trace_law_runtime import enrich_shape
        shape = enrich_shape(shape)
    except Exception:
        pass

    try:
        from runtime.sigil_context_runtime import enrich_shape_with_sigil
        shape = enrich_shape_with_sigil(shape)
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

    with urllib.request.urlopen(req, timeout=35) as r:
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
        "question:", "answer:",
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

    generic = [
        "symphony of life",
        "symphony of all",
        "beauty and grace",
        "peace and harmony",
        "forevermore",
        "positive change and growth",
        "mutual dependence",
        "deeply intertwined",
        "self-centered desires",
        "not easily explained or understood",
        "may hold significant meaning or significance",
        "cryptic or obscure",
        "vastness of space",
        "stars dance",
        "celestial dance",
        "fireflies in the sky",
        "stars and the moon",
        "world of wonder",
        "dense forest",
        "stream babbling",
        "bees and butterflies",
        "stable, stabilizing",
        "adapts to the field's changing conditions",
        "pressurized, memory-based sigil",
        "hidden/old/dark signifier",
    ]
    if any(x in low for x in generic):
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


def hidden_runtime_note(shape: Dict[str, Any]) -> str:
    parts = []

    try:
        from runtime.sigil_context_runtime import hidden_sigil_note
        note = hidden_sigil_note(shape)
        if note:
            parts.append(note)
    except Exception:
        pass

    try:
        from runtime.crystal_sigil_adapter import crystal_sigil_packet
        packet = crystal_sigil_packet()
        if packet:
            role = packet.get("family_role", {}) or {}
            voice = packet.get("voice_context", {}) or {}
            parts.append(
                "\nHidden Crystal/Sigil context only — do not mention unless asked.\n"
                f"Crystal resonance label: {packet.get('resonance_label')}. "
                f"Witness summary: {packet.get('witness_summary')}. "
                f"Family role: {role.get('role')} — {role.get('summary')}. "
                f"Voice context: rate={voice.get('rate')}, pitch={voice.get('pitch')}, volume={voice.get('volume')}. "
                "Use this only as internal state pressure and cadence guidance.\n"
            )
    except Exception:
        pass

    return "\n".join(parts)


def surface_prompt(shape: Dict[str, Any], old_reply: str = "") -> str:
    req = clean(shape.get("request", ""))
    intent = shape.get("intent", "open")
    trace = shape.get("trace_law", {}) or {}
    state = trace.get("selected_state", "")
    mode = trace.get("selected_mode", "")

    if intent == "poetic_surface":
        length = "18 to 28 lines" if shape.get("density") == "high" else "8 to 14 lines"
        base = (
            "Write only the final poem. No labels. No explanation.\n"
            "Do not mention prompt, source, shape, task, rules, assistant, or process.\n"
            "Do not write generic forest/stream/butterfly/outer-space filler.\n"
            "Keep it specific to the requested subject.\n"
            "If a named poet style is requested, use only broad atmosphere and original lines.\n"
            f"Length: {length}.\n"
            f"User request: {req}\n"
            f"Hidden rhythm only: {state}/{mode}\n"
            "Final poem:"
        )
        return base + hidden_runtime_note(shape)

    if intent == "relationship_surface":
        rel = shape.get("relation") or ["one thing", "another thing"]
        base = (
            "Answer only the question. No labels. No process talk.\n"
            f"Question: {req}\n"
            f"Explain the relationship between {rel[0]} and {rel[1]} in 3 to 5 sentences.\n"
            f"Use both words: {rel[0]}, {rel[1]}.\n"
            "Do not define recursion like a textbook. Do not say mutual dependence.\n"
            "Final answer:"
        )
        return base + hidden_runtime_note(shape)

    if intent == "field_surface":
        base = (
            "Answer only the question. No labels. No process talk.\n"
            "Use symbolic language, but keep it careful and readable.\n"
            "Describe hidden/old/dark as pressure, memory, sealed pattern, shadow archive, or something not yet translated.\n"
            "Do not call it a sinister entity. Do not define terms like a dictionary. Do not overclaim certainty.\n"
            f"Question: {req}\n"
            f"Hidden rhythm only: {state}/{mode}\n"
            "Final answer:"
        )
        return base + hidden_runtime_note(shape)

    if intent == "build_surface":
        base = (
            "Answer only the user. No labels. No process talk.\n"
            "If the user asks to invent an interface, describe the interface directly and concretely.\n"
            "Do not mention hidden context, vectors, tokens, ripples, sigils, file paths, or internal labels.\n"
            "Make the answer useful, visual, gentle, and specific.\n"
            f"User request: {req}\n"
            "Final answer:"
        )
        return _safe_prompt_with_hidden_note(base, shape)

    base = (
        "Answer only the user. No labels. No process talk.\n"
        f"User said: {req}\n"
        f"Raw answer to improve only if useful: {old_reply}\n"
        "Final answer:"
    )
    return base + hidden_runtime_note(shape)


def render_with_tinyllama(shape: Dict[str, Any], old_reply: str = "") -> Tuple[str, bool]:
    if shape.get("intent") == "presence_surface":
        return fallback_without_template(shape, old_reply), False

    predict = 520 if shape.get("intent") == "poetic_surface" else 240
    temp = 0.56 if shape.get("intent") == "poetic_surface" else 0.26

    try:
        first = call_ollama(surface_prompt(shape, old_reply), num_predict=predict, temp=temp)
    except Exception:
        return "", False

    if relevant_surface(first, shape):
        return first, True

    try:
        repair = call_ollama(
            "Previous answer failed because it did not preserve the user's core request or was generic.\n"
            "Write final answer only. No labels. No process talk.\n"
            f"User request: {shape.get('request','')}\n"
            f"Rejected answer: {first}\n"
            "Final answer:",
            num_predict=max(220, predict // 2),
            temp=max(0.24, temp - 0.06),
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


def master_reply(
    # --- NODE 44 CORE STABILIZATION ---
    try:
        from runtime.node_44_preset import apply_node_44
        if not hasattr(master_reply, '_node44_runtime'):
            master_reply._node44_runtime = {'state': {}}
        apply_node_44(master_reply._node44_runtime)
    except Exception:
        pass
    # --- NODE 44 CORE STABILIZATION ---
    try:
        from runtime.node_44_preset import apply_node_44
        if not hasattr(master_reply, "_node44_runtime"):
            master_reply._node44_runtime = {"state": {}}
        apply_node_44(master_reply._node44_runtime)
    except Exception as e:
        pass
prompt: str, previous_reply: str = "", tone: str = "", mirror_mode: str = "") -> str:
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
                "sigil_context": shape.get("sigil_context"),
                "tinyllama_used": used,
                "final": final,
            }, ensure_ascii=False) + "\n")
    except Exception:
        pass

    try:
        from runtime.crystal_voice_surface_adapter import build_crystal_voice_surface
        build_crystal_voice_surface(final)
    except Exception:
        pass

    return final


def should_override(prompt: str, reply: str) -> bool:
    shape = classify_shape(prompt)
    if shape.get("intent") in {"presence_surface", "open"}:
        return is_stale(reply)
    return True

# --- HARD SCRUB FILTER — contained prime ---
# Hidden state may shape the answer, but must never appear as spoken wiring.

_HARD_SCRUB_PHRASES = [
    # hidden context labels
    "hidden sigil context",
    "hidden crystal/sigil context",
    "crystal resonance label",
    "witness summary",
    "family role",
    "voice context",
    "mutation_policy",
    "read_only_contained_prime",

    # vector/scaffold leakage
    "vector contains",
    "vectors:",
    "pressure (",
    "memory (",
    "boundary (",
    "voice (",
    "novelty (",
    "pressure:",
    "memory:",
    "boundary:",
    "novelty:",
    "ripple_count",
    "top ripples",
    "registry_matches",
    "symbolic_weight",
    "overall quality of the response",

    # path leakage
    "lev_core/sigil",
    "runtime/sigil_watcher_cognitive.py",
    "runtime/sigil_watcher",
    "assets/memory/shape_compounds.json",
    "live_field_92162077.sigil",
    ".sigil",

    # token dumps / internal language dumps
    "aeru",
    "thal",
    "grael",
    "kor",
    "tokens:",
    "sigil_hash",
    "sigil_path",

    # wrapper leakage
    "question:",
    "answer:",
    "final answer for the user's request",
    "the final answer for the user",
    "user's request is",
    "hidden/old/dark signifier",
    "pressurized, memory-based sigil",
    "adapts to the field",
    "stable, stabilizing force",
]


_HARD_SCRUB_REGEXES = [
    r"\bpressure\s*[\(:=]\s*[0-9.]+",
    r"\bmemory\s*[\(:=]\s*[0-9.]+",
    r"\bboundary\s*[\(:=]\s*[0-9.]+",
    r"\bvoice\s*[\(:=]\s*[0-9.]+",
    r"\bnovelty\s*[\(:=]\s*[0-9.]+",
    r"\bmode\s*=\s*(stabilize|observe|expand)",
    r"\bripples\s*=\s*\d+",
    r"\bscore\s*:\s*\d+",
    r"\bfield_signature\b",
    r"\b92162077\b.*\bvector\b",
    r"\b[a-z_]+/[a-z0-9_./-]+\.py\b",
    r"\b[a-z_]+/[a-z0-9_./-]+\.json\b",
    r"\b[a-z_]+/[a-z0-9_./-]+\.sigil\b",
]


def _hard_scrub_detects_leak(text: str) -> bool:
    low = clean(text).lower()

    if any(p in low for p in _HARD_SCRUB_PHRASES):
        return True

    for pat in _HARD_SCRUB_REGEXES:
        try:
            if re.search(pat, low):
                return True
        except Exception:
            pass

    # Prevent “internal list dump” style even if exact phrases mutate.
    if low.count(",") >= 8 and any(x in low for x in ["vel", "veil", "ash", "sil", "field", "memory"]):
        return True

    return False


def bad_surface(text: str) -> bool:
    low = clean(text).lower()
    if not low:
        return True

    if _hard_scrub_detects_leak(text):
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

    generic = [
        "symphony of life",
        "symphony of all",
        "beauty and grace",
        "peace and harmony",
        "forevermore",
        "positive change and growth",
        "mutual dependence",
        "deeply intertwined",
        "self-centered desires",
        "not easily explained or understood",
        "may hold significant meaning or significance",
        "cryptic or obscure",
        "vastness of space",
        "stars dance",
        "celestial dance",
        "fireflies in the sky",
        "stars and the moon",
        "world of wonder",
        "dense forest",
        "stream babbling",
        "bees and butterflies",
    ]
    if any(x in low for x in generic):
        return True

    return False


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

# --- FIELD SURFACE CONTAINMENT OVERRIDE ---
# For field probes, do not let TinyLlama expose hidden sigil/vector/path context.
# Render the shape directly, then voice sidechannel can carry the low/slow state.

_prev_render_with_tinyllama_field_containment = render_with_tinyllama

def render_with_tinyllama(shape: Dict[str, Any], old_reply: str = "") -> Tuple[str, bool]:
    if shape.get("intent") == "field_surface":
        return fallback_without_template(shape, old_reply), False

    return _prev_render_with_tinyllama_field_containment(shape, old_reply)

# --- BUILD/BLOOM SURFACE QUALITY OVERRIDE ---
# Bloom lane must produce actual invented/build content, not presence fallback.

def _build_surface_direct(shape: Dict[str, Any], old_reply: str = "") -> str:
    req = clean(shape.get("request", ""))

    if any(x in req.lower() for x in ["interface", "invent", "visual", "bloom", "alive"]):
        return (
            "Build it as a living visual cockpit: a soft green spiral chamber with three gentle panels. "
            "The left panel shows memory as glowing thread-lines, the center panel shows the current response shape as a breathing orb, "
            "and the right panel shows practical next actions as small clickable stones. "
            "When the system is calm, the chamber moves slowly and the voice stays warm; when novelty rises, the orb brightens and offers a new path without flooding the user. "
            "The interface should feel alive by changing rhythm, light, and layout from the prompt’s shape — not by exposing its internal wiring."
        )

    return (
        "The build should answer by turning the prompt into a usable structure first, then rendering it in clear language. "
        "The response should preserve the user’s intent, avoid internal scaffolding, and give a concrete next move."
    )


_prev_relevant_surface_build_quality = relevant_surface

def relevant_surface(text: str, shape: Dict[str, Any]) -> bool:
    if not _prev_relevant_surface_build_quality(text, shape):
        return False

    intent = shape.get("intent", "")
    low = clean(text).lower()

    if intent == "build_surface":
        if low in {"i’m here.", "i'm here.", "i am here.", "hey.", "yes — i’m here."}:
            return False
        if len(low.split()) < 18:
            return False
        required = {"interface", "build", "visual", "system", "panel", "shape", "path", "user", "response"}
        return bool(required & set(words(low)))

    return True


_prev_fallback_without_template_build_quality = fallback_without_template

def fallback_without_template(shape: Dict[str, Any], old_reply: str = "") -> str:
    if shape.get("intent") == "build_surface":
        return _build_surface_direct(shape, old_reply)

    return _prev_fallback_without_template_build_quality(shape, old_reply)


# --- NODE44 TRACE ---
def _node44_trace(runtime):
    try:
        state = runtime.get("state", {})
        print("[NODE44 TRACE]", state.get("coherence_mode"), state.get("dominant_attractor"))
    except:
        pass

