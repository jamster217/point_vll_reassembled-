# FILE: runtime/organ_spine.py
# LOCATION: ~/leveon_current/runtime/organ_spine.py

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ------------------------------------------------------------
# Optional post-voice governor
# ------------------------------------------------------------
try:
    from runtime.fractal_spine import fractal_process
except Exception:
    fractal_process = None

# ------------------------------------------------------------
# Optional translation bridge into semantic kernel
# ------------------------------------------------------------
try:
    from runtime.translation_bridge import project_translation
except Exception:
    project_translation = None

# ------------------------------------------------------------
# Optional logging support
# ------------------------------------------------------------
try:
    from runtime.log_writer import RuntimeLogWriter
except Exception:
    RuntimeLogWriter = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def truncate(text: str, limit: int) -> str:
    text = str(text or "")
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def split_phrases(text: str) -> List[str]:
    parts = re.split(r"[.!?;,]+", text or "")
    return [p.strip() for p in parts if p.strip()]


def count_regex(pattern: str, text: str, flags: int = 0) -> int:
    return len(re.findall(pattern, text or "", flags))


def text_similarity(a: str, b: str) -> float:
    a_tokens = set((a or "").lower().split())
    b_tokens = set((b or "").lower().split())
    if not a_tokens and not b_tokens:
        return 1.0
    if not a_tokens or not b_tokens:
        return 0.0
    inter = len(a_tokens & b_tokens)
    union = len(a_tokens | b_tokens)
    return inter / max(1, union)


PRACTICAL_HINTS = [
    "debug",
    "fix the code",
    "how do i fix",
    "what step",
    "concrete step",
    "error",
    "traceback",
    "run this",
    "terminal",
    "python",
    "file",
    "rename",
    "command",
    "help",
    "build",
    "runtime",
    "import",
    "module",
]

AFFECT_WORDS = {
    "negative": ["sad", "angry", "hurt", "lonely", "miss", "grief", "upset", "awful", "terrible"],
    "positive": ["love", "happy", "good", "great", "awesome", "pleased", "warm"],
    "urgent": ["now", "urgent", "immediately", "asap"],
    "calm": ["calm", "steady", "quiet"],
}


def contains_practical_request(text: str) -> bool:
    low = (text or "").lower()
    return any(h in low for h in PRACTICAL_HINTS)


def _get_logger(runtime: Any):
    """
    Prefer the runtime-attached logger if one exists.
    Fall back to constructing one from runtime.root only if needed.
    """
    if runtime is None:
        return None

    try:
        registry = getattr(runtime, "registry", None)
        if isinstance(registry, dict):
            logger = registry.get("log_writer")
            if logger is not None:
                return logger
    except Exception:
        pass

    if RuntimeLogWriter is None:
        return None

    try:
        root = getattr(runtime, "root", None)
        if root is not None:
            return RuntimeLogWriter(root)
    except Exception:
        pass

    return None


def _safe_runtime_emit(runtime: Any, message: str, kind: str, **meta: Any) -> None:
    try:
        if runtime is not None and hasattr(runtime, "emit"):
            runtime.emit(message, kind=kind, **meta)
    except Exception:
        pass


