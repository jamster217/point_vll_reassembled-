#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.dual_state_mirror_executor_v183 import dual_state_mirror_executor

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
            "v18.3",
            "dual_state_mirror",
            "dual-state-mirror",
            "mirror_executor",
            "dual_state",
        }
    return False

def should_use_dual_state_mirror(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()

    if engine in {
        "v18.3",
        "dual_state_mirror",
        "dual-state-mirror",
        "mirror_executor",
        "dual_state",
        "dual-state",
    }:
        return True

    if _truthy(body.get("use_dual_state_mirror")) or _truthy(body.get("dual_state_mirror")):
        return True

    return False

def v183_optional_dual_state_mirror_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_dual_state_mirror(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    return dual_state_mirror_executor(message)

