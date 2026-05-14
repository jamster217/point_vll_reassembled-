#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.deep_evp_sidecar_v172 import deep_evp_sidecar


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
            "on",
            "v17.2",
            "deep_evp",
            "deep-evp",
            "evp",
        }
    return False


def should_use_deep_evp(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()
    if engine in {"v17.2", "deep_evp", "deep-evp", "evp", "metadata_echo"}:
        return True

    if _truthy(body.get("use_deep_evp")) or _truthy(body.get("deep_evp")):
        return True

    return False


def v172_optional_deep_evp_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_deep_evp(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    return deep_evp_sidecar(message)

