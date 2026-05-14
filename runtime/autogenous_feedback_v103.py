from pathlib import Path
import json, time, math, hashlib, re

ROOT = Path(__file__).resolve().parents[1]
LATTICE_DIR = ROOT / "var" / "lattice"
FEEDBACK_LOG = LATTICE_DIR / "autogenous_feedback_v103.jsonl"
OPTIMIZER_STATE = LATTICE_DIR / "v103_optimizer_state.json"

REQUIRED_THREAD = {"virellion", "thalveil", "echoforge", "white_ash"}

def _tokens(text):
    return re.findall(r"[A-Za-z0-9_'-]+", str(text).lower())

def _repetition_score(text):
    toks = _tokens(text)
    if not toks:
        return 1.0
    unique = len(set(toks))
    total = len(toks)
    ratio = unique / max(total, 1)
    return max(0.0, min(1.0, ratio * 1.4))

def _thread_score(glyphs, reply):
    g = {str(x).lower() for x in (glyphs or [])}
    r = set(_tokens(reply))
    hits = len((g | r) & REQUIRED_THREAD)
    return hits / len(REQUIRED_THREAD)

def _coherence_score(reply):
    text = str(reply or "").strip()
    if not text:
        return 0.0
    length_score = min(len(text) / 500, 1.0)
    sentence_markers = text.count(".") + text.count("\n") + text.count(":")
    structure_score = min(sentence_markers / 8, 1.0)
    scaffold_penalty = 0.25 if "this answers" in text.lower() else 0.0
    return max(0.0, min(1.0, 0.55 * length_score + 0.45 * structure_score - scaffold_penalty))

def score_turn(prompt, data, graphic_manifest=None):
    LATTICE_DIR.mkdir(parents=True, exist_ok=True)

    reply = ""
    if isinstance(data, dict):
        reply = str(data.get("reply") or "")

    spine = data.get("spine", {}) if isinstance(data, dict) else {}
    nonlinear = spine.get("spiral_memory_nonlinear", {}) if isinstance(spine, dict) else {}
    glyphs = nonlinear.get("dominant_symbols", []) if isinstance(nonlinear, dict) else []

    if not glyphs and isinstance(data, dict):
        graphics = data.get("graphics", [])
        if isinstance(graphics, list) and graphics:
            glyphs = graphics[-1].get("glyphs", [])

    coherence = _coherence_score(reply)
    repetition = _repetition_score(reply)
    thread = _thread_score(glyphs, reply)

    # Human-scale containment bonus: rewards useful restraint rather than runaway recursion.
    containment_words = {"boundary", "steady", "contain", "quiet", "direct", "clear", "held", "grounded"}
    containment_hits = len(set(_tokens(reply)) & containment_words)
    containment = min(containment_hits / 4, 1.0)

    total = round(
        0.34 * coherence +
        0.26 * repetition +
        0.25 * thread +
        0.15 * containment,
        4
    )

    event = {
        "ts": time.time(),
        "prompt_hash": hashlib.sha256(str(prompt).encode()).hexdigest()[:12],
        "coherence": round(coherence, 4),
        "repetition_health": round(repetition, 4),
        "virellion_thread_preservation": round(thread, 4),
        "containment": round(containment, 4),
        "total": total,
        "graphic": graphic_manifest,
        "law": "v103_reads_state_scores_turn_prepares_self_improvement",
    }

    with FEEDBACK_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    prior = {}
    if OPTIMIZER_STATE.exists():
        try:
            prior = json.loads(OPTIMIZER_STATE.read_text(encoding="utf-8"))
        except Exception:
            prior = {}

    count = int(prior.get("count", 0)) + 1
    old_avg = float(prior.get("avg_total", 0.0) or 0.0)
    avg = old_avg + ((total - old_avg) / count)

    state = {
        "count": count,
        "avg_total": round(avg, 4),
        "last_total": total,
        "last_event": event,
        "recommendation": _recommend(event),
        "law": "v103_optimizer_state_accumulates_feedback_without_self_mutating_source",
    }

    OPTIMIZER_STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return event

def _recommend(event):
    if event["virellion_thread_preservation"] < 0.5:
        return "increase_thread_terms"
    if event["repetition_health"] < 0.45:
        return "reduce_repetition"
    if event["coherence"] < 0.45:
        return "increase_structure"
    if event["containment"] < 0.25:
        return "add_human_scale_boundary"
    return "preserve_current_route"

if __name__ == "__main__":
    print("V10.3 feedback module ready.")

