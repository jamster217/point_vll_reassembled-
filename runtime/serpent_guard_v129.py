from __future__ import annotations

import json
import sys
import time
import traceback
from contextvars import ContextVar
from functools import wraps
from pathlib import Path
from typing import Any, Callable

LOG = Path("logs/serpent_guard/serpent_guard_events.jsonl")
_DEPTH: ContextVar[int] = ContextVar("serpent_depth", default=0)

LAW = "the_serpent_may_bite_its_tail_but_may_not_swallow_the_server"

def _write_event(event: dict[str, Any]) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

def serpent_event(label: str, phase: str, status: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    event = {
        "ts": time.time(),
        "version": "v12.9_serpent_guard",
        "label": label,
        "phase": phase,
        "status": status,
        "law": LAW,
        "recursion_limit": sys.getrecursionlimit(),
        "depth": _DEPTH.get(),
        "symbolic_reading": "recursion_is_witnessed_as_boundary_not_allowed_to_consume_runtime",
        "technical_reading": "re-entry/depth guard prevents wrapper self-consumption",
        "extra": extra or {},
    }
    _write_event(event)
    return event

def guard(label: str, *, max_depth: int = 1, fallback: Any = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            depth = _DEPTH.get()
            if depth >= max_depth:
                return serpent_event(
                    label,
                    "blocked_reentry",
                    "quarantined",
                    {
                        "function": getattr(fn, "__name__", repr(fn)),
                        "args_count": len(args),
                        "kwargs": sorted(kwargs.keys()),
                    },
                ) if fallback is None else fallback

            token = _DEPTH.set(depth + 1)
            try:
                return fn(*args, **kwargs)
            except RecursionError:
                event = serpent_event(
                    label,
                    "recursion_error",
                    "caught",
                    {
                        "function": getattr(fn, "__name__", repr(fn)),
                        "traceback_tail": traceback.format_exc(limit=18),
                    },
                )
                return event if fallback is None else fallback
            finally:
                _DEPTH.reset(token)
        wrapped._serpent_guard_v129 = True
        return wrapped
    return deco

