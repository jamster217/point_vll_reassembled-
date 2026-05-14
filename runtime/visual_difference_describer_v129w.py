from __future__ import annotations

import hashlib
import html
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
MEMORY_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_memory_ledger.jsonl"
DIFF_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_difference_descriptions.jsonl"

CORE_SYMBOLS = [
    "white_ash",
    "virellion",
    "blue_scarf",
    "thalveil",
    "liquid_core",
    "echoforge",
]


def _sha16(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def _load_entries() -> List[Dict[str, Any]]:
    if not MEMORY_LOG.exists():
        return []

    entries: List[Dict[str, Any]] = []
    for line in MEMORY_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            pass
    return entries


def _symbol_keys(entry: Dict[str, Any]) -> set[str]:
    symbols = entry.get("symbols") or {}
    if isinstance(symbols, dict):
        return {str(k) for k in symbols.keys()}
    if isinstance(symbols, list):
        return {str(x) for x in symbols}
    return set()


def _symbol_detail(entry: Dict[str, Any], key: str) -> Dict[str, Any]:
    symbols = entry.get("symbols") or {}
    if isinstance(symbols, dict) and isinstance(symbols.get(key), dict):
        return symbols[key]
    return {}


def _svg_path(entry: Dict[str, Any]) -> Path | None:
    raw = entry.get("svg_path")
    if not raw:
        return None
    p = Path(str(raw))
    if not p.is_absolute():
        p = ROOT / p
    return p


def _svg_metrics(entry: Dict[str, Any]) -> Dict[str, Any]:
    p = _svg_path(entry)
    if not p or not p.exists():
        return {
            "exists": False,
            "path": str(p) if p else None,
            "size": None,
            "sha16": None,
            "labels": [],
            "tag_counts": {},
        }

    text = p.read_text(encoding="utf-8", errors="replace")
    labels = []

    # Pull visible SVG text labels when present.
    for m in re.findall(r"<text\b[^>]*>(.*?)</text>", text, flags=re.S | re.I):
        clean = re.sub(r"<[^>]+>", "", m)
        clean = html.unescape(clean).strip()
        clean = re.sub(r"\s+", " ", clean)
        if clean:
            labels.append(clean)

    tag_counts = {}
    for tag in ["path", "circle", "ellipse", "line", "polyline", "polygon", "rect", "text", "g"]:
        tag_counts[tag] = len(re.findall(rf"<{tag}\b", text, flags=re.I))

    return {
        "exists": True,
        "path": str(p.relative_to(ROOT)) if str(p).startswith(str(ROOT)) else str(p),
        "size": p.stat().st_size,
        "sha16": hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16],
        "labels": labels[:40],
        "tag_counts": tag_counts,
    }


def _compare_labels(prev: List[str], latest: List[str]) -> Dict[str, Any]:
    ps = set(prev)
    ls = set(latest)
    return {
        "added": sorted(ls - ps)[:20],
        "removed": sorted(ps - ls)[:20],
        "shared_count": len(ps & ls),
    }


