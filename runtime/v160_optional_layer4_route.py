#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.layer4_lattice_sidecar_v160 import layer4_lattice_sidecar


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "layer4", "layer4_lattice", "v16", "v16.0"}
    return False


def should_use_layer4(body: Dict[str, Any]) -> bool:
    engine = str(body.get("engine") or body.get("route") or body.get("mode") or "").strip().lower()
    if engine in {"layer4", "layer4_lattice", "layer_4", "v16", "v16.0", "lattice"}:
        return True

    if _truthy(body.get("use_layer4")) or _truthy(body.get("layer4_lattice")):
        return True

    return False


def v160_optional_layer4_route(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None

    if not should_use_layer4(body):
        return None

    message = str(body.get("message") or body.get("text") or "").strip()
    return layer4_lattice_sidecar(message)

