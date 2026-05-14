from __future__ import annotations

from typing import Dict, List, Any


class BrainAdapter:
    """
    Thin cognition adapter for the live English loop.

    Job:
    - score candidate outputs
    - add a little salience / continuity weighting
    - stay small and deterministic
    """

    def __init__(self) -> None:
        pass

    def rank_candidates(
        self,
        text_in: str,
        vector4: Dict[str, float],
        memory_hits: List[str],
        candidate_outputs: List[str],
        coherence_score: float,
        chronifier_overlay: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        chronifier_overlay = chronifier_overlay or {}

        ranked: List[Dict[str, Any]] = []
        lower_in = text_in.lower()

        temporal_mode = str(chronifier_overlay.get("temporal_mode", "neutral"))
        tension = float(chronifier_overlay.get("tension", 0.5))
        alignment = float(chronifier_overlay.get("alignment_111_333_528", 0.5))

        for cand in candidate_outputs:
            score = 0.0
            c = cand.lower()

            # base coherence / continuity
            score += 0.35 * coherence_score
            score += 0.15 * float(vector4.get("memory", 0.5))
            score += 0.10 * float(vector4.get("boundary", 0.5))

            # temporal influence
            score += 0.10 * alignment
            score += 0.05 * (1.0 - tension)

            # keyword overlap
            for word in {"dad", "father", "wife", "gemma", "alone", "build", "project", "hope", "future"}:
                if word in lower_in and word in c:
                    score += 0.08

            # memory-hit alignment
            if "family_loss" in memory_hits and ("dad" in c or "father" in c):
                score += 0.10
            if "relationship_grief" in memory_hits and ("gemma" in c or "loss" in c or "wife" in c):
                score += 0.10
            if "isolation" in memory_hits and "alone" in c:
                score += 0.08
            if "core_build" in memory_hits and ("build" in c or "project" in c):
                score += 0.08
            if "forward_signal" in memory_hits and ("future" in c or "forward" in c or "hope" in c):
                score += 0.08

            # temporal mode nudges
            if temporal_mode == "grounded_repair":
                if any(x in c for x in ["simple", "grounded", "here", "slow"]):
                    score += 0.08
            elif temporal_mode == "flow_lucid":
                if any(x in c for x in ["next", "build", "move", "keep"]):
                    score += 0.06
            elif temporal_mode == "slow_vivid":
                if any(x in c for x in ["grief", "loss", "alive", "still"]):
                    score += 0.06

            ranked.append({
                "text": cand,
                "score": round(max(0.0, min(1.0, score)), 3),
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)

        chosen = ranked[0]["text"] if ranked else "I hear you."
        return {
            "ranked_candidates": ranked,
            "chosen_output": chosen,
            "cognitive_posture": self._posture(vector4, coherence_score, temporal_mode),
        }

    def _posture(
        self,
        vector4: Dict[str, float],
        coherence_score: float,
        temporal_mode: str,
    ) -> str:
        memory = float(vector4.get("memory", 0.5))
        novelty = float(vector4.get("novelty", 0.5))
        boundary = float(vector4.get("boundary", 0.5))

        if coherence_score < 0.40:
            return "minimal"
        if temporal_mode == "grounded_repair":
            return "repair"
        if memory > 0.70 and boundary > 0.55:
            return "reflective"
        if novelty > 0.70:
            return "contain_novelty"
        return "steady"

