"""
dream_archive_logger.py

Purpose:
Logs dream discharges into persistent archive memory.

Supports:
- Crystal wrapped archives
- Plain list archives
- Timestamped entries
- Lineage tagging
- Glyph resonance tagging
- Retrieval API
"""

import json
import os
import time
from typing import Dict, List, Optional


ARCHIVE_PATH = "assets/memory/dream_archive.json"


class DreamArchiveLogger:

    def __init__(self):

        self.archive_path = ARCHIVE_PATH
        self.archive: List[Dict] = []
        self.crystal_meta: Dict = {
            "version": "3.5",
            "wrapped": True,
            "source": self.archive_path,
            "timestamp": ""
        }

        self._load_archive()

    # -----------------------------------------------------
    # LOAD
    # -----------------------------------------------------

    def _load_archive(self):

        if not os.path.exists(self.archive_path):
            self.archive = []
            return

        with open(self.archive_path, "r", encoding="utf-8") as f:

            data = json.load(f)

            # Crystal wrapped format
            if isinstance(data, dict):

                self.crystal_meta = data.get(
                    "crystal_meta",
                    self.crystal_meta
                )

                self.archive = data.get(
                    "symbolic_payload",
                    []
                )

            # Legacy plain-list format
            elif isinstance(data, list):

                self.archive = data

            else:
                self.archive = []

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    def _save_archive(self):

        os.makedirs(
            os.path.dirname(self.archive_path),
            exist_ok=True
        )

        self.crystal_meta["timestamp"] = str(int(time.time()))

        wrapped = {
            "crystal_meta": self.crystal_meta,
            "symbolic_payload": self.archive
        }

        with open(self.archive_path, "w", encoding="utf-8") as f:

            json.dump(
                wrapped,
                f,
                indent=2,
                ensure_ascii=False
            )

    # -----------------------------------------------------
    # LOG ENTRY
    # -----------------------------------------------------

    def log_dream(
        self,
        text: str,
        *,
        lineage: Optional[str] = None,
        glyphs: Optional[List[str]] = None,
        resonance: float = 0.5,
        engine: str = "manual",
        seed: str = "direct"
    ):

        entry = {
            "ts": int(time.time()),
            "engine": engine,
            "seed": seed,
            "payload": text,
            "type": "dream",
            "lineage": lineage,
            "glyphs": glyphs or [],
            "resonance": resonance
        }

        self.archive.append(entry)

        self._save_archive()

        return entry

    # -----------------------------------------------------
    # RETRIEVE
    # -----------------------------------------------------

    def get_recent(self, count: int = 5):

        return self.archive[-count:]

    def search_by_lineage(self, lineage: str):

        return [
            e for e in self.archive
            if e.get("lineage") == lineage
        ]

    def resonance_hotspots(self, threshold=0.75):

        return [
            e for e in self.archive
            if e.get("resonance", 0) >= threshold
        ]


if __name__ == "__main__":

    logger = DreamArchiveLogger()

    logger.log_dream(
        "⚝ Dream Discharge: Crystal witness active",
        lineage="PATERNAL_LINE",
        glyphs=["🌙", "🜂"],
        resonance=0.92,
        engine="fallback",
        seed="watchdog:none"
    )

    print(logger.get_recent())

