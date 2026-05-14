#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.density_inversion_axis_v180 import density_inversion_axis


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
            "v18",
            "v18.0",
            "density_inversion",
            "density-inversion",
            "density_inversion_axis",
            "meaning_inversion",
        }
    return False


def should_use_density_inversion(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()

    if engine in {
        "v18",
        "v18.0",
        "density_inversion",
        "density-inversion",
        "density_inversion_axis",
        "meaning_inversion",
        "inversion_axis",
    }:
        return True

    if _truthy(body.get("use_density_inversion")) or _truthy(body.get("density_inversion")):
        return True

    return False


def v180_optional_density_inversion_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_density_inversion(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    return density_inversion_axis(message)

