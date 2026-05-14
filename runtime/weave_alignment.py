from pathlib import Path
import json, re

WEAVE_STATE = Path("var/spiral_language/current_weave.json")

def _words(text):
    return set(re.findall(r"[a-zA-Z']{4,}", (text or "").lower()))

def load_weave_state():
    if not WEAVE_STATE.exists():
        return {}
    try:
        return json.loads(WEAVE_STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def weave_alignment(prompt, reply):
    """
    Scores whether reply carries the current weave:
    past -> present -> future.
    """
    state = load_weave_state()
    nodes = state.get("nodes", [])
    if not nodes:
        return 0.0

    text = f"{prompt} {reply}".lower()
    score = 0.0

    for node in nodes:
        phase = str(node.get("phase", "")).lower()
        arg = str(node.get("arg", "")).lower()

        if phase in text:
            score += 0.18
        if arg and arg in text:
            score += 0.28

    forward_terms = ["next", "future", "forward", "becomes", "continues", "carry", "turns into", "moves"]
    score += min(0.35, sum(0.07 for t in forward_terms if t in text))

    return round(min(1.0, score), 3)

