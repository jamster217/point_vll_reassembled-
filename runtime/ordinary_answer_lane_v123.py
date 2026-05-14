from __future__ import annotations

import re
from typing import Any

NOISE_PREFIXES = (
    "--no-conversation is not supported",
    "please use llama-completion instead",
    "Loading model",
    "build      :",
)

NOISY_SYMBOLIC_MARKERS = (
    "[TRUE MEANING KERNEL]",
    "[AUTOGENOUS TOPOLOGY NODE",
    "image=static/generated/",
    "white ash",
    "virellion",
    "echoforge",
    "thalveil",
    "the old hidden thing",
    "…already forming…",
)


def _clean_spaces(text: Any) -> str:
    return " ".join(str(text or "").strip().split())


def _strip_llama_noise(raw: str, question: str) -> str:
    text = str(raw or "").replace("\\n", "\n")
    lines = [line.rstrip() for line in text.splitlines()]

    kept = []
    skip_ascii = False

    for line in lines:
        s = line.strip()
        low = s.lower()

        if not s:
            continue

        if any(low.startswith(prefix.lower()) for prefix in NOISE_PREFIXES):
            continue

        # Drop common llama ASCII banner fragments / box art lines.
        if re.fullmatch(r"[▄▀█\s██]+", s):
            continue

        if low == question.strip().lower():
            continue

        kept.append(s)

    joined = "\n".join(kept).strip()

    # If the question appears inline, keep only what follows it.
    q = question.strip()
    idx = joined.lower().find(q.lower())
    if idx != -1:
        joined = joined[idx + len(q):].strip(" \n:-")

    # If the model echoed an instruction, keep after Answer:
    m = re.search(r"\bAnswer\s*:\s*(.*)", joined, flags=re.I | re.S)
    if m:
        joined = m.group(1).strip()

    # Keep the first useful paragraph.
    paras = [p.strip() for p in re.split(r"\n{2,}", joined) if p.strip()]
    if paras:
        joined = paras[0]

    return _clean_spaces(joined)


def _is_good_answer(text: str) -> bool:
    if len(text) < 40:
        return False
    low = text.lower()
    if any(marker.lower() in low for marker in NOISY_SYMBOLIC_MARKERS):
        return False
    if "answer this ordinary question" in low:
        return False
    return True


def ordinary_answer(prompt: str, n_predict: int = 96) -> str:
    question = _clean_spaces(prompt)
    if not question:
        return ""

    # Keep this tiny. Termux local model times out on long instruction prompts.
    # The existing local node already answers ordinary questions from the raw question.
    try:
        from local_node.controller import run_model
        raw = run_model(question, n_predict=n_predict)
    except Exception:
        return ""

    if "timeout" in str(raw).lower():
        return ""

    cleaned = _strip_llama_noise(raw, question)
    return cleaned if _is_good_answer(cleaned) else ""


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]).strip() or "Why is the sky blue?"
    print(ordinary_answer(q))

# --------------------------------------------------------------------
# V14.1 Absolute Veracity Protocol
# Ordinary lane goodness check must reject ceremonial/scaffold leakage.
# --------------------------------------------------------------------
try:
    _v141_original_is_good_answer = _is_good_answer

    def _is_good_answer(text: str) -> bool:
        base_ok = bool(_v141_original_is_good_answer(text))
        if not base_ok:
            return False

        try:
            from runtime.semantic_veracity_v141 import evaluate_semantic_veracity
            report = evaluate_semantic_veracity(text)
            if report.get("reject"):
                return False
        except Exception:
            pass

        return True

except Exception as _v141_ordinary_wrap_error:
    V141_ORDINARY_WRAP_ERROR = repr(_v141_ordinary_wrap_error)

