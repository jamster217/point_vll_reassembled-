#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.apex_v16_sync_v161 import apex_v16_sync


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "v16.1", "apex_v16", "apex-v16", "apex_lattice"}
    return False


def should_use_apex_v16(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()
    if engine in {"v16.1", "apex_v16", "apex-v16", "apex_lattice", "apex_v16_sync"}:
        return True

    if _truthy(body.get("use_apex_v16")) or _truthy(body.get("apex_v16_sync")):
        return True

    return False


def v161_optional_apex_v16_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_apex_v16(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    return apex_v16_sync(message)

