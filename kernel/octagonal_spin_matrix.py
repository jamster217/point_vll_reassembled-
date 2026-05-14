# file: kernel/octagonal_spin_matrix.py
"""
Octagonal Spin Matrix
---------------------
Simple 8-phase state machine used as a "spin lattice" for vectors.

Phase indices 0..7 map to 0°, 45°, …, 315°. This is symbolic rotation:
we use deterministic permutations / sign flips instead of heavy math.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import time


@dataclass
class OctagonalState:
    phase_index: int = 0         # 0..7
    loop_count: int = 0
    updated_at: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class OctagonalSpinMatrix:
    def __init__(self) -> None:
        self.state = OctagonalState(
            phase_index=0,
            loop_count=0,
            updated_at=time.time(),
        )

    # ------------------------------------------------------------------
    # Phase management
    # ------------------------------------------------------------------

    @property
    def phase(self) -> int:
        return self.state.phase_index

    @property
    def degrees(self) -> float:
        return float(self.state.phase_index * 45.0)

    def step(self, n: int = 1) -> None:
        """
        Advance N phases forward (can be negative).
        Increments loop_count whenever we wrap past 7 → 0.
        """
        n = int(n)
        if n == 0:
            return
        before = self.state.phase_index
        self.state.phase_index = (self.state.phase_index + n) % 8
        if n > 0 and self.state.phase_index < before:
            self.state.loop_count += 1
        self.state.updated_at = time.time()

    def set_phase(self, idx: int) -> None:
        self.state.phase_index = int(idx) % 8
        self.state.updated_at = time.time()

    # ------------------------------------------------------------------
    # Vector projection
    # ------------------------------------------------------------------

    def project(self, vec: List[float]) -> List[float]:
        """
        Symbolic 'rotation' of a vector based on phase.

        - phase 0: identity
        - phase 1,3,5,7: cyclic permutations
        - phase 2,6: reversed
        - phase 4: sign flip
        """
        if not vec:
            return []
        d = len(vec)
        p = self.state.phase_index

        if p == 0:
            return list(vec)
        if p in (1, 3, 5, 7):
            shift = p % d
            return [vec[(i - shift) % d] for i in range(d)]
        if p in (2, 6):
            return list(reversed(vec))
        if p == 4:
            return [-x for x in vec]
        return list(vec)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        return {
            "phase_index": self.state.phase_index,
            "degrees": self.degrees,
            "loop_count": self.state.loop_count,
            "updated_at": self.state.updated_at,
        }

    def load_snapshot(self, data: Dict[str, Any]) -> None:
        try:
            self.state.phase_index = int(data.get("phase_index", 0)) % 8
            self.state.loop_count = int(data.get("loop_count", 0))
            self.state.updated_at = float(data.get("updated_at", time.time()))
        except Exception:
            # keep previous state if bad data
            pass

