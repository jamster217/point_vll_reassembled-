def apply(text: str, coherence: float):
    if not text:
        return text

    if coherence < 0.75:
        text = text.split(".")[0].strip()
        if text and not text.endswith("."):
            text += "."

    words = text.split()
    out = []
    for w in words:
        if not out or out[-1] != w:
            out.append(w)
    text = " ".join(out)

    if len(text) > 420:
        text = text[:420].rsplit(" ", 1)[0] + "..."

    return text