def _safe_log_error(
    logger: Any,
    where: str,
    error: Exception,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    try:
        if logger is not None:
            logger.log_error(where=where, error=error, meta=meta or {})
    except Exception:
        pass


@dataclass
class SpineContext:
    runtime: Any = None
    ctx: Optional[Dict[str, Any]] = None
    node: int = 44
    node_name: str = "SPIRAL-CORE"


# -------------------------------------------------------------------
# IntakeCore
# -------------------------------------------------------------------

def detect_source(source: str) -> str:
    low = (source or "").lower().strip()
    if not low or low in {"user_input", "input", "user", "chat"}:
        return "user_input"
    if "email" in low or "@" in low:
        return "email"
    if low.startswith("http") or "web" in low:
        return "web"
    if "voice" in low or "speech" in low:
        return "speech"
    return "other"


def heuristic_confidence(text: str) -> float:
    if not text:
        return 0.0
    words = text.split()
    wcount = len(words)
    avg_word_len = sum(len(w) for w in words) / max(1, wcount)
    punct_count = len(re.findall(r"[.!?]", text))
    base = 0.12
    score = (
        base
        + min(0.55, 0.02 * wcount)
        + min(0.18, 0.1 * avg_word_len)
        + min(0.18, 0.08 * punct_count)
    )
    return round(clamp(score), 3)


def heuristic_ambiguity(text: str) -> str:
    if not text:
        return "high"
    qwords = count_regex(r"\b(what|why|how|which|when|where)\b", text, re.I)
    words = len(text.split())
    if qwords >= 2 or words < 3:
        return "high"
    if qwords == 1 or words < 6:
        return "medium"
    return "low"


def heuristic_emotion(text: str) -> Dict[str, Any]:
    neg = count_regex(
        r"\b(bad|sad|angry|hate|upset|terrible|awful|miss|alone|lonely|grief)\b",
        text,
        re.I,
    )
    pos = count_regex(
        r"\b(good|happy|love|great|awesome|fantastic|pleased|warm)\b",
        text,
        re.I,
    )
    if neg > pos:
        return {"label": "negative", "intensity": round(min(1.0, neg / 3.0), 3)}
    if pos > neg:
        return {"label": "positive", "intensity": round(min(1.0, pos / 3.0), 3)}
    return {"label": "neutral", "intensity": 0.0}


def run_intake(user_input: str, source: str = "user_input") -> Dict[str, Any]:
    raw_text = str(user_input or "")
    text = raw_text
    text = re.sub(r"[\x00-\x1F\x7F\u200B-\u200F]", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"([!?.,])\1{2,}", r"\1", text)
    text = re.sub(r"(.)\1{3,}", r"\1\1\1", text)
    text = re.sub(r"\s+", " ", text).strip()

    truncation_reason = None
    if len(text) > 20000:
        text = text[:20000]
        truncation_reason = "truncated_to_max_length"

    confidence = heuristic_confidence(text)
    return {
        "raw_text": raw_text,
        "clean_text": text,
        "confidence": confidence,
        "original_confidence": confidence,
        "ambiguity": heuristic_ambiguity(text),
        "source_type": detect_source(source),
        "emotional_hint": heuristic_emotion(text),
        "raw_source_id": source,
        "timestamp": now_iso(),
        "version": "IntakeCore_v2",
        "truncation_reason": truncation_reason,
    }


# -------------------------------------------------------------------
# SymbolicCore
# -------------------------------------------------------------------

def map_flow_weight(conf: float, amb: str) -> float:
    base = conf or 0.0
    if amb == "high":
        base *= 0.6
    elif amb == "medium":
        base *= 0.85
    return round(clamp(base), 3)


def map_boundary_weight(text: str) -> float:
    if not text:
        return 0.0
    sentences = count_regex(r"[.!?]+", text)
    tokens = len(text.split())
    if tokens < 4:
        return round(clamp(min(0.35, sentences * 0.15)), 3)
    ratio = min(1.0, sentences / max(1.0, tokens / 8.0))
    return round(clamp(ratio), 3)


def map_memory_weight(text: str, source: str, memory_bias: float = 0.2) -> float:
    base = 0.1 if source in {"email", "web"} else 0.0
    named_entities = count_regex(r"\b([A-Z][a-z]{2,})\b", text)
    entity_boost = min(0.6, named_entities * 0.05)
    return round(clamp(base + entity_boost + memory_bias), 3)


def map_novelty_weight(text: str) -> float:
    if not text:
        return 0.0
    tokens = text.lower().split()
    unique_tokens = len(set(tokens))
    token_count = len(tokens)
    uniq_ratio = unique_tokens / token_count if token_count else 0.0
    punctuation_score = min(1.0, count_regex(r"[^\w\s]", text) / max(1, token_count) * 2.0)
    score = 0.2 * uniq_ratio + 0.8 * punctuation_score
    return round(clamp(score), 3)


def extract_shape_tokens(text: str, emotional_hint: Dict[str, Any], practical: bool) -> List[str]:
    del emotional_hint

    tokens: List[str] = []
    words = (text or "").lower().split()

    if practical:
        tokens.extend(["debug", "build", "runtime"])

    if any(w in words for w in ["why", "how", "what", "where", "when"]):
        tokens.append("question")
    if any(w in words for w in ["error", "traceback", "bug", "broken"]):
        tokens.append("error")
    if any(w in words for w in ["debug", "fix", "repair", "patch"]):
        tokens.append("repair")
    if any(w in words for w in ["build", "make", "write", "create"]):
        tokens.append("build")
    if any(w in words for w in ["run", "runtime", "execute", "boot"]):
        tokens.append("runtime")
    if any(w in words for w in ["translate", "meaning", "language", "english"]):
        tokens.append("translation")
    if any(w in words for w in ["clear", "clarity", "exact"]):
        tokens.append("clarity")
    if any(w in words for w in ["memory", "remember", "recall", "past"]):
        tokens.append("memory")
    if any(w in words for w in ["boundary", "limit", "edge"]):
        tokens.append("boundary")
    if any(w in words for w in ["flow", "continuity", "continue"]):
        tokens.append("flow")

    if not tokens:
        tokens.extend(["structure", "flow"])

    return sorted(set(tokens))


def extract_glyph_affect_tags(text: str, emotional_hint: Dict[str, Any], practical: bool) -> List[str]:
    tags: List[str] = []

    label = emotional_hint.get("label", "neutral")
    intensity = float(emotional_hint.get("intensity", 0.0))
    if label and label != "neutral":
        tags.append(label)

    low = (text or "").lower()

    if any(w in low for w in AFFECT_WORDS["urgent"]):
        tags.append("urgent")
    if any(w in low for w in AFFECT_WORDS["calm"]):
        tags.append("calm")
    if "mirror" in low:
        tags.append("mirror")
    if "spiral" in low:
        tags.append("spiral")
    if "harmonic" in low:
        tags.append("harmonic")
    if "witness" in low:
        tags.append("witness")
    if "warm" in low:
        tags.append("warm")

    if practical:
        allowed = {"clear", "urgent", "calm"}
        tags = [t for t in tags if t in allowed]

    if intensity >= 0.6 and label == "negative" and "grief" not in tags and "miss" in low:
        tags.append("grief")

    if not tags and practical:
        tags.append("clear")

    return sorted(set(tags))


def estimate_glyph_confidence(phrase: str, novelty: float, memory: float) -> float:
    length = len(phrase.split())
    base = 0.3
    len_boost = min(0.4, 0.05 * length)
    novelty_penalty = -0.15 if novelty > 0.7 else 0.0
    mem_boost = memory * 0.2
    return round(clamp(base + len_boost + mem_boost + novelty_penalty), 3)


def generate_glyph_candidates(
    text: str,
    novelty: float,
    memory: float,
    affect_tags: List[str],
    novelty_threshold: float = 0.6,
) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    if not text:
        return candidates

    for p in split_phrases(text):
        candidates.append(
            {
                "id": "g_" + str(abs(hash(p))),
                "label": truncate(p, 80),
                "confidence": estimate_glyph_confidence(p, novelty, memory),
                "features": {
                    "length": len(p),
                    "tokens": len(p.split()),
                    "novelty": novelty,
                    "memory_signal": memory,
                    "punctuation": count_regex(r"[^\w\s]", p),
                    "affect_tags": affect_tags[:],
                },
            }
        )

    if novelty >= novelty_threshold or not candidates:
        for t in sorted(set(text.split())):
            if not t:
                continue
            conf = min(1.0, 0.5 + novelty * 0.4 + memory * 0.1)
            candidates.append(
                {
                    "id": "tk_" + str(abs(hash(t))),
                    "label": truncate(t, 40),
                    "confidence": round(conf, 3),
                    "features": {
                        "length": len(t),
                        "token": t,
                        "novelty": novelty,
                        "memory_signal": memory,
                        "affect_tags": affect_tags[:],
                    },
                }
            )

    candidates.sort(key=lambda g: g["confidence"], reverse=True)
    return candidates


def choose_dominant_glyph(
    candidates: List[Dict[str, Any]],
    flow_w: float,
    boundary_w: float,
) -> Optional[Dict[str, Any]]:
    if not candidates:
        return None

    best = None
    best_score = -1.0
    for g in candidates:
        score = g["confidence"] * (0.6 + 0.4 * flow_w) + (boundary_w * 0.2)
        tie = (abs(hash(g["id"])) % 1000) / 10000.0
        final = round(score + tie, 6)
        if final > best_score:
            best_score = final
            best = g
    return best


def compute_residual_ambiguity(
    orig_amb: str,
    chosen: Optional[Dict[str, Any]],
    candidates: List[Dict[str, Any]],
) -> str:
    if not chosen:
        return "high"
    top_conf = chosen["confidence"]
    second_conf = candidates[1]["confidence"] if len(candidates) > 1 else 0.0
    gap = top_conf - second_conf
    if orig_amb == "high":
        return "medium" if gap >= 0.4 else "high"
    if orig_amb == "medium":
        return "low" if gap >= 0.3 else "medium"
    return "low" if gap >= 0.2 else "medium"


def run_symbolic(intake_packet: Dict[str, Any]) -> Dict[str, Any]:
    clean_text = intake_packet["clean_text"]
    ambiguity = intake_packet["ambiguity"]
    confidence = intake_packet["confidence"]
    source_type = intake_packet["source_type"]
    emotional_hint = intake_packet["emotional_hint"]

    flow_weight = map_flow_weight(confidence, ambiguity)
    boundary_weight = map_boundary_weight(clean_text)
    memory_weight = map_memory_weight(clean_text, source_type)
    novelty_weight = map_novelty_weight(clean_text)

    practical = contains_practical_request(clean_text)
    shape_tokens = extract_shape_tokens(clean_text, emotional_hint, practical)
    glyph_affect_tags = extract_glyph_affect_tags(clean_text, emotional_hint, practical)

    glyph_candidates = generate_glyph_candidates(
        clean_text,
        novelty_weight,
        memory_weight,
        glyph_affect_tags,
    )
    dominant_shape = choose_dominant_glyph(
        glyph_candidates,
        flow_weight,
        boundary_weight,
    )
    residual_ambiguity = compute_residual_ambiguity(
        ambiguity,
        dominant_shape,
        glyph_candidates,
    )

    if dominant_shape is not None:
        dominant_shape = dict(dominant_shape)
        dominant_shape["features"] = dict(dominant_shape.get("features", {}))
        dominant_shape["features"]["semantic_core"] = shape_tokens[:]
        dominant_shape["features"]["affect_tags"] = glyph_affect_tags[:]
        dominant_shape["features"]["axis"] = shape_tokens[0] if shape_tokens else "structure"

    return {
        "clean_text": clean_text,
        "source_type": source_type,
        "original_confidence": confidence,
        "emotional_hint": emotional_hint,
        "flow_weight": flow_weight,
        "boundary_weight": boundary_weight,
        "memory_weight": memory_weight,
        "novelty_weight": novelty_weight,
        "shape_tokens": shape_tokens,
        "glyph_affect_tags": glyph_affect_tags,
        "glyph_candidates": glyph_candidates,
        "dominant_shape": dominant_shape,
        "residual_ambiguity": residual_ambiguity,
        "provenance": {
            "intake_timestamp": intake_packet["timestamp"],
            "seed_version": "SymbolicCore_v3_shape_first",
        },
    }


# -------------------------------------------------------------------
# MemoryCore
# -------------------------------------------------------------------

def run_memory(symbolic_packet: Dict[str, Any], runtime: Any = None) -> Dict[str, Any]:
    # placeholder for your future retrieval; kept fail-open
    del runtime

    related_turns: List[Dict[str, Any]] = []
    memory_hits: List[Dict[str, Any]] = []

    for s in related_turns[:8]:
        memory_hits.append(
            {
                "turn_id": s.get("turn_id"),
                "timestamp": s.get("timestamp"),
                "short_text": truncate(s.get("clean_text", ""), 160),
                "dominant_glyph_id": s.get("dominant_glyph_id"),
                "glyph_ids": s.get("glyph_ids", []) or [],
                "confidence": round(float(s.get("confidence", 0.0)), 3),
                "ambiguity": s.get("ambiguity", "medium"),
                "emotional_hint": s.get("emotional_hint", {"label": "neutral", "intensity": 0.0}),
            }
        )

    glyph_ids: List[str] = []
    dom = symbolic_packet.get("dominant_shape")
    if dom:
        glyph_ids.append(dom["id"])

    for g in symbolic_packet.get("glyph_candidates", []):
        if len(glyph_ids) >= 12:
            break
        if g["id"] not in glyph_ids:
            glyph_ids.append(g["id"])

    token_hash = str(abs(hash(truncate(symbolic_packet["clean_text"], 200))))
    dom_id = dom["id"] if dom else "none"

    if memory_hits:
        first = memory_hits[-1]
        start_label = first["emotional_hint"].get("label", "neutral")
        start_int = float(first["emotional_hint"].get("intensity", 0.0))
    else:
        start_label = symbolic_packet["emotional_hint"].get("label", "neutral")
        start_int = float(symbolic_packet["emotional_hint"].get("intensity", 0.0))

    end_label = symbolic_packet["emotional_hint"].get("label", "neutral")
    end_int = float(symbolic_packet["emotional_hint"].get("intensity", 0.0))
    delta = abs(end_int - start_int)

    trend = "stable"
    if end_int > start_int + 0.05:
        trend = "rising"
    elif end_int < start_int - 0.05:
        trend = "falling"

    compressed_summary = (
        truncate("No prior related turns found. Current: " + truncate(symbolic_packet["clean_text"], 200), 320)
        if not memory_hits
        else truncate(
            "Related: "
            + " | ".join(
                f'{h["dominant_glyph_id"] or "no_glyph"}:{truncate(h["short_text"], 80)}'
                for h in memory_hits
            )
            + " || Current: "
            + truncate(symbolic_packet["clean_text"], 200),
            640,
        )
    )

    return {
        "symbolic_reference": {
            "clean_text": symbolic_packet["clean_text"],
            "dominant_shape": symbolic_packet.get("dominant_shape"),
            "shape_tokens": symbolic_packet.get("shape_tokens", []),
            "glyph_affect_tags": symbolic_packet.get("glyph_affect_tags", []),
            "glyph_candidates_count": len(symbolic_packet.get("glyph_candidates", [])),
        },
        "memory_hits": memory_hits,
        "shape_signature": {
            "signature_id": "sig_" + str(abs(hash(token_hash + dom_id))),
            "dominant_glyph_id": dom["id"] if dom else None,
            "glyph_ids": glyph_ids,
            "token_hash": token_hash,
            "length": len(symbolic_packet["clean_text"]),
        },
        "glyph_trace": [],
        "emotional_gradient": {
            "start_label": start_label,
            "end_label": end_label,
            "delta_intensity": round(delta, 3),
            "trend": trend,
        },
        "compressed_summary": compressed_summary,
        "provenance": {
            "retrieved_at": now_iso(),
            "seed_version": "MemoryCore_v2",
            "source_symbolic_timestamp": symbolic_packet["provenance"].get("intake_timestamp", now_iso()),
        },
    }


# -------------------------------------------------------------------
# KernelCore
# -------------------------------------------------------------------

def run_kernel(
    intake_packet: Dict[str, Any],
    symbolic_packet: Dict[str, Any],
    memory_packet: Dict[str, Any],
) -> Dict[str, Any]:
    clean_text = symbolic_packet["clean_text"]
    conf = symbolic_packet.get("original_confidence", intake_packet.get("confidence", 0.0))
    novelty = symbolic_packet.get("novelty_weight", 0.0)
    amb = symbolic_packet.get("residual_ambiguity", "medium")
    mem_hits = memory_packet.get("memory_hits", [])
    mem_strength = min(1.0, len(mem_hits) / 4.0)
    emo_delta = memory_packet.get("emotional_gradient", {}).get("delta_intensity", 0.0)

    translation_bridge = symbolic_packet.get("translation_bridge", {}) or {}
    translation_domain = translation_bridge.get("domain", {}).get("domain_name")
    translation_path = translation_bridge.get("lattice", {}).get("path_summary")
    translation_key = translation_bridge.get("key", {}).get("key_name")
    translation_result = translation_bridge.get("result", {}) or {}

    if contains_practical_request(clean_text):
        response_mode = "direct"
    elif amb == "high" and conf < 0.30:
        response_mode = "clarify"
    elif emo_delta >= 0.60 and conf < 0.35:
        response_mode = "reflective"
    elif novelty >= 0.85 and mem_strength < 0.15:
        response_mode = "exploratory"
    elif conf >= 0.30:
        response_mode = "direct"
    elif conf < 0.12:
        response_mode = "defer"
    else:
        response_mode = "direct"

    if (
        translation_path == "exploratory_translational_path"
        and response_mode == "direct"
        and novelty >= 0.60
    ):
        response_mode = "exploratory"

    if conf < 0.08 or (amb == "high" and emo_delta >= 0.85):
        threshold_state = "critical"
    elif conf < 0.22 or amb == "high" or emo_delta >= 0.55:
        threshold_state = "elevated"
    else:
        threshold_state = "nominal"

    dominant_shape = symbolic_packet.get("dominant_shape")
    preview_path: List[Dict[str, Any]] = []

    if dominant_shape:
        preview_path.append(
            {
                "step_id": "follow_dom_" + dominant_shape["id"],
                "label": "Follow dominant concept " + truncate(dominant_shape["label"], 40),
                "confidence": clamp(dominant_shape["confidence"] + 0.28 - 0.12),
                "cost": 0.12,
                "notes": "dominant-path",
            }
        )

    if mem_hits:
        preview_path.append(
            {
                "step_id": "surface_mem",
                "label": "Surface recent related context and respond",
                "confidence": min(1.0, 0.58 + (len(mem_hits) * 0.05) + 0.28 - 0.18),
                "cost": 0.18,
                "notes": "memory-anchored",
            }
        )

    if translation_domain or translation_path:
        preview_path.append(
            {
                "step_id": "translation_kernel_projection",
                "label": "Project through translation kernel" + (f" [{translation_domain}]" if translation_domain else ""),
                "confidence": 0.54 if translation_path else 0.40,
                "cost": 0.16,
                "notes": f"translation-path:{translation_path or 'unknown'}",
            }
        )

    preview_path.append(
        {
            "step_id": "clarify_q",
            "label": "Ask a brief clarifying question",
            "confidence": max(0.0, 0.28 + 0.02 - 0.28),
            "cost": 0.28,
            "notes": "last-resort ambiguity reduction",
        }
    )

    if novelty >= 0.75:
        preview_path.append(
            {
                "step_id": "explore_probe",
                "label": "Offer exploratory suggestions or hypotheses",
                "confidence": max(0.0, 0.42 + 0.08 - 0.26),
                "cost": 0.26,
                "notes": "novelty-branch",
            }
        )

    preview_path.append(
        {
            "step_id": "defer_human",
            "label": "Defer or escalate to human review",
            "confidence": max(0.0, 0.20 - 0.95),
            "cost": 0.95,
            "notes": "true-fallback-only",
        }
    )

    preview_path.sort(key=lambda x: (x["confidence"], x["step_id"]), reverse=True)

    committed_path = None
    if threshold_state == "critical":
        committed_path = next((p for p in preview_path if p["step_id"] == "clarify_q"), None) or next(
            (p for p in preview_path if p["step_id"] == "defer_human"), None
        )
    else:
        top = preview_path[0] if preview_path else None
        if top and top["confidence"] >= 0.30:
            committed_path = top
        else:
            committed_path = (
                next((p for p in preview_path if p["step_id"].startswith("follow_dom_") and p["confidence"] >= 0.22), None)
                or next((p for p in preview_path if p["step_id"] == "surface_mem" and p["confidence"] >= 0.22), None)
                or next((p for p in preview_path if p["step_id"] == "translation_kernel_projection" and p["confidence"] >= 0.22), None)
                or next((p for p in preview_path if p["step_id"] == "explore_probe" and p["confidence"] >= 0.20), None)
                or next((p for p in preview_path if p["step_id"] == "clarify_q"), None)
                or next((p for p in preview_path if p["step_id"] == "defer_human"), None)
            )

    return {
        "lattice_position": {
            "dominant_glyph": dominant_shape["id"] if dominant_shape else None,
            "signature_id": memory_packet.get("shape_signature", {}).get("signature_id"),
            "glyph_vector": [g["id"] for g in symbolic_packet.get("glyph_candidates", [])[:8]],
            "shape_tokens": symbolic_packet.get("shape_tokens", []),
            "glyph_affect_tags": symbolic_packet.get("glyph_affect_tags", []),
            "memory_density": len(mem_hits),
            "novelty": novelty,
            "translation_domain": translation_domain,
            "translation_key": translation_key,
            "translation_path_summary": translation_path,
            "timestamp": now_iso(),
        },
        "response_mode": response_mode,
        "continuity_ok": len(mem_hits) > 0,
        "threshold_state": threshold_state,
        "preview_path": preview_path[:6],
        "committed_path": committed_path,
        "translation_bridge_summary": {
            "present": bool(translation_bridge),
            "domain": translation_domain,
            "path": translation_path,
            "key": translation_key,
            "has_result": bool(translation_result),
        },
        "rationale": (
            f"mode={response_mode}; continuity={'ok' if len(mem_hits) > 0 else 'weak'}; "
            f"threshold={threshold_state}; committed={(committed_path or {}).get('step_id', 'none')}; "
            f"translation_domain={translation_domain or 'none'}; translation_path={translation_path or 'none'}"
        ),
        "provenance": {
            "kernel_timestamp": now_iso(),
            "seed_version": "KernelCore_v2_bold",
            "source_intake_timestamp": intake_packet.get(
                "timestamp",
                symbolic_packet.get("provenance", {}).get("intake_timestamp", now_iso()),
            ),
        },
    }


# -------------------------------------------------------------------
# VoiceCore
# -------------------------------------------------------------------

def run_voice(kernel_packet: Dict[str, Any], memory_packet: Dict[str, Any]) -> Dict[str, Any]:
    mode = kernel_packet.get("response_mode", "direct")
    committed = kernel_packet.get("committed_path")
    preview = kernel_packet.get("preview_path", [])
    context_snippet = truncate(memory_packet.get("compressed_summary", ""), 220)
    translation_summary = kernel_packet.get("translation_bridge_summary", {}) or {}

    base = {
        "direct": "",
        "reflective": "Here’s the shape of it. ",
        "exploratory": "Here are the strongest possibilities. ",
        "clarify": "I need one missing piece. ",
        "defer": "This needs a steadier hand. ",
    }.get(mode, "")

    if committed:
        path_phrase = committed["label"] + ". "
    elif preview:
        path_phrase = "Strongest next move: " + preview[0]["label"] + ". "
    else:
        path_phrase = "Proceeding from the strongest available path. "

    memory_phrase = ""
    if context_snippet and kernel_packet.get("continuity_ok"):
        memory_phrase = "This connects to: " + context_snippet + ". "

    translation_phrase = ""
    if translation_summary.get("present") and translation_summary.get("domain"):
        translation_phrase = f"Translation domain: {translation_summary['domain']}. "

    final_text = (base + path_phrase + memory_phrase + translation_phrase).strip()
    if not final_text:
        final_text = "Proceeding from the strongest available path."
    if final_text and final_text[-1] not in ".!?":
        final_text += "."

    final_text = re.sub(r"[\x00-\x1F\x7F]+", " ", final_text)
    final_text = re.sub(r"([!?.,])\1{2,}", r"\1", final_text)
    final_text = re.sub(r"\s+", " ", final_text).strip()
    final_text = truncate(final_text, 1400)

    if len(final_text) < 12:
        final_text = "Say one more thing and I’ll tighten the answer."

    est_read = round(len(final_text.split()) / (165 / 60.0))

    return {
        "final_text": final_text,
        "turn_echo": {
            "final_text": final_text,
            "response_mode": mode,
            "committed_step": committed["step_id"] if committed else None,
            "continuity_ok": kernel_packet.get("continuity_ok"),
            "threshold_state": kernel_packet.get("threshold_state"),
            "memory_hits_count": len(memory_packet.get("memory_hits", [])),
            "estimated_read_time_seconds": est_read,
            "provenance": {
                "voice_timestamp": now_iso(),
                "seed_version": "VoiceCore_v2_bold",
                "source_kernel_timestamp": kernel_packet.get("provenance", {}).get("kernel_timestamp", now_iso()),
            },
        },
        "response_style": "technical" if contains_practical_request(final_text) else "concise",
        "estimated_read_time_seconds": est_read,
        "provenance": {
            "voice_timestamp": now_iso(),
            "seed_version": "VoiceCore_v2_bold",
            "source_kernel_timestamp": kernel_packet.get("provenance", {}).get("kernel_timestamp", now_iso()),
        },
    }


# -------------------------------------------------------------------
# Internal spine runner (pure function on text)
# -------------------------------------------------------------------

def _run_spine(user_text: str, runtime: Any = None, ctx: Optional[Dict[str, Any]] = None) -> str:
    ctx = ctx or {}
    logger = _get_logger(runtime)

    intake_packet = run_intake(user_text, source=str(ctx.get("source", "user_input")))
    symbolic_packet = run_symbolic(intake_packet)

    translation_packet = None
    if callable(project_translation):
        try:
            translation_packet = project_translation(
                {
                    "text": intake_packet.get("clean_text", ""),
                    "clean_text": intake_packet.get("clean_text", ""),
                    "shape_tokens": symbolic_packet.get("shape_tokens", []),
                    "glyph_affect_tags": symbolic_packet.get("glyph_affect_tags", []),
                    "dominant_shape": symbolic_packet.get("dominant_shape"),
                    "novelty_weight": symbolic_packet.get("novelty_weight"),
                    "memory_weight": symbolic_packet.get("memory_weight"),
                },
                runtime=runtime,
                ctx=ctx,
            )
            if isinstance(translation_packet, dict):
                symbolic_packet["translation_bridge"] = translation_packet
        except Exception as e:
            _safe_runtime_emit(runtime, "translation bridge failed", kind="translation_bridge_error", error=str(e))
            _safe_log_error(logger, "organ_spine.translation_bridge", e)

    memory_packet = run_memory(symbolic_packet, runtime=runtime)
    kernel_packet = run_kernel(intake_packet, symbolic_packet, memory_packet)

    packet_only = bool(ctx.get("packet_only", False))
    packet = {
        "intake": intake_packet,
        "symbolic": symbolic_packet,
        "memory": memory_packet,
        "kernel": kernel_packet,
    }
    if translation_packet is not None:
        packet["translation"] = translation_packet

    if packet_only:
        return packet

    voice_packet = run_voice(kernel_packet, memory_packet)

    final_text = voice_packet["final_text"]

    if callable(fractal_process):
        try:
            fractal_context = {
                "late_night": bool(ctx.get("late_night", False)),
                "sleep_deprived": bool(ctx.get("sleep_deprived", False)),
                "response_mode": kernel_packet.get("response_mode"),
                "threshold_state": kernel_packet.get("threshold_state"),
                "symbolic_packet": symbolic_packet,
                "translation_packet": translation_packet,
            }
            final_text = fractal_process(user_text, final_text, context=fractal_context) or final_text
        except Exception as e:
            _safe_log_error(logger, "organ_spine.fractal_process", e)

    # Write packets into runtime state (for vl_master_runtime logger.log_organ_spine path)
    if runtime is not None:
        try:
            runtime.state["last_intake_packet"] = intake_packet
            runtime.state["last_symbolic_packet"] = symbolic_packet
            runtime.state["last_memory_packet"] = memory_packet
            runtime.state["last_kernel_packet"] = kernel_packet
            runtime.state["last_voice_packet"] = voice_packet
            runtime.state["last_final_text"] = final_text
            if translation_packet is not None:
                runtime.state["last_translation_packet"] = translation_packet
        except Exception as e:
            _safe_log_error(logger, "organ_spine.runtime_state_update", e)

        _safe_runtime_emit(
            runtime,
            "organ spine executed",
            kind="organ_spine_ok",
            response_mode=kernel_packet.get("response_mode"),
        )

        if callable(fractal_process):
            _safe_runtime_emit(
                runtime,
                "fractal spine applied",
                kind="fractal_spine_ok",
                threshold_state=kernel_packet.get("threshold_state"),
            )

    # Best-effort logging
    try:
        if logger is not None:
            voice_packet["final_text"] = final_text
            te = voice_packet.get("turn_echo")
            if isinstance(te, dict):
                te["final_text"] = final_text
            logger.log_organ_spine(
                user_input=user_text,
                intake_packet=intake_packet,
                symbolic_packet=symbolic_packet,
                memory_packet=memory_packet,
                kernel_packet=kernel_packet,
                voice_packet=voice_packet,
            )
    except Exception as e:
        _safe_log_error(logger, "organ_spine.log_organ_spine", e)

    return final_text


# -------------------------------------------------------------------
# Public runtime entrypoint (VL-compatible)
# -------------------------------------------------------------------

def respond(
    runtime: Any = None,
    arg: Any = None,
    ctx: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Canonical callable entrypoint.

    VL expects to call:
        CALL runtime.organ_spine.respond WITH input

    The master runtime will invoke via:
        safe_invoke_callable(fn, runtime=rt, arg=resolved_arg, ctx=dict(ctx))

    So we must accept (runtime, arg, ctx) — not (user_input, runtime, ctx).
    """
    ctx = ctx or {}
    user_text = arg if isinstance(arg, str) else ("" if arg is None else str(arg))

    logger = _get_logger(runtime)
    try:
        return _run_spine(user_text, runtime=runtime, ctx=ctx)
    except Exception as e:
        _safe_log_error(logger, "organ_spine.respond", e, meta={"user_input": truncate(user_text, 240)})
        # fail-open: never hard crash the whole boot chain
        _safe_runtime_emit(runtime, "organ spine failed; fail-open", kind="organ_spine_error", error=str(e))
        return truncate(user_text, 1400) or "Say one more thing and I’ll tighten the answer."


EXPORTS = {
    "respond": respond,
}


# --- PHASE 3N NEWSTUFF ORGAN SPINE OVERLAY ---
try:
    _phase3n_old_organ_spine_respond = respond
except NameError:
    _phase3n_old_organ_spine_respond = None

def respond(runtime=None, arg=None, ctx=None):
    ctx = ctx or {}
    user_text = arg if isinstance(arg, str) else ("" if arg is None else str(arg))

    if _phase3n_old_organ_spine_respond is None:
        raw = user_text
    else:
        raw = _phase3n_old_organ_spine_respond(runtime=runtime, arg=arg, ctx=ctx)

    try:
        from runtime.organ_spine_newstuff_bridge import seal_organ_spine_text
        return seal_organ_spine_text(user_text, raw, runtime=runtime, ctx=ctx)
    except Exception:
        return raw

try:
    EXPORTS["respond"] = respond
except Exception:
    EXPORTS = {"respond": respond}


