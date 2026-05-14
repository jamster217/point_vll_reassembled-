from __future__ import annotations

from typing import Any, Dict, List, Optional


SHAPE_KEYS = ["flow", "boundary", "memory", "novelty", "confidence"]


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _is_reflective(text: str) -> bool:
    lowered = (text or "").lower()
    return any(
        word in lowered
        for word in [
            "feel",
            "thinking",
            "think",
            "meaning",
            "why",
            "remember",
            "miss",
            "care",
            "sacred",
            "grief",
            "hope",
            "angry",
            "love",
            "heavy",
            "strange",
        ]
    )


class GenerationBiasEngine:
    """
    Shape-based generation bias engine with a minimal shape field stabilizer.

    Public API stays the same:
      - build_generation_bias(...)
      - apply_generation_bias_to_reply(...)

    New internal features:
      - running averages of shape_signature
      - last 3 deltas
      - motif-weighted smoothing
      - stability index
    """

    def __init__(self, base_alpha: float = 0.20) -> None:
        self.base_alpha = base_alpha
        self.last_emotional_state: Optional[str] = None
        self.shape_field: Dict[str, float] = {
            "flow": 0.50,
            "boundary": 0.50,
            "memory": 0.50,
            "novelty": 0.50,
            "confidence": 0.50,
        }
        self.recent_deltas: List[Dict[str, float]] = []

    # ---------------------------------------------------------
    # Shape field stabilizer
    # ---------------------------------------------------------
    def _normalize_shape_signature(self, shape_signature: Dict[str, float]) -> Dict[str, float]:
        return {
            key: _clamp(shape_signature.get(key, 0.0))
            for key in SHAPE_KEYS
        }

    def _motif_smoothing_alpha(self, motifs: List[str]) -> float:
        """
        More active motifs -> slightly stronger update, but bounded.
        """
        motif_count = len(motifs or [])
        alpha = self.base_alpha + min(0.12, 0.02 * motif_count)
        return _clamp(alpha, 0.05, 0.35)

    def _update_shape_field(
        self,
        shape_signature: Dict[str, float],
        motifs: List[str],
    ) -> Dict[str, Any]:
        current = self._normalize_shape_signature(shape_signature)
        previous = dict(self.shape_field)
        alpha = self._motif_smoothing_alpha(motifs)

        for key in SHAPE_KEYS:
            self.shape_field[key] = _clamp(
                (1.0 - alpha) * self.shape_field[key] + alpha * current[key]
            )

        delta = {
            key: round(current[key] - previous[key], 4)
            for key in SHAPE_KEYS
        }

        self.recent_deltas.append(delta)
        if len(self.recent_deltas) > 3:
            self.recent_deltas.pop(0)

        delta_magnitude = sum(abs(delta[key]) for key in SHAPE_KEYS) / float(len(SHAPE_KEYS))
        stability_index = round(_clamp(1.0 - delta_magnitude), 4)

        return {
            "current": current,
            "running_average": dict(self.shape_field),
            "delta": delta,
            "recent_deltas": list(self.recent_deltas),
            "stability_index": stability_index,
            "smoothing_alpha": round(alpha, 4),
        }

    # ---------------------------------------------------------
    # Emotional gradient
    # ---------------------------------------------------------
    def _build_emotional_gradient(
        self,
        previous_emotional_state: Optional[str],
        current_emotional_state: str,
        delta: Dict[str, float],
    ) -> Dict[str, Any]:
        if not previous_emotional_state:
            gradient = "emerging"
        elif previous_emotional_state == current_emotional_state:
            gradient = "steady"
        else:
            gradient = "shifting"

        return {
            "from": previous_emotional_state or "none",
            "to": current_emotional_state,
            "gradient": gradient,
            "shape_effect": {
                key: round(delta.get(key, 0.0), 4)
                for key in SHAPE_KEYS
            },
        }

    # ---------------------------------------------------------
    # Generation bias packet
    # ---------------------------------------------------------
    def build_generation_bias(
        self,
        shape_signature: Dict[str, float],
        motifs: List[str],
        retrieval_context: Optional[Dict[str, Any]],
        current_emotional_state: str,
    ) -> Dict[str, Any]:
        retrieval_context = retrieval_context or {}
        shape_field_packet = self._update_shape_field(shape_signature, motifs)

        current = shape_field_packet["current"]
        delta = shape_field_packet["delta"]
        stability_index = float(shape_field_packet["stability_index"])

        relevant_nodes = retrieval_context.get("relevant_nodes", []) or []
        recent_motifs = retrieval_context.get("recent_motifs", []) or []

        content_bias = {
            "encourage_callbacks": current["memory"] >= 0.60,
            "encourage_associative_leaps": current["novelty"] >= 0.55,
            "encourage_precision": current["boundary"] >= 0.60,
            "confidence_pull": round(current["confidence"], 4),
            "node_pull": len(relevant_nodes),
        }

        tone_mode = "steady"
        if current_emotional_state == "grief":
            tone_mode = "soft"
        elif current_emotional_state == "hope":
            tone_mode = "rising"
        elif current_emotional_state == "rage":
            tone_mode = "charged"
        elif current_emotional_state == "awe":
            tone_mode = "wide"
        elif current_emotional_state == "love":
            tone_mode = "tender"

        tone_bias = {
            "tone_mode": tone_mode,
            "pacing": "slow" if current["memory"] > 0.65 else "steady",
            "confidence": round(current["confidence"], 4),
            "stability_index": stability_index,
        }

        structural_bias = {
            "paragraph_length": (
                "short"
                if current["boundary"] > 0.68
                else "medium" if current["memory"] > 0.45 else "short"
            ),
            "recursion_depth": (
                "high" if current["novelty"] > 0.70
                else "medium" if current["novelty"] > 0.50
                else "low"
            ),
            "transition_style": "spiral" if current["memory"] > 0.60 else "direct",
            "associative_arc": "open" if current["novelty"] > 0.55 else "contained",
            "fractal_pull": round(current["memory"] * current["novelty"], 4),
            "waveform_pull": round((1.0 - current["boundary"]) * current["flow"], 4),
            "layered_pull": round(current["boundary"] * current["confidence"], 4),
        }

        motif_pull: List[str] = []
        for motif in motifs:
            if motif not in motif_pull:
                motif_pull.append(motif)
        for motif in recent_motifs:
            if motif not in motif_pull:
                motif_pull.append(motif)

        emotional_gradient = self._build_emotional_gradient(
            previous_emotional_state=self.last_emotional_state,
            current_emotional_state=current_emotional_state,
            delta=delta,
        )

        self.last_emotional_state = current_emotional_state

        return {
            "content_bias": content_bias,
            "tone_bias": tone_bias,
            "structural_bias": structural_bias,
            "motif_pull": motif_pull[:5],
            "emotional_gradient": emotional_gradient,
            "shape_field": shape_field_packet,
            "node_count": len(relevant_nodes),
        }

    # ---------------------------------------------------------
    # Light application to reply
    # ---------------------------------------------------------
    def apply_generation_bias_to_reply(
        self,
        input_text: str,
        final_text: str,
        generation_bias: Dict[str, Any],
        retrieval_context: Optional[Dict[str, Any]] = None,
        practical_request: bool = False,
    ) -> str:
        if practical_request:
            return str(final_text or "").strip()

        retrieval_context = retrieval_context or {}
        enriched = str(final_text or "").strip()
        if not enriched:
            return enriched

        if not _is_reflective(input_text):
            return enriched

        content_bias = generation_bias.get("content_bias", {}) or {}
        tone_bias = generation_bias.get("tone_bias", {}) or {}
        structural_bias = generation_bias.get("structural_bias", {}) or {}
        relevant_nodes = retrieval_context.get("relevant_nodes", []) or []
        recent_motifs = retrieval_context.get("recent_motifs", []) or []
        previous_emotional_state = retrieval_context.get("previous_emotional_state")
        current_emotional_state = generation_bias.get("emotional_gradient", {}).get("to", "neutral")

        additions: List[str] = []

        if content_bias.get("encourage_callbacks") and relevant_nodes:
            top_node = relevant_nodes[0]
            gloss = str(top_node.get("gloss", "") or "").strip()
            if gloss and len(gloss.split()) <= 16 and len(enriched.split()) >= 12:
                if gloss.lower() not in enriched.lower():
                    additions.append(f"It seems connected to {gloss}.")

        if content_bias.get("encourage_associative_leaps"):
            additions.append("There may be more than one layer moving at once.")

        if content_bias.get("encourage_precision") and tone_bias.get("tone_mode") in {"steady", "soft", "tender"}:
            additions.append("The shape of it is becoming more defined.")

        if recent_motifs:
            motif = str(recent_motifs[0] or "").strip()
            if motif and motif.lower() not in enriched.lower():
                additions.append(f"The motif of {motif} is still active.")

        adjacent_states = {
            "grief": {"grief", "love", "awe"},
            "love": {"love", "grief", "hope"},
            "hope": {"hope", "awe", "love"},
            "rage": {"rage"},
            "awe": {"awe", "hope", "grief"},
            "neutral": set(),
        }
        if previous_emotional_state and previous_emotional_state not in ("neutral", ""):
            allowed = adjacent_states.get(current_emotional_state, {current_emotional_state})
            if previous_emotional_state in allowed:
                if previous_emotional_state.lower() not in enriched.lower():
                    additions.append(f"There is still some {previous_emotional_state} under it.")

        if structural_bias.get("transition_style") == "spiral" and len(enriched.split()) >= 12:
            additions.append("It seems to be circling something that has not fully left.")

        for addition in additions[:2]:
            if addition.lower() not in enriched.lower():
                enriched += f" {addition}"

        return enriched

