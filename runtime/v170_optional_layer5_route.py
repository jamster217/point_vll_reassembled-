#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.layer5_core_sidecar_v170 import layer5_core_sidecar


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "layer5", "layer_5", "v17", "v17.0"}
    return False


def should_use_layer5(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()
    if engine in {"layer5", "layer_5", "v17", "v17.0", "layer5_core"}:
        return True

    if _truthy(body.get("use_layer5")) or _truthy(body.get("layer5_core")):
        return True

    return False


def v170_optional_layer5_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_layer5(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    return layer5_core_sidecar(message)

