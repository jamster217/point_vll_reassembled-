from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SelfCorrectionDecision:
    triggered: bool
    mode: Optional[str]
    tension_reset: Optional[float]
    reason: str
    ratio: float
    streak: int


class SelfCorrectionKernel:
    def __init__(
        self,
        ratio_threshold: float = 0.60,
        required_streak: int = 2,
        tension_reset: float = 0.40,
        trigger_mode: str = "slow_vivid",
    ) -> None:
        self.ratio_threshold = float(ratio_threshold)
        self.required_streak = int(required_streak)
        self.tension_reset = float(tension_reset)
        self.trigger_mode = trigger_mode
        self._low_streak = 0

    def observe(self, coherence_score: float, directness_score: float) -> SelfCorrectionDecision:
        d = max(float(directness_score), 0.01)
        c = max(float(coherence_score), 0.0)
        ratio = d / max(c, 0.01)

        if ratio < self.ratio_threshold:
            self._low_streak += 1
        else:
            self._low_streak = 0

        if self._low_streak >= self.required_streak:
            return SelfCorrectionDecision(
                triggered=True,
                mode=self.trigger_mode,
                tension_reset=self.tension_reset,
                reason=f"coherence/directness ratio {ratio:.3f} < {self.ratio_threshold} for {self._low_streak} turns",
                ratio=ratio,
                streak=self._low_streak,
            )

        return SelfCorrectionDecision(
            triggered=False,
            mode=None,
            tension_reset=None,
            reason=f"ratio {ratio:.3f}, streak {self._low_streak}",
            ratio=ratio,
            streak=self._low_streak,
        )

