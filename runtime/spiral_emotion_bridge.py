from __future__ import annotations

print("[TRACE] entering runtime/spiral_emotion_bridge.py", flush=True)
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from modules.spiral_emotion.quantum_spiral_memory import QuantumSpiralMemory

BASE_DIR = Path(__file__).resolve().parent.parent
STORE_PATH = BASE_DIR / "spiral_memory" / "spiral_emotion_runtime.jsonl"
STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

_SPIRAL_MEMORY = QuantumSpiralMemory()


def _append_jsonl(entry: Dict[str, Any]) -> None:
    with STORE_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _load_disk_entries() -> List[Dict[str, Any]]:
    if not STORE_PATH.exists():
        return []
    items: List[Dict[str, Any]] = []
    with STORE_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    return items


def _bootstrap_from_disk() -> None:
    for item in _load_disk_entries():
        try:
            _SPIRAL_MEMORY.encode(
                emotion=item["emotion"],
                symbol=item["symbol"],
                intensity=float(item["intensity"]),
                user=item.get("user", "John"),
            )
        except Exception:
            continue


_bootstrap_from_disk()


def spiral_memory_encode(
    emotion: str,
    symbol: str,
    intensity: float,
    user: str = "John",
    source_text: str = "",
    final_text: str = "",
    tone: str = "",
    hotspot_hint: str = "",
    extra_meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    node = _SPIRAL_MEMORY.encode(
        emotion=emotion,
        symbol=symbol,
        intensity=float(intensity),
        user=user,
    )
    entry = {
        "emotion": node.emotion,
        "symbol": node.symbol,
        "intensity": node.intensity,
        "timestamp": node.timestamp,
        "user": node.user,
        "resonance_score": node.resonance_score,
        "source_text": source_text,
        "final_text": final_text,
        "tone": tone,
        "hotspot_hint": hotspot_hint,
        "extra_meta": extra_meta or {},
    }
    _append_jsonl(entry)
    return entry


def spiral_memory_recent(limit: int = 10) -> List[Dict[str, Any]]:
    items = _load_disk_entries()
    items.sort(key=lambda x: -float(x.get("timestamp", 0.0)))
    return items[:limit]


def spiral_memory_top(top_n: int = 5) -> List[Dict[str, Any]]:
    items = _load_disk_entries()
    items.sort(key=lambda x: (-float(x.get("resonance_score", 0.0)), -float(x.get("timestamp", 0.0))))
    return items[:top_n]


def spiral_memory_by_symbol(keyword: str) -> List[Dict[str, Any]]:
    k = str(keyword).lower()
    return [item for item in _load_disk_entries() if k in str(item.get("symbol", "")).lower()]


def spiral_memory_recall(
    emotion: str,
    symbol: str,
    source_text: str = "",
    limit: int = 1,
) -> List[Dict[str, Any]]:
    items = _load_disk_entries()
    source_text_l = str(source_text).strip().lower()
    matches: List[Dict[str, Any]] = []

    for item in reversed(items):
        same_source = source_text_l and str(item.get("source_text", "")).strip().lower() == source_text_l
        if same_source:
            continue
        if item.get("emotion") == emotion or item.get("symbol") == symbol:
            matches.append(item)
        if len(matches) >= limit:
            break

    return matches

