from __future__ import annotations

"""
still_turn_scheduler.py – Le'Veon Runtime Extension

Fractal Still-Turn Scheduler (FSTS)

This module adds an adaptive, phi-ratio-based pause cadence into Le'Veon's
organ_spine loop. It measures human + system response latency and schedules
"still turns"—micro-pauses where the lattice can re-index, reconcile memory,
and run harmonic recalibration passes.
"""

import math
import time
import logging
from collections import deque
from typing import Callable, Deque, List, Optional


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

auto_callbacks: List[Callable[[], None]] = []


def register_still_turn_callback(func: Callable[[], None]) -> None:
    """Public API for other modules to register still-turn work."""
    auto_callbacks.append(func)


class FractalStillTurnScheduler:
    """Adaptive still-turn scheduler using golden-ratio spacing."""

    PHI: float = (1 + 5 ** 0.5) / 2

    def __init__(self, window: int = 32, still_turn_factor: float = 1.0) -> None:
        self.window: int = window
        self.latencies: Deque[float] = deque(maxlen=window)
        self.ewma_latency: Optional[float] = None
        self.still_turn_factor = still_turn_factor
        self._next_phi_multiple: int = 1
        self._turn_index: int = 0

    def record_turn(self, duration: float) -> None:
        """Record the latency of the last turn."""
        self.latencies.append(duration)
        if self.ewma_latency is None:
            self.ewma_latency = duration
        else:
            alpha = 2 / (len(self.latencies) + 1)
            self.ewma_latency = alpha * duration + (1 - alpha) * self.ewma_latency
        self._turn_index += 1
        logger.debug(
            "Turn %d recorded (%.3fs) EWMA %.3fs",
            self._turn_index,
            duration,
            self.ewma_latency,
        )

    def should_run_still_turn(self) -> bool:
        """Return True if this turn should be a still turn."""
        if self.ewma_latency is None:
            return False

        phi_turn = math.floor(self.PHI * self._next_phi_multiple * self.still_turn_factor)
        phi_turn = max(1, phi_turn)

        if self._turn_index >= phi_turn:
            self._next_phi_multiple += 1
            logger.debug(
                "Still turn triggered at index %d (phi multiple %d)",
                self._turn_index,
                self._next_phi_multiple - 1,
            )
            return True
        return False

    def run_still_turn(self) -> None:
        """Execute all registered still-turn callbacks."""
        start_time = time.perf_counter()
        logger.info("Still turn start (#%d)", self._turn_index)

        for cb in auto_callbacks:
            try:
                cb()
            except Exception as exc:
                name = getattr(cb, "__name__", repr(cb))
                logger.exception("Error in still-turn callback %s: %s", name, exc)

        elapsed = time.perf_counter() - start_time
        logger.info("Still turn complete in %.3fs", elapsed)

    @classmethod
    def patch_organ_spine(cls) -> "FractalStillTurnScheduler":
        """Monkey-patch runtime.organ_spine._run_spine to inject still-turn logic."""
        from importlib import import_module

        organ_spine = import_module("runtime.organ_spine")
        original_run_spine = organ_spine._run_spine
        scheduler = cls()

        def _patched_run_spine(*args, **kwargs):
            turn_start = time.monotonic()
            result = original_run_spine(*args, **kwargs)
            scheduler.record_turn(time.monotonic() - turn_start)
            if scheduler.should_run_still_turn():
                scheduler.run_still_turn()
            return result

        organ_spine._run_spine = _patched_run_spine
        logger.info("FractalStillTurnScheduler patched into runtime.organ_spine._run_spine")
        return scheduler

