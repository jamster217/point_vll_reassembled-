#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


LOG_PATH = Path("logs/sge_turns.jsonl")


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_timestamp(entry: dict[str, Any], fallback_index: int) -> str:
    for key in ("timestamp", "created_at", "generated_at", "time"):
        raw = entry.get(key)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return f"turn-{fallback_index:04d}"


def _extract_family(entry: dict[str, Any]) -> str:
    role_block = entry.get("crystal_family_role") or {}
    if isinstance(role_block, dict):
        family = role_block.get("family")
        if isinstance(family, str) and family.strip():
            return family.strip()

    for key in ("shape_signature_in", "shape_signature_out", "shape_signature"):
        sig = entry.get(key)
        if isinstance(sig, str) and "|" in sig:
            return sig.split("|", 1)[0].strip()

    shape_in = entry.get("shape_in") or {}
    if isinstance(shape_in, dict):
        keywords = shape_in.get("keywords") or []
        if isinstance(keywords, list) and keywords:
            first = keywords[0]
            if isinstance(first, str) and first.strip():
                return first.strip()

    return "unknown"


def _extract_role(entry: dict[str, Any]) -> str:
    role_block = entry.get("crystal_family_role") or {}
    if isinstance(role_block, dict):
        role = role_block.get("role")
        if isinstance(role, str) and role.strip():
            return role.strip()
    return "unknown"


def _extract_stability(entry: dict[str, Any]) -> float:
    if "signature_stability" in entry:
        return _to_float(entry.get("signature_stability"), 0.0)

    role_block = entry.get("crystal_family_role") or {}
    if isinstance(role_block, dict) and "stability" in role_block:
        return _to_float(role_block.get("stability"), 0.0)

    crystal_index = entry.get("crystal_index") or {}
    if isinstance(crystal_index, dict):
        families = crystal_index.get("families") or []
        if isinstance(families, list):
            target_family = _extract_family(entry)
            for fam in families:
                if isinstance(fam, dict) and fam.get("family") == target_family:
                    return _to_float(fam.get("stability"), 0.0)

    return 0.0


def _extract_release_delta(entry: dict[str, Any]) -> float:
    delta = entry.get("shape_delta") or {}
    if isinstance(delta, dict):
        return _to_float(delta.get("release"), 0.0)
    return 0.0


def load_turns(path: Path = LOG_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            family = _extract_family(entry)
            role = _extract_role(entry)
            stability = _extract_stability(entry)
            release_delta = _extract_release_delta(entry)

            row = {
                "turn_index": idx,
                "timestamp": _parse_timestamp(entry, idx),
                "prompt": entry.get("prompt", ""),
                "family": family,
                "role": role,
                "stability": stability,
                "release_delta": release_delta,
            }
            rows.append(row)

    return rows


def apply_release_zscore(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    family_values: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        family_values[row["family"]].append(row["release_delta"])

    stats_map: dict[str, tuple[float, float]] = {}
    for family, values in family_values.items():
        mean = statistics.fmean(values) if values else 0.0
        stdev = statistics.pstdev(values) if len(values) > 1 else 0.0
        stats_map[family] = (mean, stdev)

    enriched: list[dict[str, Any]] = []
    for row in rows:
        mean, stdev = stats_map[row["family"]]
        if stdev == 0:
            z = 0.0
        else:
            z = (row["release_delta"] - mean) / stdev

        item = dict(row)
        item["release_z"] = z
        item["family_release_mean"] = mean
        item["family_release_stdev"] = stdev
        enriched.append(item)

    return enriched


def build_timeline_window(path: Path = LOG_PATH, last_n: int = 40) -> dict[str, Any]:
    rows = load_turns(path)
    if last_n > 0:
        rows = rows[-last_n:]

    rows = apply_release_zscore(rows)

    families = Counter(row["family"] for row in rows)
    roles = Counter(row["role"] for row in rows)

    avg_stability = statistics.fmean([r["stability"] for r in rows]) if rows else 0.0
    avg_release = statistics.fmean([r["release_delta"] for r in rows]) if rows else 0.0

    return {
        "source": str(path),
        "turn_count": len(rows),
        "avg_stability": avg_stability,
        "avg_release_delta": avg_release,
        "families": dict(families),
        "roles": dict(roles),
        "rows": rows,
    }


def main() -> None:
    data = build_timeline_window()
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()

