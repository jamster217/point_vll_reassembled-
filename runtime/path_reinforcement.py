from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class PathStats:
    count: int
    boost: float


class PathReinforcement:
    """
    Reinforce frequently successful translation paths.
    path_id example: "glyph:fear|phenome:TH|style:direct"
    """

    def __init__(
        self,
        path: str = "runtime/path_weights.json",
        per_hit_boost: float = 0.03,
        boost_cap: float = 0.12,
    ) -> None:
        self.path = path
        self.per_hit_boost = float(per_hit_boost)
        self.boost_cap = float(boost_cap)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def increment(self, path_id: str) -> PathStats:
        data = self._load()
        entry = data.get(path_id, {"count": 0})
        entry["count"] = int(entry.get("count", 0)) + 1
        data[path_id] = entry
        self._save(data)
        boost = min(entry["count"] * self.per_hit_boost, self.boost_cap)
        return PathStats(count=entry["count"], boost=boost)

    def get_boost(self, path_id: str) -> Tuple[float, Dict]:
        data = self._load()
        entry = data.get(path_id)
        if not entry:
            return 0.0, {"count": 0, "boost": 0.0}
        count = int(entry.get("count", 0))
        boost = min(count * self.per_hit_boost, self.boost_cap)
        return boost, {"count": count, "boost": boost}

    def _load(self) -> Dict:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: Dict) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

