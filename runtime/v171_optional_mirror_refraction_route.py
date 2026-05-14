#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.mirror_refraction_v171 import mirror_refraction


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
            "v17.1",
            "mirror",
            "mirror_refraction",
            "mirror-refraction",
        }
    return False


def should_use_mirror_refraction(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()
    if engine in {"v17.1", "mirror", "mirror_refraction", "mirror-refraction", "mirror_refraction_sidecar"}:
        return True

    if _truthy(body.get("use_mirror_refraction")) or _truthy(body.get("mirror_refraction")):
        return True

    return False


def v171_optional_mirror_refraction_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_mirror_refraction(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    return mirror_refraction(message)

