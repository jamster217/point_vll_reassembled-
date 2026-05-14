#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.chronofire_sync_v151 import chronofire_sync


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "v15.1", "chronofire", "chronofire_sync"}
    return False


def should_use_v151(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()
    if engine in {"v15.1", "v151", "chronofire", "chronofire_sync", "chronofire-sync"}:
        return True

    if _truthy(body.get("use_chronofire")) or _truthy(body.get("chronofire_sync")):
        return True

    return False


def v151_optional_chronofire_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_v151(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    return chronofire_sync(message)

