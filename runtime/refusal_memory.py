from pathlib import Path
import json, time, re

LOG = Path("var/rejection_memory/refused_surfaces.jsonl")
LOG.parent.mkdir(parents=True, exist_ok=True)

BAD_PATTERNS = [
    "appears as",
    "carrying a role",
    "current pattern",
    "is the doorway",
    "answer is not in the mechanism",
    "living visual cockpit",
    "something old or hidden is surfacing",
    "hold the pressure",
    "name what is actually being asked",
]

def detect_refusal(reply: str):
    text = (reply or "").lower()
    return [p for p in BAD_PATTERNS if p in text]

def log_refusal(prompt: str, reply: str, reason=None):
    reasons = reason or detect_refusal(reply)
    if not reasons:
        return False

    row = {
        "ts": time.time(),
        "prompt": prompt,
        "reply_preview": (reply or "")[:220],
        "reasons": reasons,
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return True

def refusal_pressure(prompt: str):
    """
    Returns a soft bias score based on past refusals.
    Higher means: be more prompt-specific, less scaffolded.
    """
    if not LOG.exists():
        return 0.0

    p = (prompt or "").lower()
    words = set(re.findall(r"[a-zA-Z']{4,}", p))
    if not words:
        return 0.0

    score = 0.0
    try:
        rows = LOG.read_text(encoding="utf-8").splitlines()[-200:]
        for line in rows:
            obj = json.loads(line)
            old = (obj.get("prompt") or "").lower()
            old_words = set(re.findall(r"[a-zA-Z']{4,}", old))
            overlap = len(words & old_words)
            if overlap:
                score += min(0.25, overlap * 0.04)
    except Exception:
        return 0.0

    return min(score, 1.0)

def repair_instruction(prompt: str):
    pressure = refusal_pressure(prompt)
    if pressure <= 0:
        return ""

    return (
        "Refusal memory active: avoid prior rejected scaffold/meta surfaces. "
        "Answer the user's exact prompt with concrete imagery, direct usefulness, "
        "and no machinery description."
    )

