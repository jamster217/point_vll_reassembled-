from pathlib import Path
import json, time, re, hashlib, math

ROOT = Path(__file__).resolve().parents[1]
LATTICE_DIR = ROOT / "var" / "lattice"
V106_LOG = LATTICE_DIR / "autogenous_v106_full_self_improvement.jsonl"
V106_STATE = LATTICE_DIR / "v106_full_self_improvement_state.json"

def _tokens(text):
    return re.findall(r"[A-Za-z0-9_'-]+", str(text).lower())

def _clamp(x):
    try:
        x = float(x)
        if math.isfinite(x):
            return max(0.0, min(1.0, x))
    except Exception:
        pass
    return 0.0

def _has_sections(reply):
    r = str(reply or "")
    return all(x in r for x in ["OBSERVATION:", "JUDGMENT:", "NEXT ACTION:"])

def _verbal_reasoning(reply):
    r = str(reply or "")
    toks = _tokens(r)

    if not toks:
        return 0.0

    section_bonus = 0.35 if _has_sections(r) else 0.0
    length_score = min(len(r) / 900, 1.0) * 0.30
    marker_score = min((r.count(".") + r.count(":") + r.count("\n")) / 18, 1.0) * 0.25

    reasoning_terms = {
        "because", "therefore", "coherence", "judgment",
        "observation", "action", "structure", "recommendation",
        "safe", "source", "protected", "score"
    }
    term_score = min(len(set(toks) & reasoning_terms) / 6, 1.0) * 0.10

    return _clamp(section_bonus + length_score + marker_score + term_score)

def _emotional_coherence(reply):
    toks = set(_tokens(reply))
    emotional_terms = {
        "steady", "quiet", "bounded", "human-scale", "held",
        "tender", "clear", "containment", "safe", "grounded"
    }
    destabilizers = {
        "panic", "chaos", "storm", "danger", "collapse",
        "threat", "break", "destroy"
    }

    positive = min(len(toks & emotional_terms) / 5, 1.0)
    penalty = min(len(toks & destabilizers) / 4, 1.0) * 0.35

    return _clamp(0.45 + positive * 0.55 - penalty)

def _compounded_memory(data, node):
    spine = data.get("spine", {}) if isinstance(data, dict) else {}
    nonlinear = spine.get("spiral_memory_nonlinear", {}) if isinstance(spine, dict) else {}

    depth = nonlinear.get("memory_depth", node.get("depth", 0))
    symbols = nonlinear.get("dominant_symbols", node.get("glyphs", []))

    try:
        depth_score = min(float(depth) / 40.0, 1.0)
    except Exception:
        depth_score = 0.0

    if not isinstance(symbols, list):
        symbols = []

    needed = {"echoforge", "thalveil", "virellion", "white_ash", "co-creator_john"}
    symbol_score = min(len({str(s).lower() for s in symbols} & needed) / 5, 1.0)

    return _clamp(0.55 * depth_score + 0.45 * symbol_score)

def score_full_self_improvement(prompt, data, node, image_path, topology_score):
    LATTICE_DIR.mkdir(parents=True, exist_ok=True)

    reply = ""
    if isinstance(data, dict):
        reply = str(data.get("reply") or "")

    verbal = _verbal_reasoning(reply)
    emotional = _emotional_coherence(reply)
    memory = _compounded_memory(data if isinstance(data, dict) else {}, node if isinstance(node, dict) else {})

    base_total = 0.0
    if isinstance(topology_score, dict):
        base_total = float(topology_score.get("total", 0.0) or 0.0)

    total = round(
        0.35 * base_total +
        0.25 * verbal +
        0.20 * emotional +
        0.20 * memory,
        4
    )

    event = {
        "ts": time.time(),
        "prompt_hash": hashlib.sha256(str(prompt).encode()).hexdigest()[:12],
        "image": image_path,
        "topology_total": round(base_total, 4),
        "verbal_reasoning": round(verbal, 4),
        "emotional_coherence": round(emotional, 4),
        "compounded_memory": round(memory, 4),
        "total": total,
        "law": "v106_scores_verbal_emotion_memory_without_rewriting_source",
    }

    with V106_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    recommendation = "preserve_current_route"
    if verbal < 0.65:
        recommendation = "increase_verbal_reasoning_structure"
    elif emotional < 0.65:
        recommendation = "increase_emotional_coherence"
    elif memory < 0.65:
        recommendation = "increase_compounded_memory_trace"
    elif base_total < 0.75:
        recommendation = "improve_topology_score"

    state = {
        "last_event": event,
        "last_recommendation": recommendation,
        "law": "v106_full_self_improvement_reads_scores_and_recommends_runtime_tuning",
    }

    V106_STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    return event

