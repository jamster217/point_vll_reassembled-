from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from runtime.resonance_buffer import ResonanceBuffer, extract_semantic_anchors
from runtime.emotional_continuity import apply_decay_filter, blend_into_vector
from runtime.self_correction_kernel import SelfCorrectionKernel
from runtime.path_reinforcement import PathReinforcement

# Optional gravity well hook (must never crash governor)
try:
    from runtime.gravity_well_runtime import (
        load_sigil,
        well_state_from_kernel_state,
        gravity_well_bonus,
    )
except Exception:
    load_sigil = None
    well_state_from_kernel_state = None
    gravity_well_bonus = None


@dataclass
class Candidate:
    text: str
    base_score: float
    meta: Dict


def compute_directness_score(prompt: str, text: str) -> float:
    p = set(extract_semantic_anchors(prompt))
    t_list = extract_semantic_anchors(text)
    t = set(t_list)
    overlap = len(p.intersection(t))

    base = 0.0
    if overlap >= 1:
        base += 0.20
    if len(text.strip()) >= 60:
        base += 0.10

    causal = sum(1 for w in ("because", "by", "shapes", "determines", "causes") if w in text.lower())
    score = base + 0.06 * overlap + 0.05 * causal
    return min(1.0, score)


def compute_coherence_score(text: str) -> float:
    bad_starts = ("this question is really about", "the answer should", "in conclusion")
    low = text.strip().lower()
    if any(low.startswith(b) for b in bad_starts):
        return 0.10
    sents = [s for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
    if len(sents) == 0:
        return 0.10
    if len(sents) > 7:
        return 0.60
    return 0.78


class LeveonGovernor:
    def __init__(self) -> None:
        self.buffer = ResonanceBuffer()
        self.self_correct = SelfCorrectionKernel()
        self.paths = PathReinforcement()
        self._sigil = None
        if load_sigil:
            try:
                self._sigil = load_sigil()
            except Exception:
                self._sigil = None

    def select(
        self,
        prompt: str,
        candidates: List[Candidate],
        prompt_memory_flag: bool = False,
        last_resonance_vectors: Optional[List[Dict[str, float]]] = None,
        current_resonance_vector: Optional[Dict[str, float]] = None,
        path_id_for_winner: Optional[str] = None,
        kernel_state: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        prompt_anchors = extract_semantic_anchors(prompt)

        resonance_used = current_resonance_vector or {}
        continuity_dbg = None
        if prompt_memory_flag and last_resonance_vectors:
            cont = apply_decay_filter(last_resonance_vectors, decay=0.9, max_turns=5)
            resonance_used = blend_into_vector(resonance_used, cont.composite, alpha=0.35)
            continuity_dbg = {"used": cont.used, "weights": cont.weights, "composite": cont.composite}

        # gravity well state (ultra-soft)
        well_state = None
        if well_state_from_kernel_state and isinstance(kernel_state, dict):
            try:
                well_state = well_state_from_kernel_state(kernel_state)
            except Exception:
                well_state = None

        ranked: List[Dict[str, Any]] = []
        for c in (candidates or []):
            gold_boost, gold_dbg = self.buffer.score_boost(c.text, prompt_anchors=prompt_anchors)

            path_boost = 0.0
            path_dbg = {"count": 0, "boost": 0.0}
            pid = (c.meta or {}).get("path_id")
            if pid:
                path_boost, path_dbg = self.paths.get_boost(pid)

            well_boost = 0.0
            well_dbg = {"depth": None, "overlap": 0, "boost": 0.0}
            if gravity_well_bonus and well_state:
                try:
                    well_boost, well_dbg = gravity_well_bonus(c.text, well_state, sigil=self._sigil)
                except Exception:
                    well_boost, well_dbg = 0.0, {"depth": None, "overlap": 0, "boost": 0.0}

            final_score = float(c.base_score) + float(gold_boost) + float(path_boost) + float(well_boost)

            ranked.append(
                {
                    "text": c.text,
                    "score": round(final_score, 6),
                    "base_score": float(c.base_score),
                    "boosts": {"gold": gold_boost, "path": path_boost, "well": well_boost},
                    "debug": {"gold": gold_dbg, "path": path_dbg, "well": well_dbg},
                }
            )

        ranked.sort(key=lambda x: x["score"], reverse=True)
        winner = ranked[0] if ranked else {"text": "", "score": 0.0}

        directness = compute_directness_score(prompt, winner["text"])
        coherence = compute_coherence_score(winner["text"])
        sc = self.self_correct.observe(coherence_score=coherence, directness_score=directness)

        path_stats = None
        if path_id_for_winner:
            path_stats = self.paths.increment(path_id_for_winner)

        stored_gold = self.buffer.add_if_gold(
            chosen_output=winner["text"],
            directness_score=directness,
            meta={"prompt_anchors": prompt_anchors, "winner_score": winner.get("score", 0.0)},
        )

        return {
            "ok": True,
            "chosen_output": winner["text"],
            "ranked_candidates": ranked[:5],
            "metrics": {
                "directness_score": round(directness, 6),
                "coherence_score": round(coherence, 6),
                "coherence_to_directness": round(sc.ratio, 6),
            },
            "self_correction": {
                "triggered": sc.triggered,
                "mode": sc.mode,
                "tension_reset": sc.tension_reset,
                "reason": sc.reason,
                "streak": sc.streak,
            },
            "continuity": continuity_dbg,
            "reinforcement": None if not path_stats else {"count": path_stats.count, "boost": path_stats.boost},
            "gold_standard_stored": stored_gold,
            "lock_phrase": "translation first, filter second, memory conditional, delivery last",
            "resonance_vector_used": resonance_used,
            "gravity_well": well_state,
        }

