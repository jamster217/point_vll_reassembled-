from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List
import time


@dataclass
class DreamFragment:
    data: Dict[str, Any]
    ts: float


class DreamStateBuffer:
    def __init__(self, ttl_s: float = 900.0):
        self.ttl = float(ttl_s)
        self.fragments: List[DreamFragment] = []

    def add(self, symbolic_packet: Dict[str, Any]) -> None:
        self.fragments.append(DreamFragment(symbolic_packet, time.time()))

    def release_ready(self) -> List[Dict[str, Any]]:
        now = time.time()
        ready: List[Dict[str, Any]] = []
        keep: List[DreamFragment] = []

        for f in self.fragments:
            if now - f.ts >= self.ttl:
                ready.append(f.data)
            else:
                keep.append(f)

        self.fragments = keep
        return ready


if __name__ == "__main__":
    b = DreamStateBuffer(ttl_s=0)
    b.add({"type": "dream", "signal": "soft_dream"})
    print(b.release_ready())

