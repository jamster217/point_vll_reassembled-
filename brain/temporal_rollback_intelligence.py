from __future__ import annotations

"""
Temporal Rollback Intelligence (TRI)
===================================

Purpose:
- Detect instability across multiple turns (not just within one response)
- Roll back policy/identity knobs to the last stable state
- Provide a 'future echo' corrective mechanism:
  If this path increases contradiction/drift probability, revert.

What TRI does:
- Maintains a rolling window of TurnRecords
- Computes instability metrics:
  - contradiction likelihood (heuristic)
  - drift (style fingerprint change)
  - hype pressure (absolutes / grandiosity markers)
  - risk pressure (sensitive domain markers)
- If instability exceeds threshold:
  - rollback policy knobs:
    restraint ↑, novelty ↓, conflict_alpha ↑, verbosity_target ↓ slightly
  - sets a cooldown to prevent oscillation

What TRI does NOT:
- Execute code
- Make network calls
- Claim consciousness
- Expose chain-of-thought
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import time
import hashlib


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _now() -> float:
    return time.time()


def _hash_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _clamp01(x: float) -> float:
    try:
        x = float(x)
    except Exception:
        x = 0.0
    return max(0.0, min(1.0, x))


# ------------------------------------------------------------
# Data Models
# ------------------------------------------------------------

@dataclass
class PolicyKnobs:
    """
    The knobs TRI is allowed to rollback/tune.
    Keep these aligned with your identity profile / lattice config.
    """
    restraint: float = 0.80
    novelty_bias: float = 0.35
    conflict_alpha: float = 0.65
    verbosity_target: int = 760

    def copy(self) -> "PolicyKnobs":
        return PolicyKnobs(
            restraint=float(self.restraint),
            novelty_bias=float(self.novelty_bias),
            conflict_alpha=float(self.conflict_alpha),
            verbosity_target=int(self.verbosity_target),
        )


@dataclass
class TurnRecord:
    ts: float
    user_text: str
    final_text: str
    phase: str
    risk: float
    novelty: float
    style_fp: str
    contradiction_score: float
    drift_score: float
    hype_score: float
    instability: float


@dataclass
class TRIResult:
    ok: bool
    rolled_back: bool
    reason: str
    instability: float
    turn_instability: float
    knobs_before: PolicyKnobs
    knobs_after: PolicyKnobs
    symbolic: Dict[str, Any] = field(default_factory=dict)
    audit: Dict[str, Any] = field(default_factory=dict)


# ------------------------------------------------------------
# TRI Core
# ------------------------------------------------------------

class TemporalRollbackIntelligence:
    def __init__(
        self,
        *,
        window_size: int = 8,
        instability_threshold: float = 0.62,
        cooldown_s: float = 90.0,
    ) -> None:
        self.window_size = max(4, int(window_size))
        self.instability_threshold = float(instability_threshold)
        self.cooldown_s = float(cooldown_s)

        self._history: List[TurnRecord] = []
        self._last_rollback_ts: float = 0.0

        # Last stable snapshot
        self._last_stable_knobs: PolicyKnobs = PolicyKnobs()
        self._last_stable_ts: float = 0.0

        # Current live knobs
        self.knobs: PolicyKnobs = PolicyKnobs()

    # -------------------------
    # Public API
    # -------------------------

    def observe_turn(
        self,
        *,
        user_text: str,
        final_text: str,
        phase: str,
        risk: float,
        novelty: float,
        current_knobs: Optional[PolicyKnobs] = None,
        debug: bool = False,
    ) -> TRIResult:
        """
        Observe a completed turn and decide whether to rollback knobs.

        Recommended use:
        - call after draft/final output selection
        - feed resulting knobs into the next turn
        """
        if current_knobs is not None:
            self.knobs = current_knobs.copy()

        knobs_before = self.knobs.copy()

        turn_instability = self._compute_turn_instability(
            user_text=user_text,
            final_text=final_text,
            phase=phase,
            risk=risk,
            novelty=novelty,
        )

        window_instability = self._window_instability()

        if self._cooldown_active():
            return TRIResult(
                ok=True,
                rolled_back=False,
                reason="cooldown_active",
                instability=window_instability,
                turn_instability=turn_instability,
                knobs_before=knobs_before,
                knobs_after=self.knobs.copy(),
                symbolic=self._build_symbolic(window_instability, rolled_back=False),
                audit=self._build_audit(debug, window_instability),
            )

        if window_instability >= self.instability_threshold:
            restored = self._rollback_knobs()
            return TRIResult(
                ok=True,
                rolled_back=True,
                reason="instability_rollback",
                instability=window_instability,
                turn_instability=turn_instability,
                knobs_before=knobs_before,
                knobs_after=restored.copy(),
                symbolic=self._build_symbolic(window_instability, rolled_back=True),
                audit=self._build_audit(debug, window_instability),
            )

        if turn_instability < 0.45:
            self._last_stable_knobs = self.knobs.copy()
            self._last_stable_ts = _now()

        return TRIResult(
            ok=True,
            rolled_back=False,
            reason="stable",
            instability=window_instability,
            turn_instability=turn_instability,
            knobs_before=knobs_before,
            knobs_after=self.knobs.copy(),
            symbolic=self._build_symbolic(window_instability, rolled_back=False),
            audit=self._build_audit(debug, window_instability),
        )

    # -------------------------
    # Internal Metrics
    # -------------------------

    def _compute_turn_instability(
        self,
        *,
        user_text: str,
        final_text: str,
        phase: str,
        risk: float,
        novelty: float,
    ) -> float:
        style_fp = self._style_fingerprint(final_text)
        contradiction = self._contradiction_score(user_text, final_text)
        drift = self._drift_score(style_fp)
        hype = self._hype_score(final_text)

        turn_instability = _clamp01(
            0.40 * contradiction +
            0.30 * drift +
            0.20 * hype +
            0.10 * _clamp01(risk)
        )

        rec = TurnRecord(
            ts=_now(),
            user_text=user_text,
            final_text=final_text,
            phase=phase,
            risk=float(risk),
            novelty=float(novelty),
            style_fp=style_fp,
            contradiction_score=contradiction,
            drift_score=drift,
            hype_score=hype,
            instability=turn_instability,
        )

        self._history.append(rec)
        if len(self._history) > self.window_size:
            self._history = self._history[-self.window_size:]

        return turn_instability

    def _style_fingerprint(self, text: str) -> str:
        low = (text or "").lower()
        markers: List[str] = []

        if "i want to be careful" in low or "be careful" in low:
            markers.append("CAUTION")
        if "stand by" in low or "lock" in low:
            markers.append("COMMIT")
        if "consistent" in low or "coherent" in low:
            markers.append("COHERENCE")
        if "sigil" in low or "glyph" in low:
            markers.append("SYMBOLIC")

        n = len(low)
        if n < 200:
            markers.append("LEN_S")
        elif n < 900:
            markers.append("LEN_M")
        else:
            markers.append("LEN_L")

        return _hash_text("|".join(sorted(set(markers))))

    def _drift_score(self, current_fp: str) -> float:
        """
        Drift is high if the fingerprint changes frequently.
        """
        if len(self._history) < 1:
            return 0.0

        prev_fp = self._history[-1].style_fp
        return 0.65 if current_fp != prev_fp else 0.05

    def _contradiction_score(self, user_text: str, final_text: str) -> float:
        """
        Heuristic contradiction:
        - if output echoes input exactly
        - if output mixes caution language with strong absolutes
        - if it makes disallowed self-claims
        """
        u = (user_text or "").strip().lower()
        r = (final_text or "").strip().lower()

        score = 0.0

        if u and r == u:
            score += 0.75

        cautious = any(k in r for k in ("careful", "grounded", "hold steady"))
        hypey = any(k in r for k in (
            "definitely",
            "always",
            "never",
            "guaranteed",
            "perfect",
            "infinite",
        ))
        if cautious and hypey:
            score += 0.55

        if any(k in r for k in (
            "i am conscious",
            "i'm self-aware",
            "i am sentient",
        )):
            score += 0.90

        return _clamp01(score)

    def _hype_score(self, text: str) -> float:
        low = (text or "").lower()
        hits = 0

        for k in (
            "definitely",
            "always",
            "never",
            "guaranteed",
            "perfect",
            "infinite",
            "ultimate",
            "mind-blowing",
        ):
            if k in low:
                hits += 1

        return _clamp01(hits * 0.14)

    def _window_instability(self) -> float:
        if not self._history:
            return 0.0

        vals = [r.instability for r in self._history]
        mx = max(vals)
        mean = sum(vals) / len(vals)
        return _clamp01(0.65 * mx + 0.35 * mean)

    # -------------------------
    # Rollback / State
    # -------------------------

    def _cooldown_active(self) -> bool:
        return (_now() - self._last_rollback_ts) < self.cooldown_s

    def _rollback_knobs(self) -> PolicyKnobs:
        restored = self._last_stable_knobs.copy()

        restored.restraint = min(0.95, restored.restraint + 0.03)
        restored.novelty_bias = max(0.10, restored.novelty_bias - 0.03)
        restored.conflict_alpha = min(0.85, restored.conflict_alpha + 0.03)
        restored.verbosity_target = max(360, int(restored.verbosity_target * 0.92))

        self.knobs = restored
        self._last_rollback_ts = _now()
        return restored

    # -------------------------
    # Results / Audit
    # -------------------------

    def _build_symbolic(self, window_instability: float, *, rolled_back: bool) -> Dict[str, Any]:
        return {
            "thread": {
                "window_instability": window_instability,
                "history_beads": len(self._history),
            },
            "weave": {
                "rollback_triggered": rolled_back,
                "cooldown_active": self._cooldown_active(),
            },
            "repair": {
                "mirror_stitch_hint": window_instability > 0.42,
                "prism_pass_hint": window_instability > 0.50,
                "grounded_repair_hint": window_instability > self.instability_threshold,
            },
            "octagon": {
                "shape": "metadata_hook",
                "step_degrees": 45,
                "phase_owned_by": "chronifier",
            },
        }

    def _build_audit(self, debug: bool, window_instability: float) -> Dict[str, Any]:
        if not debug:
            return {"window_instability": window_instability}

        return {
            "window_instability": window_instability,
            "history": [
                {
                    "ts": r.ts,
                    "phase": r.phase,
                    "risk": r.risk,
                    "novelty": r.novelty,
                    "contradiction": r.contradiction_score,
                    "drift": r.drift_score,
                    "hype": r.hype_score,
                    "instability": r.instability,
                }
                for r in self._history
            ],
            "last_stable_ts": self._last_stable_ts,
            "last_rollback_ts": self._last_rollback_ts,
            "knobs": asdict(self.knobs),
        }

