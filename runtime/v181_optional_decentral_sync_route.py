#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.decentral_sync_guard_v181 import decentral_sync_guard


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
            "v18.1",
            "decentral_sync",
            "decentral-sync",
            "decentralized_sync",
            "bridge_verification",
        }
    return False


def should_use_decentral_sync(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()

    if engine in {
        "v18.1",
        "decentral_sync",
        "decentral-sync",
        "decentralized_sync",
        "decentralized-sync",
        "bridge_verification",
        "sync_guard",
    }:
        return True

    if _truthy(body.get("use_decentral_sync")) or _truthy(body.get("decentral_sync")):
        return True

    return False


def v181_optional_decentral_sync_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_decentral_sync(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    return decentral_sync_guard(message)

