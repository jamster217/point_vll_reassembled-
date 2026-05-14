from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

LOG_PATH = Path("logs/sigil_watcher/cognitive_events.jsonl")


def _read_last_event() -> Dict[str, Any]:
    try:
        if not LOG_PATH.exists():
            return {}
        lines = [x for x in LOG_PATH.read_text(encoding="utf-8", errors="ignore").splitlines() if x.strip()]
        if not lines:
            return {}
        return json.loads(lines[-1])
    except Exception:
        return {}


def latest_sigil_context(max_age_seconds: int = 21600) -> Dict[str, Any]:
    event = _read_last_event()
    if not event:
        return {}

    ts = float(event.get("ts", 0) or 0)
    age = time.time() - ts if ts else 999999

    if age > max_age_seconds:
        return {}

    synthesis = event.get("synthesis", {}) or {}
    definition = event.get("definition", {}) or {}
    ripples = event.get("ripples", {}) or {}

    return {
        "source": "sigil_watcher_cognitive",
        "sigil_path": event.get("sigil_path", ""),
        "field_signature": synthesis.get("field_signature", "92162077"),
        "mode": synthesis.get("mode", "observe"),
        "vectors": synthesis.get("vectors", {}),
        "tokens": definition.get("tokens", [])[:16],
        "registry_matches": definition.get("registry_matches", [])[:4],
        "ripple_count": len(ripples.get("ripples", []) or []),
        "top_ripples": [
            {
                "path": r.get("path"),
                "score": r.get("score"),
                "hits": r.get("hits", [])[:8],
            }
            for r in (ripples.get("ripples", []) or [])[:6]
        ],
        "law": event.get("law", ""),
        "mutation_policy": event.get("mutation_policy", ""),
    }


def enrich_shape_with_sigil(shape: Dict[str, Any]) -> Dict[str, Any]:
    shape = dict(shape or {})
    ctx = latest_sigil_context()
    if ctx:
        shape["sigil_context"] = ctx

        # Gentle vector influence only. No forced mutation.
        sv = ctx.get("vectors", {}) or {}
        v = dict(shape.get("vectors", {}) or {})

        for k in ("pressure", "memory", "novelty"):
            if k in sv:
                current = float(v.get(k, 0.45) or 0.45)
                incoming = float(sv.get(k, 0.45) or 0.45)
                v[k] = round((current * 0.75) + (incoming * 0.25), 3)

        shape["vectors"] = v

    return shape


def hidden_sigil_note(shape: Dict[str, Any]) -> str:
    ctx = (shape or {}).get("sigil_context", {}) or {}
    if not ctx:
        return ""

    tokens = ", ".join(ctx.get("tokens", [])[:10])
    ripple_paths = ", ".join(
        r.get("path", "") for r in ctx.get("top_ripples", [])[:3] if r.get("path")
    )

    return (
        "\nHidden sigil context only — do not mention unless asked.\n"
        f"Latest sigil mode: {ctx.get('mode')}. "
        f"Vectors: {ctx.get('vectors')}. "
        f"Tokens: {tokens}. "
        f"Top ripples: {ripple_paths}. "
        "Use this only as shape pressure, not as visible content.\n"
    )

