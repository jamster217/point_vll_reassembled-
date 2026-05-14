from __future__ import annotations

def cleanup_surface(text: str) -> str:
    if not text:
        return text

    removals = [
        "Internet lookup result:",
        "Direct read of your prompt:",
        "The system is treating this as",
        "It will answer plainly first, then attach the live mirror state so the response stays connected to the build.",
    ]

    out = str(text)

    for r in removals:
        out = out.replace(r, "")

    # collapse repeated blank lines
    while "\n\n\n" in out:
        out = out.replace("\n\n\n", "\n\n")

    return out.strip()

if __name__ == "__main__":
    sample = "Internet lookup result: Leaves change color."
    print(cleanup_surface(sample))

