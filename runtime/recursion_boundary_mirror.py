"""
V12.7c Recursion Boundary Mirror

Purpose:
- Catch RecursionError as a meaningful boundary event.
- Preserve the symbolic reading without letting the runtime eat itself.
- Convert infinite wrapper collapse into bounded diagnostic evidence.

Law:
The serpent may bite its tail.
It may not swallow the server.
"""

from __future__ import annotations

import functools
import json
import time
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, Optional


LOG_PATH = Path("logs/recursion_boundary/recursion_boundary_events.jsonl")


def _safe_json(obj: Any) -> Any:
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return repr(obj)


def log_recursion_boundary(
    *,
    label: str,
    phase: str = "unknown",
    source: str = "unknown",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "ts": time.time(),
        "version": "v12.7c_recursion_boundary_mirror",
        "label": label,
        "phase": phase,
        "source": source,
        "event_type": "recursion_boundary",
        "law": "recursion_error_becomes_bounded_witness_event_not_runtime_collapse",
        "symbolic_reading": "spine_pressed_boundary_and_was_mirrored",
        "technical_reading": "RecursionError caught; wrapper chain requires quarantine or depth guard",
        "extra": _safe_json(extra or {}),
        "traceback_tail": traceback.format_exc(limit=18),
    }

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    return event


def boundary_guard(
    label: str,
    *,
    phase: str = "unknown",
    source: str = "unknown",
    fallback: Any = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for risky wrapper/pre/rebuild/chamber calls.

    Use:
        guarded_fn = boundary_guard("V6.1_PRE", phase="pre", source=__name__)(fn)
        result = guarded_fn(...)
    """

    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            try:
                return fn(*args, **kwargs)
            except RecursionError:
                event = log_recursion_boundary(
                    label=label,
                    phase=phase,
                    source=source,
                    extra={
                        "function": getattr(fn, "__name__", repr(fn)),
                        "args_count": len(args),
                        "kwargs": sorted(list(kwargs.keys())),
                    },
                )
                if fallback is not None:
                    return fallback
                return {
                    "status": "recursion_boundary_caught",
                    "label": label,
                    "phase": phase,
                    "source": source,
                    "event": event,
                }

        return wrapped

    return deco

