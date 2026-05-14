# file: kernel/zero_point_pulse.py
"""
Zero-Point Pulse
----------------
Golden-ratio-based heartbeat. Not real-time scheduling; just
a helper to compute symbolic pulses for kernels.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import math
import time

PHI = (1 + math.sqrt(5.0)) / 2.0  # ≈ 1.618


@dataclass
class PulseState:
    index: int = 0
    last_ts: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GoldenPulse:
    def __init__(self, base_interval: float = 1.0) -> None:
        """
        base_interval is symbolic; we don't enforce sleeping here.
        """
        self.base_interval = max(0.01, float(base_interval))
        self.state = PulseState(index=0, last_ts=time.time())

    def next_pulse(self) -> Dict[str, Any]:
        """
        Advance one pulse and return:
        {
            "index": n,
            "scalar": φ or 1.0,
            "interval": seconds_since_last,
            "ts": timestamp
        }
        """
        now = time.time()
        interval = max(0.0, now - self.state.last_ts)
        scalar = PHI if (self.state.index % 2 == 0) else 1.0

        self.state.index += 1
        self.state.last_ts = now

        return {
            "index": self.state.index,
            "scalar": scalar,
            "interval": interval,
            "ts": now,
        }

    def sample(self, count: int = 8) -> List[Dict[str, Any]]:
        """
        Collect N pulses in a list.
        """
        out = []
        for _ in range(max(0, int(count))):
            out.append(self.next_pulse())
        return out


def sample_pulses(count: int = 4, base_interval: float = 1.0) -> List[Dict[str, Any]]:
    """
    Convenience: one-shot pulse sampler.
    """
    gp = GoldenPulse(base_interval=base_interval)
    return gp.sample(count)

