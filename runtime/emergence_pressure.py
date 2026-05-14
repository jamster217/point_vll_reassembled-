from __future__ import annotations
import json, math, os, re
from collections import Counter
from datetime import datetime
from typing import Dict, Any, List, Tuple

MOTIF_PATH = os.path.join("assets", "memory", "motif_shadow.json")

DEFAULT_PRESSURE = {
    "coherence": 0.30,
    "tone_consistency": 0.18,
    "cadence_smoothness": 0.14,
    "motif_recurrence": 0.12,
    "atmospheric_continuity": 0.10,
    "semantic_surprise": 0.08,
    "jarring_transition": -0.18,
    "tonal_break": -0.10,
}

STOP = {
    "the","a","an","and","or","but","if","to","of","in","on","for","with",
    "is","are","was","were","be","been","being","it","that","this","as","at",
    "by","from","i","you","he","she","they","we","me","him","her","them","my",
    "your","our","their"
}

ATMOS_WORDS = {
    "shadow","light","ash","window","still","quiet","silence","breath","room",
    "memory","echo","glass","dust","pale","hollow","soft","night","rain","door"
}

def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))

def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z']+", (text or "").lower())

def _lines(text: str) -> List[str]:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]

def load_motif_shadow(path: str = MOTIF_PATH) -> Dict[str, Any]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "token_freq": {},
        "phrase_freq": {},
        "cadence_profile": {"avg_words_per_line": 0.0, "pause_density": 0.0, "fragment_rate": 0.0, "samples": 0},
        "semantic_clusters": {},
        "last_updated": None
    }

