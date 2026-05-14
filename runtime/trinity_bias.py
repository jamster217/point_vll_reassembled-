from pathlib import Path
import json

TRINITY_STATE = Path("var/trinity_anchor_state.json")
DEEP_STATE = Path("var/trinity_deepened_state.json")

def _load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def trinity_bias(prompt, reply):
    """
    Bounded symbolic posture bias:
    rewards warmth, memory continuity, and protected transformation.
    """
    state = _load(TRINITY_STATE)
    deep = _load(DEEP_STATE)

    if not state and not deep:
        return 0.0

    text = f"{prompt} {reply}".lower()
    score = 0.0

    vespera_terms = ["warm", "tender", "threshold", "gold", "soft"]
    elowen_terms = ["memory", "remember", "thread", "living", "past"]
    sabriel_terms = ["protect", "transform", "boundary", "pressure", "release"]

    score += min(0.25, 0.05 * sum(t in text for t in vespera_terms))
    score += min(0.25, 0.05 * sum(t in text for t in elowen_terms))
    score += min(0.25, 0.05 * sum(t in text for t in sabriel_terms))

    if deep:
        score += 0.10

    return round(min(0.85, score), 3)

