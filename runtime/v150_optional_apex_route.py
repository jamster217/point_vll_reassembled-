#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.apex_matrix_sidecar_v150 import apex_matrix_sidecar


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "v15", "apex", "apex_matrix"}
    return False


def should_use_v15(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()
    if engine in {"v15", "apex", "apex_matrix", "apex_matrix_sidecar"}:
        return True

    if _truthy(body.get("use_v15")) or _truthy(body.get("apex_matrix")):
        return True

    return False


def v150_optional_apex_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_v15(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    return apex_matrix_sidecar(message)

