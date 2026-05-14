import re

STOP = {"the","a","an","and","or","but","to","of","in","on","at","for","with","as","is","are","was","were","be","been","being","it","that","this","you","i","we","they","he","she","them","him","her"}

def toks(s: str):
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9\s'\-]", " ", s)
    out = [t for t in s.split() if len(t) > 2 and t not in STOP]
    return set(out)

def fidelity_score(seed_text: str, candidate_text: str) -> float:
    A = toks(seed_text)
    B = toks(candidate_text)
    if not A or not B:
        return 0.0
    overlap = len(A & B)
    return overlap / max(1, len(A))

def contradiction_flag(seed_text: str, candidate_text: str) -> bool:
    # super-light guardrail: deny obvious polarity flips
    seed = (seed_text or "").lower()
    cand = (candidate_text or "").lower()
    flips = [
        ("never", "always"),
        ("no longer", "forever"),
        ("cannot", "can"),
        ("won't", "will"),
        ("not", ""),  # crude: only used with threshold below
    ]
    # only trigger on very obvious flips where seed contains one and cand contains the opposite
    if ("cannot" in seed and "can" in cand) or ("won't" in seed and "will" in cand):
        return True
    if ("never" in seed and "always" in cand) or ("always" in seed and "never" in cand):
        return True
    return False

