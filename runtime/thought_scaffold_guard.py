import re
from typing import Dict

# ===================================================================
# THOUGHT SCAFFOLD GUARD - v5
# ===================================================================

BANNED_REGEXES = [
    r"A structured relationship forms through constrained interaction\.?",
    r"The prompt is outside the current routed patterns, so the next step is(?:\s*:\s*|\s*\.\s*|\s+)?",
    r"(?:to\s+)?map it to the closest stable domain(?: instead of forcing a generic answer)?(?:\.{1,3})?",
    r"closest stable domain(?: instead of forcing a generic answer)?(?:\.{1,3})?",
    r"That is a conceptual question(?:\. Answer it directly in terms of structure(?:, memory, time, emotion, and relation)?\.?|\. Give a direct definition first\.?)?",
    r"The emotional layer should ground the feeling first(?:\. Only after that should it widen into symbolism\.?)?",
    r"There is a balanced interaction between forces(?:, allowing gradual movement and change)?\.?",
    r"It carries a trace of what was already there\.?",
    r"No strong critique motifs detected; output can pass unchanged\.?",
    r"Detected motifs are already relatively stable; no corrective mutation was needed\.?",
    r"Detected motifs.*?$",
    r"Suggested stabilized motifs.*?$",
    r"\|\s*counter-balanced by\s*\|.*?$",
]

WORD_RE = re.compile(r"[a-zA-Z0-9_\-']+")

def _clean(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" .", ".").replace(" ,", ",")
    text = re.sub(r"\.\s*\.", ".", text)
    text = re.sub(r"^\s*to\s+(?=[a-z])", "", text, flags=re.I)
    return text.strip()

def _words(text: str):
    return WORD_RE.findall(text.lower())

def strip_banned(text: str) -> str:
    out = text or ""
    for pat in BANNED_REGEXES:
        out = re.sub(pat, " ", out, flags=re.I | re.M)
    out = re.sub(r"\s+", " ", out)
    out = re.sub(r"\.\s*\.", ".", out)
    return _clean(out)

def info_tokens(text: str):
    stop = {
        "the","a","an","and","or","but","if","then","so","to","of","in","on","at",
        "is","it","this","that","with","for","as","by","from","be","was","were",
        "are","has","have","had","into","through","over","under","between","what"
    }
    return [w for w in _words(strip_banned(text)) if len(w) > 3 and w not in stop]

def adds_information(prev: str, new: str, min_new: int = 2) -> bool:
    prev_set = set(info_tokens(prev))
    new_set = set(info_tokens(new))
    added = [w for w in new_set if w not in prev_set]
    return len(added) >= min_new

def compress_stage(text: str) -> str:
    return strip_banned(text)

def enforce_reasoning_progression(thesis: str, synthesis: str, final_point: str) -> Dict[str, str]:
    thesis = compress_stage(thesis)
    synthesis = compress_stage(synthesis)
    final_point = compress_stage(final_point)

    if not thesis:
        thesis = ""
    if not synthesis:
        synthesis = thesis
    if not final_point:
        final_point = synthesis or thesis

    if thesis and synthesis and not adds_information(thesis, synthesis):
        synthesis = thesis

    if synthesis and final_point and not adds_information(synthesis, final_point):
        final_point = synthesis

    if not final_point:
        final_point = synthesis or thesis

    return {
        "thesis": thesis,
        "synthesis": synthesis,
        "final_point": final_point,
    }

def repair_single_output(text: str) -> str:
    original = (text or "").strip()
    cleaned = compress_stage(original)
    low = original.lower()

    # If scaffold stripping removes everything, keep only emotionally important
    # very short outputs; otherwise return empty string instead of the original scaffold.
    if not cleaned:
        if any(k in low for k in ("black hole", "grief", "dad", "father", "loss")):
            return original
        return ""

    if len(cleaned) < 15 and any(k in low for k in ("black hole", "grief", "dad", "father", "loss")):
        return original

    return cleaned

def clean_output(text: str) -> str:
    return repair_single_output(text)

if __name__ == "__main__":
    test1 = '''This carries the weight of: "Only the markings remained..." A structured relationship forms through constrained interaction. | counter-balanced by | No strong critique motifs detected...'''
    test2 = 'The prompt is outside the current routed patterns, so the next step is to map it to the closest stable domain... It carries a trace of what was already there.'

    print("=== CLEAN TEST 1 ===")
    print(clean_output(test1))
    print("\n=== CLEAN TEST 2 ===")
    print(clean_output(test2))
    print("\n=== PROGRESSION TEST ===")
    print(enforce_reasoning_progression(test1, test1, test2))

