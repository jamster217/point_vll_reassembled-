#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.coherent_meaning_engine_v14 import coherent_meaning_engine, prove_packet


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "v14", "coherent_meaning_engine"}
    return False


def should_use_v14(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()
    if engine in {"v14", "cme", "coherent_meaning_engine", "meaning_engine"}:
        return True

    if _truthy(body.get("use_v14")) or _truthy(body.get("meaning_engine")):
        return True

    return False


def v141_optional_meaning_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_v14(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    out = coherent_meaning_engine(message)
    proof = prove_packet(out)

    meta = out.setdefault("meta", {})
    meta["v141_optional_api_route"] = "active"
    meta["v141_invocation"] = {
        "engine": body.get("engine"),
        "use_v14": body.get("use_v14"),
        "route": body.get("route"),
        "mode": body.get("mode"),
    }
    meta["v141_proof"] = proof

    return out