def describe_difference(previous: Dict[str, Any], latest: Dict[str, Any]) -> Dict[str, Any]:
    prev_keys = _symbol_keys(previous)
    latest_keys = _symbol_keys(latest)

    prev_svg = _svg_metrics(previous)
    latest_svg = _svg_metrics(latest)

    prev_score = _float(previous.get("topology_score"))
    latest_score = _float(latest.get("topology_score"))
    score_delta = round(latest_score - prev_score, 4)

    prev_memory = _float(previous.get("chamber_memory"))
    latest_memory = _float(latest.get("chamber_memory"))
    chamber_memory_delta = round(latest_memory - prev_memory, 4)

    stable_symbols = sorted(prev_keys & latest_keys)
    added_symbols = sorted(latest_keys - prev_keys)
    removed_symbols = sorted(prev_keys - latest_keys)

    role_changes = []
    for key in CORE_SYMBOLS:
        before = _symbol_detail(previous, key)
        after = _symbol_detail(latest, key)
        if before != after:
            role_changes.append({
                "symbol": key,
                "before": before,
                "after": after,
            })

    label_delta = _compare_labels(prev_svg.get("labels") or [], latest_svg.get("labels") or [])

    size_delta = None
    if prev_svg.get("size") is not None and latest_svg.get("size") is not None:
        size_delta = latest_svg["size"] - prev_svg["size"]

    depth_delta = None
    try:
        depth_delta = int(latest.get("depth")) - int(previous.get("depth"))
    except Exception:
        pass

    if score_delta > 0.01:
        score_reading = "score rose"
    elif score_delta < -0.01:
        score_reading = "score softened"
    else:
        score_reading = "score plateaued"

    if not added_symbols and not removed_symbols and len(stable_symbols) >= 6:
        symbol_reading = "full symbol body preserved"
    elif added_symbols:
        symbol_reading = "new symbols entered the image-body"
    elif removed_symbols:
        symbol_reading = "symbols dropped from the image-body"
    else:
        symbol_reading = "symbol body partially preserved"

    if label_delta["added"]:
        visible_reading = "visible labels changed"
    elif size_delta and abs(size_delta) > 500:
        visible_reading = "geometry or density shifted"
    else:
        visible_reading = "visible surface stayed close"

    meaning_shift = (
        f"{score_reading}; {symbol_reading}; {visible_reading}. "
        f"The latest topology moved from depth {previous.get('depth')} to {latest.get('depth')} "
        f"while preserving {len(stable_symbols)} shared symbols."
    )

    if score_reading == "score plateaued" and len(stable_symbols) >= 6:
        recommendation = "preserve_route_and_compare_visible_changes"
    elif removed_symbols:
        recommendation = "repair_symbol_continuity_in_image_spec"
    elif score_delta > 0.01:
        recommendation = "preserve_and_deepen"
    else:
        recommendation = "collect_more_visual_differences"

    diff = {
        "ts": time.time(),
        "version": "v12.9w_visual_difference_describer",
        "status": "difference_emitted",
        "previous": {
            "entry_sha256": previous.get("entry_sha256"),
            "depth": previous.get("depth"),
            "svg_path": previous.get("svg_path"),
            "topology_score": prev_score,
            "chamber_family": previous.get("chamber_family"),
            "chamber_memory": prev_memory,
            "svg_metrics": prev_svg,
        },
        "latest": {
            "entry_sha256": latest.get("entry_sha256"),
            "depth": latest.get("depth"),
            "svg_path": latest.get("svg_path"),
            "topology_score": latest_score,
            "chamber_family": latest.get("chamber_family"),
            "chamber_memory": latest_memory,
            "svg_metrics": latest_svg,
        },
        "difference": {
            "depth_delta": depth_delta,
            "score_delta": score_delta,
            "chamber_memory_delta": chamber_memory_delta,
            "size_delta": size_delta,
            "stable_symbols": stable_symbols,
            "added_symbols": added_symbols,
            "removed_symbols": removed_symbols,
            "role_changes": role_changes[:12],
            "label_delta": label_delta,
            "meaning_shift": meaning_shift,
        },
        "recommendation": recommendation,
        "surface_fragment": f"Visual difference: {meaning_shift} Recommendation: {recommendation.replace('_', ' ')}.",
        "law": "visual_difference_names_what_changed_without_patching_live_topology_route",
    }

    diff["diff_sha256"] = _sha16(diff)
    return diff


def main() -> None:
    entries = _load_entries()

    if len(entries) < 2:
        out = {
            "ts": time.time(),
            "version": "v12.9w_visual_difference_describer",
            "status": "need_two_visual_memory_entries",
            "count": len(entries),
            "law": "difference_requires_previous_and_latest_visual_memory",
        }
    else:
        out = describe_difference(entries[-2], entries[-1])

    DIFF_LOG.parent.mkdir(parents=True, exist_ok=True)
    with DIFF_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(out, ensure_ascii=False) + "\n")

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