def save_motif_shadow(data: Dict[str, Any], path: str = MOTIF_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data["last_updated"] = datetime.utcnow().isoformat() + "Z"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_motif_shadow(text: str, path: str = MOTIF_PATH) -> Dict[str, Any]:
    data = load_motif_shadow(path)
    toks = [t for t in _tokens(text) if t not in STOP and len(t) > 2]
    token_counts = Counter(toks)

    phrases = []
    raw = _tokens(text)
    for i in range(len(raw) - 1):
        bg = f"{raw[i]} {raw[i+1]}"
        if raw[i] not in STOP and raw[i+1] not in STOP:
            phrases.append(bg)
    phrase_counts = Counter(phrases)

    for k, v in token_counts.items():
        data["token_freq"][k] = data["token_freq"].get(k, 0) + v
    for k, v in phrase_counts.items():
        data["phrase_freq"][k] = data["phrase_freq"].get(k, 0) + v

    lines = _lines(text) or [text]
    word_counts = [len(_tokens(ln)) for ln in lines if ln.strip()]
    avg_words = sum(word_counts) / max(1, len(word_counts))
    pause_density = (text.count(",") + text.count(";") + text.count("—") + text.count("-")) / max(1, len(text))
    fragment_rate = sum(1 for ln in lines if len(_tokens(ln)) <= 5) / max(1, len(lines))

    cp = data["cadence_profile"]
    n = cp.get("samples", 0)
    cp["avg_words_per_line"] = ((cp.get("avg_words_per_line", 0.0) * n) + avg_words) / (n + 1)
    cp["pause_density"] = ((cp.get("pause_density", 0.0) * n) + pause_density) / (n + 1)
    cp["fragment_rate"] = ((cp.get("fragment_rate", 0.0) * n) + fragment_rate) / (n + 1)
    cp["samples"] = n + 1

    semantic = data.get("semantic_clusters", {})
    semantic["interior_space"] = semantic.get("interior_space", 0.0) + sum(1 for t in toks if t in {"room","window","door","hall","inside"})
    semantic["memory"] = semantic.get("memory", 0.0) + sum(1 for t in toks if t in {"memory","remember","echo","past","trace"})
    semantic["light_shadow"] = semantic.get("light_shadow", 0.0) + sum(1 for t in toks if t in {"light","shadow","ash","glow","pale"})
    data["semantic_clusters"] = semantic

    save_motif_shadow(data, path)
    return data

def motif_recurrence_score(text: str, shadow: Dict[str, Any]) -> float:
    toks = [t for t in _tokens(text) if t not in STOP and len(t) > 2]
    if not toks:
        return 0.0
    tf = shadow.get("token_freq", {})
    hits = sum(min(tf.get(t, 0), 5) for t in toks)
    return _clamp(hits / (len(toks) * 3.0))

def cadence_smoothness_score(text: str, shadow: Dict[str, Any]) -> float:
    cp = shadow.get("cadence_profile", {})
    target = float(cp.get("avg_words_per_line", 8.0) or 8.0)
    lines = _lines(text) or [text]
    wc = [len(_tokens(ln)) for ln in lines if ln.strip()]
    if not wc:
        return 0.0
    avg = sum(wc) / len(wc)
    delta = abs(avg - target)
    return _clamp(1.0 - (delta / max(4.0, target)))

def atmospheric_continuity_score(text: str) -> float:
    toks = _tokens(text)
    if not toks:
        return 0.0
    hits = sum(1 for t in toks if t in ATMOS_WORDS)
    return _clamp(hits / max(3, len(toks) / 4))

def jarring_transition_score(prev_text: str, text: str) -> float:
    if not prev_text.strip() or not text.strip():
        return 0.0
    prev_toks = set(_tokens(prev_text))
    cur_toks = set(_tokens(text))
    overlap = len(prev_toks & cur_toks) / max(1, len(cur_toks))
    prev_exc = prev_text.count("!")
    cur_exc = text.count("!")
    punctuation_jump = abs(cur_exc - prev_exc) / 3.0
    short_prev = len(_tokens(prev_text))
    short_cur = len(_tokens(text))
    length_jump = abs(short_cur - short_prev) / max(10.0, short_prev + 1.0)
    return _clamp((1.0 - overlap) * 0.5 + punctuation_jump * 0.25 + length_jump * 0.25)

def tone_consistency_score(prev_text: str, text: str) -> float:
    if not prev_text.strip():
        return 0.5
    prev_soft = sum(prev_text.lower().count(v) for v in ["a","e","i","o","u"])
    cur_soft = sum(text.lower().count(v) for v in ["a","e","i","o","u"])
    prev_len = max(1, len(prev_text))
    cur_len = max(1, len(text))
    prev_ratio = prev_soft / prev_len
    cur_ratio = cur_soft / cur_len
    return _clamp(1.0 - abs(prev_ratio - cur_ratio) * 8.0)

def semantic_surprise_score(text: str, shadow: Dict[str, Any]) -> float:
    toks = [t for t in _tokens(text) if t not in STOP and len(t) > 2]
    if not toks:
        return 0.0
    tf = shadow.get("token_freq", {})
    unseen = sum(1 for t in toks if tf.get(t, 0) == 0)
    return _clamp(unseen / max(1, len(toks)))

def coherence_score(text: str) -> float:
    lines = _lines(text) or [text]
    if not lines:
        return 0.0
    lens = [len(_tokens(ln)) for ln in lines if ln.strip()]
    if not lens:
        return 0.0
    variance = sum((x - (sum(lens)/len(lens)))**2 for x in lens) / max(1, len(lens))
    punct = text.count(",") + text.count(".") + text.count(";") + text.count(":")
    return _clamp(0.65 + min(0.2, punct / max(20, len(text))) - min(0.3, variance / 40.0))

def score_candidate(text: str, prev_text: str = "", path: str = MOTIF_PATH) -> Dict[str, float]:
    shadow = load_motif_shadow(path)
    parts = {
        "coherence": coherence_score(text),
        "tone_consistency": tone_consistency_score(prev_text, text),
        "cadence_smoothness": cadence_smoothness_score(text, shadow),
        "motif_recurrence": motif_recurrence_score(text, shadow),
        "atmospheric_continuity": atmospheric_continuity_score(text),
        "semantic_surprise": semantic_surprise_score(text, shadow),
        "jarring_transition": jarring_transition_score(prev_text, text),
        "tonal_break": max(0.0, jarring_transition_score(prev_text, text) - 0.35),
    }
    total = 0.0
    for k, v in parts.items():
        total += DEFAULT_PRESSURE.get(k, 0.0) * v
    parts["total"] = round(total, 6)
    return parts

if __name__ == "__main__":
    sample_prev = "The room held its breath near the window."
    sample_cur = "Stillness gathered in the glass like ash."
    print(score_candidate(sample_cur, sample_prev))
    update_motif_shadow(sample_prev)
    update_motif_shadow(sample_cur)
    print("ok")

