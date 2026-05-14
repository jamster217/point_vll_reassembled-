#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.fractal_core_replication_v182 import fractal_core_replication


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
            "v18.2",
            "fractal_core",
            "fractal-core",
            "fractal_replication",
            "fractal-core-replication",
        }
    return False


def should_use_fractal_core(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()

    if engine in {
        "v18.2",
        "fractal_core",
        "fractal-core",
        "fractal_replication",
        "fractal-core-replication",
        "fractal_core_replication",
    }:
        return True

    if _truthy(body.get("use_fractal_core")) or _truthy(body.get("fractal_core")):
        return True

    return False


def v182_optional_fractal_core_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_fractal_core(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    return fractal_core_replication(message)

