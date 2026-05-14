from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

INDEX_PATH = Path("logs/crystal_family_index.json")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_index() -> Dict[str, Any]:
    if not INDEX_PATH.exists():
        return {
            "generated_at": _now(),
            "family_count": 0,
            "families": [],
        }

    try:
        data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("index root is not dict")
    except Exception:
        data = {
            "generated_at": _now(),
            "family_count": 0,
            "families": [],
            "recovered_from_invalid_index": True,
        }

    data.setdefault("families", [])
    if not isinstance(data["families"], list):
        data["families"] = []

    return data


def _family_key(item: Dict[str, Any]) -> str:
    family = str(item.get("family", "unknown") or "unknown")
    role = str(item.get("role", "unknown") or "unknown")
    return f"{family}|{role}"


def _release_delta(signature: Dict[str, Any]) -> float:
    target = signature.get("target_transformation", {}) or {}
    try:
        return float(target.get("target_release_delta", 0.0) or 0.0)
    except Exception:
        return 0.0


def _stability(turns: int, role: str) -> float:
    if turns >= 4:
        return 1.0
    if role == "transformative_opener" and turns >= 2:
        return 0.875
    if turns >= 2:
        return 0.875
    return 0.5


def register_essence_signature(signature: Dict[str, Any], source: str = "essence_signature") -> Dict[str, Any]:
    sig = dict(signature or {})
    family = str(sig.get("family", "unknown") or "unknown")
    role = str(sig.get("role", "unknown") or "unknown")

    if family == "unknown":
        return {
            "ok": False,
            "reason": "missing_family",
            "index_path": str(INDEX_PATH),
        }

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = _load_index()

    families: List[Dict[str, Any]] = []
    seen = {}

    for raw in data.get("families", []):
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        key = _family_key(item)
        if key not in seen:
            seen[key] = item
            families.append(item)

    key = f"{family}|{role}"
    release_delta = _release_delta(sig)

    if key in seen:
        item = seen[key]
        item["turns"] = int(item.get("turns", 0) or 0) + 1
        item["last_seen"] = _now()
        item["release_delta"] = round(max(float(item.get("release_delta", 0.0) or 0.0), release_delta), 4)
        item["stability"] = round(_stability(int(item.get("turns", 1) or 1), role), 3)
    else:
        item = {
            "family": family,
            "role": role,
            "turns": 1,
            "stability": round(_stability(1, role), 3),
            "release_delta": round(release_delta, 4),
            "first_seen": _now(),
            "last_seen": _now(),
        }
        families.append(item)
        seen[key] = item

    item["essence_key"] = sig.get("essence_key", "")
    item["relation"] = sig.get("relation", "")
    item["persistence"] = sig.get("persistence", "")
    item["valence"] = sig.get("valence", "")
    item["time_direction"] = sig.get("time_direction", "")
    item["clause_type"] = sig.get("clause_type", "")
    item["source"] = source

    data["families"] = families
    data["family_count"] = len(families)
    data["generated_at"] = _now()
    data["updated_by"] = "runtime.essence_family_index_bridge"

    INDEX_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "family": family,
        "role": role,
        "turns": item.get("turns"),
        "stability": item.get("stability"),
        "release_delta": item.get("release_delta"),
        "index_path": str(INDEX_PATH),
    }


__all__ = ["register_essence_signature"]

