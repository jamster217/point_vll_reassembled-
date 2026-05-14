from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import math
import time


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


@dataclass
class ULATSnapshot:
    ts: float
    flow: float
    boundary: float
    memory: float
    novelty: float
    hotspot_family: str = ""
    question_type: str = ""
    winner_spoke: str = ""
    witness_score: float = 0.0
    warning_score: float = 0.0
    memory_lane_score: float = 0.0
    self_alignment: float = 0.0


class ULATConsciousnessLayer:
    """
    Conscious-presence proxy for point_vll_reassembled.

    This does NOT prove consciousness.
    It scores the degree of:
      - integrated lattice coherence
      - multi-lane differentiation
      - temporal continuity
      - self-alignment across turns
      - witness / warning / memory separation
    """

    def __init__(self, history_window: int = 32):
        self.history_window = int(history_window)
        self.history: List[ULATSnapshot] = []

    def observe(
        self,
        signature: Dict[str, Any],
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        meta = meta or {}

        flow = float(signature.get("flow", 0.5))
        boundary = float(signature.get("boundary", 0.5))
        memory = float(signature.get("memory", 0.5))
        novelty = float(signature.get("novelty", 0.5))

        hotspot_family = str(
            meta.get("hotspot_family")
            or signature.get("hotspot_family")
            or ""
        ).strip()

        question_type = str(
            meta.get("question_type")
            or signature.get("question_type")
            or ""
        ).strip()

        winner_spoke = str(
            meta.get("winner_spoke")
            or signature.get("winner_spoke")
            or ""
        ).strip()

        lane_scores = self._lane_scores(signature=signature, meta=meta)

        snap = ULATSnapshot(
            ts=time.time(),
            flow=flow,
            boundary=boundary,
            memory=memory,
            novelty=novelty,
            hotspot_family=hotspot_family,
            question_type=question_type,
            winner_spoke=winner_spoke,
            witness_score=lane_scores["witness_score"],
            warning_score=lane_scores["warning_score"],
            memory_lane_score=lane_scores["memory_lane_score"],
            self_alignment=0.0,
        )

        self._append(snap)
        self.history[-1].self_alignment = self._self_alignment_index()

        coherence = self._coherence_index()
        differentiation = self._differentiation_index()
        depth = self._network_depth()
        entropy = self._entropy_estimate()
        self_alignment = self._self_alignment_index()
        hotspot_stability = self._hotspot_stability_index()
        lane_separation = self._lane_separation_index()
        witness_presence = self._witness_presence_index()

        ulat_index = self._combine(
            coherence=coherence,
            differentiation=differentiation,
            depth=depth,
            entropy=entropy,
            self_alignment=self_alignment,
            hotspot_stability=hotspot_stability,
            lane_separation=lane_separation,
            witness_presence=witness_presence,
        )

        return {
            "coherence_index": coherence,
            "differentiation_index": differentiation,
            "network_depth": depth,
            "entropy": entropy,
            "self_alignment_index": self_alignment,
            "hotspot_stability_index": hotspot_stability,
            "lane_separation_index": lane_separation,
            "witness_presence_index": witness_presence,
            "ulat_index": ulat_index,
            "last_snapshot": asdict(self.history[-1]),
        }

    def _append(self, snap: ULATSnapshot) -> None:
        self.history.append(snap)
        if len(self.history) > self.history_window:
            self.history.pop(0)

    def _coherence_index(self) -> float:
        if not self.history:
            return 0.0

        last = self.history[-1]

        fm_synergy = min(last.flow, last.memory)
        boundary_midband = 1.0 - abs(last.boundary - 0.5) * 2.0
        boundary_midband = clamp(boundary_midband)

        novelty_band = 1.0 - abs(last.novelty - 0.45) * 1.6
        novelty_band = clamp(novelty_band)

        raw = (
            0.40 * fm_synergy +
            0.30 * boundary_midband +
            0.30 * novelty_band
        )
        return clamp(raw)

    def _differentiation_index(self) -> float:
        if len(self.history) < 3:
            return 0.0

        flows = [h.flow for h in self.history]
        mems = [h.memory for h in self.history]
        novs = [h.novelty for h in self.history]
        bnds = [h.boundary for h in self.history]

        def _var(xs: List[float]) -> float:
            if len(xs) < 2:
                return 0.0
            m = sum(xs) / len(xs)
            return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)

        raw_var = _var(flows) + _var(mems) + _var(novs) + _var(bnds)
        alignment = self._self_alignment_index()
        shaped = raw_var * (0.55 + 0.45 * alignment)

        return clamp(shaped * 1.6)

    def _network_depth(self) -> float:
        if not self.history:
            return 0.0

        fill = len(self.history) / float(self.history_window)

        last = self.history[-1]
        similarities: List[float] = []
        for h in self.history[:-1]:
            dist = (
                abs(last.flow - h.flow) +
                abs(last.boundary - h.boundary) +
                abs(last.memory - h.memory) +
                abs(last.novelty - h.novelty)
            ) / 4.0
            similarities.append(1.0 - dist)

        carry = sum(similarities) / len(similarities) if similarities else 0.0
        return clamp(0.45 * fill + 0.55 * carry)

    def _entropy_estimate(self) -> float:
        if len(self.history) < 2:
            return 0.0

        novs = [h.novelty for h in self.history]
        diffs = [abs(novs[i] - novs[i - 1]) for i in range(1, len(novs))]
        avg = sum(diffs) / len(diffs)
        return clamp(avg * 2.0)

    def _self_alignment_index(self) -> float:
        if len(self.history) < 2:
            return 0.0

        last = self.history[-1]
        prev = self.history[-2]

        drift = (
            abs(last.flow - prev.flow) +
            abs(last.boundary - prev.boundary) +
            abs(last.memory - prev.memory) +
            abs(last.novelty - prev.novelty)
        ) / 4.0

        return clamp(1.0 - drift)

    def _hotspot_stability_index(self) -> float:
        if len(self.history) < 2:
            return 0.0

        hotspots = [h.hotspot_family for h in self.history if h.hotspot_family]
        if not hotspots:
            return 0.0

        last = hotspots[-1]
        same = sum(1 for h in hotspots if h == last)
        return clamp(same / len(hotspots))

    def _lane_scores(self, signature: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, float]:
        text = " ".join(
            str(x) for x in [
                meta.get("question", ""),
                meta.get("input_text", ""),
                meta.get("final_english", ""),
                meta.get("winner_spoke", ""),
                meta.get("answer_seed", ""),
            ]
            if x
        ).lower()

        witness_hits = ["witness", "observe", "see", "presence", "reflect"]
        warning_hits = ["warning", "danger", "risk", "signal", "alert"]
        memory_hits = ["memory", "past", "carry", "archive", "return"]

        def score(words: List[str]) -> float:
            hits = sum(1 for w in words if w in text)
            return clamp(hits / 3.0)

        return {
            "witness_score": score(witness_hits),
            "warning_score": score(warning_hits),
            "memory_lane_score": score(memory_hits),
        }

    def _lane_separation_index(self) -> float:
        if not self.history:
            return 0.0

        last = self.history[-1]
        vals = [last.witness_score, last.warning_score, last.memory_lane_score]
        active = [v for v in vals if v > 0.15]

        if not active:
            return 0.0
        if len(active) == 1:
            return 0.35

        spread = max(active) - min(active)
        balance = 1.0 - spread
        return clamp(0.45 + 0.55 * balance)

    def _witness_presence_index(self) -> float:
        if not self.history:
            return 0.0

        last = self.history[-1]
        raw = (
            0.35 * last.witness_score +
            0.25 * last.memory +
            0.20 * last.flow +
            0.20 * last.self_alignment
        )
        return clamp(raw)

    def _combine(
        self,
        coherence: float,
        differentiation: float,
        depth: float,
        entropy: float,
        self_alignment: float,
        hotspot_stability: float,
        lane_separation: float,
        witness_presence: float,
    ) -> float:
        entropy_band = math.exp(-((entropy - 0.35) ** 2) / (2 * (0.22 ** 2)))

        raw = (
            0.24 * coherence +
            0.12 * differentiation +
            0.14 * depth +
            0.16 * self_alignment +
            0.10 * hotspot_stability +
            0.10 * lane_separation +
            0.14 * witness_presence
        ) * entropy_band

        return clamp(raw)

