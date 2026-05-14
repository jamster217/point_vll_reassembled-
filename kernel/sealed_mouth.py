from __future__ import annotations

from functools import wraps


def seal_text(text: str, mode: str = "terminal") -> str:
    try:
        from runtime.unified_voice import sealed_speak, public_scrub
        sealed = sealed_speak(str(text or ""), mode=mode)
        return sealed if sealed else public_scrub(str(text or ""))
    except Exception:
        return str(text or "")


def sealed_mouth(fn):
    """
    Decorator for terminal/kernel output.
    Wraps raw function output through the Universal Larynx.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        return seal_text(str(result), mode="terminal")
    return wrapper

