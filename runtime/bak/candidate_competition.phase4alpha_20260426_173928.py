from pathlib import Path
import json, time, re

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
    """
    Chronifier-lite continuity score.
    Rewards replies that carry the current trajectory instead of acting like an isolated turn.
    """
    text = f"{prompt} {reply}".lower()
    continuity_terms = [
        "next", "again", "still", "continues", "carry", "carried",
        "memory", "timeline", "turn", "path", "future", "previous",
        "pressure", "release", "holding", "becomes"
    ]
    hits = sum(1 for t in continuity_terms if t in text)
    return min(1.0, hits / 6.0)


def chronifier_weight():
    """
    Reads Presence Kernel if available.
    Uses resonance/gravitas as soft pressure on candidate selection.
    """
    try:
        from runtime.presence_kernel import PresenceState
        st = PresenceState.load()
        return min(0.8, max(0.05, (float(st.resonance) + float(st.gravitas)) / 3.0))
    except Exception:
        return 0.15


def score_candidate(prompt, reply):
    text = (reply or "").lower()
    pwords = _words(prompt)
    rwords = _words(reply)

    bad_hits = [b for b in BAD_PATTERNS if b in text]
    overlap = len(pwords & rwords)
    length = len(reply or "")

    score = 0.0
    score += overlap * 2.0
    score += min(length / 220, 1.0) * 3.0
    score -= len(bad_hits) * 100.0
    score += chronifier_weight() * timeline_alignment(prompt, reply)

    if length < 90:
        score -= 4.0

    return {
        "score": round(score, 3),
        "bad_hits": bad_hits,
        "overlap": overlap,
        "length": length,
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
                    "preview": r["reply"][:160],
                }
                for r in ranked
            ],
        }, ensure_ascii=False) + "\n")

    return winner["reply"], ranked

