from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REGISTRY_PATH = Path("data/registry/genesis_data_registry.json")


def load_genesis_registry() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {"data": [], "ok": False, "error": "missing_registry"}
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"data": [], "ok": False, "error": "registry_not_dict"}
        if "data" not in data or not isinstance(data.get("data"), list):
            return {"data": [], "ok": False, "error": "missing_data_list"}
        data["ok"] = True
        return data
    except Exception as e:
        return {"data": [], "ok": False, "error": f"invalid_registry: {e}"}


def registry_entries() -> List[Dict[str, Any]]:
    data = load_genesis_registry()
    return list(data.get("data", []) or [])


def registry_summary() -> Dict[str, Any]:
    loaded = load_genesis_registry()
    items = list(loaded.get("data", []) or [])
    valid = [x for x in items if x.get("valid_json") is True]
    invalid = [x for x in items if x.get("valid_json") is False]

    return {
        "ok": bool(loaded.get("ok")),
        "error": loaded.get("error", ""),
        "count": len(items),
        "valid_count": len(valid),
        "invalid_count": len(invalid),
        "sample_paths": [x.get("path", "") for x in items[:10]],
    }


def registry_invalid_entries(limit: int = 20) -> List[Dict[str, Any]]:
    items = registry_entries()
    bad = [x for x in items if x.get("valid_json") is False]
    return bad[:limit]


def registry_find(term: str, limit: int = 20) -> List[Dict[str, Any]]:
    t = str(term or "").lower()
    if not t:
        return []
    hits = []
    for item in registry_entries():
        blob = json.dumps(item, ensure_ascii=False).lower()
        if t in blob:
            hits.append(item)
        if len(hits) >= limit:
            break
    return hits

