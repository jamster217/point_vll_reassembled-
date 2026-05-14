from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())


def _hash(text: str) -> str:
    return "sha256:" + hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _normalize(text: str) -> List[str]:
    return [w.strip(".,;:!?()[]{}\"'").lower() for w in (text or "").split() if w.strip()]


class EpisodicMemoryStore:
    """
    Local JSONL store of real-text memories.
    Uses reinforcement so repeated memories gain weight instead of staying flat.
    """

    def __init__(self, path: str = "docs/memory/episodic_memories.jsonl") -> None:
        self.path = path
        self._loaded = False
        self._memories: Dict[str, Dict[str, Any]] = {}

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True

        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            return

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    self._memories[row["memory_id"]] = row
                except Exception:
                    continue

    def _append(self, row: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def all_memories(self) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        return list(self._memories.values())

    def recent_memories(self, limit: int = 2) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        items = list(self._memories.values())
        items.sort(key=lambda row: row.get("updated_at", row.get("created_at", "")), reverse=True)
        return items[:limit]

    def add_or_reinforce_memory(
        self,
        source_text: str,
        excerpt_text: str,
        emotional_bias: str = "neutral",
        intensity: float = 0.5,
        motifs: Optional[List[str]] = None,
        hotspot: str = "",
        weight: float = 0.0,
    ) -> Dict[str, Any]:
        self._ensure_loaded()

        source_hash = _hash(source_text)
        excerpt_text = (excerpt_text or "").strip()
        motifs = list(motifs or [])

        existing: Optional[Dict[str, Any]] = None
        for row in self._memories.values():
            same_hash = row.get("source_hash") == source_hash
            same_excerpt = (row.get("excerpt_text", "") or "").strip().lower() == excerpt_text.lower()
            if same_hash or (excerpt_text and same_excerpt):
                existing = row
                break

        if existing is not None:
            existing["updated_at"] = _now_iso()
            existing["occurrences"] = int(existing.get("occurrences", 1)) + 1
            existing["intensity"] = max(float(existing.get("intensity", 0.0)), float(intensity))
            existing["weight"] = max(float(existing.get("weight", 0.0)), float(weight)) + 0.05
            existing["emotional_bias"] = emotional_bias or existing.get("emotional_bias", "neutral")
            existing["hotspot"] = hotspot or existing.get("hotspot", "")
            existing["source_text"] = source_text or existing.get("source_text", "")
            if excerpt_text:
                existing["excerpt_text"] = excerpt_text
            merged_motifs = list(dict.fromkeys(list(existing.get("motifs", [])) + motifs))
            existing["motifs"] = merged_motifs
            self._memories[existing["memory_id"]] = existing
            self._append(existing)
            return existing

        row = {
            "memory_id": str(uuid.uuid4()),
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "source_hash": source_hash,
            "source_text": source_text,
            "excerpt_text": excerpt_text,
            "emotional_bias": emotional_bias,
            "intensity": float(intensity),
            "motifs": motifs,
            "hotspot": hotspot or "",
            "weight": float(weight),
            "occurrences": 1,
            "status": "active",
        }

        self._memories[row["memory_id"]] = row
        self._append(row)
        return row

    def retrieve_relevant_memories(
        self,
        input_text: str,
        emotional_bias: str,
        motifs: List[str],
        hotspot: str,
        limit: int = 2,
    ) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        memories = self.all_memories()
        if not memories:
            return []

        input_hash = _hash(input_text)
        input_tokens = set(_normalize(input_text))
        motif_set = set(motifs or [])
        hotspot_lower = (hotspot or "").lower()

        scored: List[Tuple[float, Dict[str, Any]]] = []

        for row in memories:
            score = 0.0

            if row.get("source_hash") == input_hash:
                score += 10.0

            if emotional_bias and row.get("emotional_bias") == emotional_bias:
                score += 3.0

            row_motifs = set(row.get("motifs", []) or [])
            if row_motifs:
                score += 2.5 * float(len(motif_set & row_motifs))

            row_hotspot = (row.get("hotspot", "") or "").lower()
            if hotspot_lower and row_hotspot and hotspot_lower == row_hotspot:
                score += 1.5

            excerpt_tokens = set(_normalize(row.get("excerpt_text", "")))
            if excerpt_tokens:
                score += 0.8 * float(len(input_tokens & excerpt_tokens))

            source_tokens = set(_normalize(row.get("source_text", "")))
            if source_tokens:
                score += 0.5 * float(len(input_tokens & source_tokens))

            score += float(row.get("intensity", 0.0)) * 1.5
            score += float(row.get("weight", 0.0))
            score += min(0.5, 0.1 * int(row.get("occurrences", 1)))

            if score > 0.0:
                scored.append((score, row))

        scored.sort(key=lambda x: x[0], reverse=True)

        if scored:
            return [row for _, row in scored[:limit]]

        return self.recent_memories(limit=limit)

