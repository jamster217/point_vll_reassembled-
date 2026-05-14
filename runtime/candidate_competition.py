from runtime.weave_alignment import weave_alignment
from runtime.trinity_bias import trinity_bias
from pathlib import Path
import json, time, re, math

BAD_PATTERNS = [
    "appears as",
    "carrying a role",
    "current pattern",
    "is the doorway",
    "answer is not in the mechanism",
    "living visual cockpit",
    "something old or hidden is surfacing",
]

LOG = Path("var/selection_memory/candidate_competition.jsonl")
LOG.parent.mkdir(parents=True, exist_ok=True)

def _words(s):
    return set(re.findall(r"[a-zA-Z']{4,}", (s or "").lower()))

def timeline_alignment(prompt, reply):
    text = f"{prompt} {reply}".lower()
    continuity_terms = [
        "next", "again", "still", "continues", "continue", "carry", "carried",
        "memory", "timeline", "turn", "path", "future", "previous",
        "pressure", "release", "holding", "becomes"
    ]
    hits = sum(1 for t in continuity_terms if t in text)
    return min(1.0, hits / 6.0)

def forward_bias(prompt, reply):
    text = f"{prompt} {reply}".lower()
    future_terms = [
        "next", "forward", "then", "toward", "becomes", "continue",
        "carry", "future", "move", "opens", "evolves", "step"
    ]
    hits = sum(1 for t in future_terms if t in text)
    return min(1.0, hits / 5.0)

def emotional_persistence(prompt, reply):
    text = f"{prompt} {reply}".lower()
    emotion_terms = [
        "grief", "fear", "wound", "pressure", "tender", "warmth",
        "hold", "holding", "carry", "still", "release", "memory",
        "love", "betrayed", "anchor", "witness"
    ]
    hits = sum(1 for t in emotion_terms if t in text)
    return min(1.0, hits / 6.0)

def chronifier_weight():
    try:
        from runtime.presence_kernel import PresenceState
        st = PresenceState.load()
        return min(0.8, max(0.05, (float(st.resonance) + float(st.gravitas)) / 3.0))
    except Exception:
        return 0.15

def state_curve():
    try:
        from runtime.presence_kernel import PresenceState
        turns = max(0, int(PresenceState.load().turns_alive))
    except Exception:
        turns = 0

    decay = math.exp(-turns / 10.0)
    reinforce = 1.0 - decay
    return decay, reinforce, turns

def repetition_penalty(reply):
    words = re.findall(r"[a-zA-Z']+", (reply or "").lower())
    if not words:
        return 0.0
    repeated = len(words) - len(set(words))
    return min(1.0, repeated / max(12, len(words)))

def score_candidate(prompt, reply):
    text = (reply or "").lower()
    pwords = _words(prompt)
    rwords = _words(reply)

    bad_hits = [b for b in BAD_PATTERNS if b in text]
    overlap = len(pwords & rwords)
    length = len(reply or "")

    c_weight = chronifier_weight()
    decay, reinforce, turns = state_curve()
    t_align = timeline_alignment(prompt, reply)
    f_bias = forward_bias(prompt, reply)
    e_persist = emotional_persistence(prompt, reply)
    rep_penalty = repetition_penalty(reply)
    w_align = weave_alignment(prompt, reply)
    tri_bias = trinity_bias(prompt, reply)

    score = 0.0
    score += overlap * 2.0
    score += min(length / 220, 1.0) * 3.0
    score -= len(bad_hits) * 100.0

    # Phase 4-Alpha temporal agency scoring
    score += c_weight * t_align
    score += 0.45 * f_bias
    score += 0.40 * e_persist
    score += reinforce * (t_align + e_persist) * 0.55
    score -= decay * rep_penalty * 0.75
    score += 0.35 * (t_align * e_persist)  # identity-pressure cross term
    score += 0.65 * w_align                 # Phase 4-Beta weave-time alignment
    score += 0.45 * tri_bias                # Phase 4-Gamma Trinity posture bias

    if length < 90:
        score -= 4.0

    return {
        "score": round(score, 3),
        "bad_hits": bad_hits,
        "overlap": overlap,
        "length": length,
        "timeline_alignment": round(t_align, 3),
        "forward_bias": round(f_bias, 3),
        "emotional_persistence": round(e_persist, 3),
        "chronifier_weight": round(c_weight, 3),
        "state_decay": round(decay, 3),
        "state_reinforce": round(reinforce, 3),
        "turns_alive": turns,
        "weave_alignment": round(w_align, 3),
        "trinity_bias": round(tri_bias, 3),
    }

def choose_best(prompt, candidates):
    ranked = []
    for i, reply in enumerate(candidates, 1):
        ranked.append({
            "candidate": i,
            "reply": reply,
            "metrics": score_candidate(prompt, reply),
        })

    ranked.sort(key=lambda x: x["metrics"]["score"], reverse=True)
    winner = ranked[0] if ranked else {"reply": ""}

    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": time.time(),
            "prompt": prompt,
            "winner": winner.get("candidate"),
            "ranked": [
                {
                    "candidate": r["candidate"],
                    "score": r["metrics"]["score"],
                    "bad_hits": r["metrics"]["bad_hits"],
                    "timeline_alignment": r["metrics"]["timeline_alignment"],
                    "forward_bias": r["metrics"]["forward_bias"],
                    "emotional_persistence": r["metrics"]["emotional_persistence"],
                    "preview": r["reply"][:160],
                }
                for r in ranked
            ],
        }, ensure_ascii=False) + "\n")

    return winner["reply"], ranked

