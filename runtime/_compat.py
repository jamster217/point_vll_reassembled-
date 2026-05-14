from __future__ import annotations

from typing import Any


def clamp(x: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        v = float(x)
    except Exception:
        v = 0.0
    return max(lo, min(hi, v))


def _clamp(x: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    return clamp(x, lo, hi)


def identity(x: Any, *args: Any, **kwargs: Any) -> Any:
    return x


def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return float(default)


def safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return int(default)


def as_dict(x: Any) -> dict[str, Any]:
    return x if isinstance(x, dict) else {}


def as_list(x: Any) -> list[Any]:
    return x if isinstance(x, list) else ([] if x is None else [x])


class _CompatFallback:
    """
    Observer-mode fallback for unknown compat symbols.
    Safe enough for import-time and light runtime probing.
    """

    def __init__(self, name: str = "compat_fallback") -> None:
        self.name = name

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if args:
            return args[0]
        if "default" in kwargs:
            return kwargs["default"]
        return None

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return f"<_CompatFallback {self.name}>"

    def __iter__(self):
        return iter(())


def __getattr__(name: str) -> Any:
    # lets "from runtime._compat import something_missing"
    # resolve during observer-mode probing without crashing import
    return _CompatFallback(name)


__all__ = [
    "clamp",
    "_clamp",
    "identity",
    "safe_float",
    "safe_int",
    "as_dict",
    "as_list",
]

