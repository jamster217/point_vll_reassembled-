from __future__ import annotations

from typing import Any, Dict, List, Optional
from memory.shape_sequence_compactor import ShapeSequenceCompactor
from memory.user_pattern_lattice import UserPatternLattice


def _clean(x: Any) -> str:
    return str(x or "").strip()


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


class DialecticBraidEngine:
    """
    Experimental Le'Veon seed:
    - initial prompt/answer
    - derive internal questions
    - derive internal answers
    - braid logic + emotion
    - detect hotspots
    - store user/user-shared patterns
    - choose final response from abundance
    """

    def __init__(
        self,
        *,
        sequence_compactor: Optional[ShapeSequenceCompactor] = None,
        user_lattice: Optional[UserPatternLattice] = None,
    ) -> None:
        self.sequence_compactor = sequence_compactor or ShapeSequenceCompactor()
        self.user_lattice = user_lattice or UserPatternLattice()

    def run(
        self,
        *,
        user_name: str,
        prompt_text: str,
        initial_answer: str,
        previous_prompt: str = "",
        previous_reply: str = "",
        domain: str = "",
        shape_signature: Optional[Dict[str, float]] = None,
        emotion_weights: Optional[Dict[str, float]] = None,
        depth: int = 3,
    ) -> Dict[str, Any]:
        prompt_text = _clean(prompt_text)
        initial_answer = _clean(initial_answer)
        previous_prompt = _clean(previous_prompt)
        previous_reply = _clean(previous_reply)
        domain = _clean(domain)
        shape_signature = shape_signature or {}
        emotion_weights = emotion_weights or {}

        abundance: List[Dict[str, Any]] = []
        braid_steps: List[Dict[str, Any]] = []

        current_q = prompt_text
        current_a = initial_answer

        for step_idx in range(max(1, depth)):
            derived_q = self._derive_internal_question(
                origin_prompt=prompt_text,
                current_question=current_q,
                current_answer=current_a,
                domain=domain,
                step_idx=step_idx,
            )
            derived_a = self._derive_internal_answer(
                derived_question=derived_q,
                current_answer=current_a,
                domain=domain,
                step_idx=step_idx,
            )

            logic_score = self._logic_score(derived_q, derived_a, domain)
            emotion_score = self._emotion_score(prompt_text, derived_q, derived_a, emotion_weights)
            hotspot_score = self._hotspot_score(logic_score, emotion_score, derived_q, derived_a)

            step = {
                "step": step_idx,
                "source_question": current_q,
                "source_answer": current_a,
                "derived_question": derived_q,
                "derived_answer": derived_a,
                "logic_score": logic_score,
                "emotion_score": emotion_score,
                "hotspot_score": hotspot_score,
            }
            braid_steps.append(step)

            abundance.append({
                "type": "candidate_answer",
                "text": derived_a,
                "logic_score": logic_score,
                "emotion_score": emotion_score,
                "hotspot_score": hotspot_score,
                "total": round(_clamp((logic_score * 0.4) + (emotion_score * 0.28) + (hotspot_score * 0.32)), 4),
            })

            current_q = derived_q
            current_a = derived_a

        abundance.append({
            "type": "initial_answer",
            "text": initial_answer,
            "logic_score": self._logic_score(prompt_text, initial_answer, domain),
            "emotion_score": self._emotion_score(prompt_text, prompt_text, initial_answer, emotion_weights),
            "hotspot_score": 0.52,
            "total": 0.58,
        })

        abundance.sort(key=lambda x: float(x.get("total", 0.0)), reverse=True)
        final_answer = abundance[0]["text"] if abundance else initial_answer

        seq_packet = self.sequence_compactor.observe_exchange(
            previous_prompt=previous_prompt,
            previous_reply=previous_reply,
            current_prompt=prompt_text,
            current_reply=final_answer,
            previous_domain=domain,
            current_domain=domain,
            enable_english_gloss=False,
        )

        user_packet = self.user_lattice.observe_user_sequence(
            user_name=user_name,
            prompt_text=prompt_text,
            reply_text=final_answer,
            domain=domain,
            logical_coherence=float(seq_packet.get("logical_coherence", 0.5)),
            emotional_fidelity=float(seq_packet.get("emotional_fidelity", 0.5)),
            hotspot_score=max([float(x.get("hotspot_score", 0.0)) for x in braid_steps] or [0.5]),
            sequence_family=str(seq_packet.get("sequence_family", "")),
            relation_chain=list(seq_packet.get("relation_chain", []) or []),
            shape_signature=shape_signature,
            emotion_weights=emotion_weights,
            hotspot_hint="braid_hotspot",
        )

        return {
            "user_name": user_name,
            "prompt_text": prompt_text,
            "initial_answer": initial_answer,
            "final_answer": final_answer,
            "braid_steps": braid_steps,
            "abundance_pool": abundance[:8],
            "sequence_packet": seq_packet,
            "user_packet": user_packet,
            "cross_user_connections": self.user_lattice.get_cross_user_connections(user_name, limit=5),
        }

    # ---------------------------------------------------------
    # Internal derivation
    # ---------------------------------------------------------
    def _derive_internal_question(
        self,
        *,
        origin_prompt: str,
        current_question: str,
        current_answer: str,
        domain: str,
        step_idx: int,
    ) -> str:
        low_q = current_question.lower()
        low_a = current_answer.lower()

        if step_idx == 0 and low_q.strip().startswith("why"):
            return "What underlying relation makes that true?"

        if "memory" in low_q or "memory" in low_a:
            return "What keeps the remembered pattern active instead of fading completely?"

        if any(x in low_q for x in ["grief", "pain", "loss", "miss"]):
            return "What is the feeling trying to preserve, protect, or stay connected to?"

        if "time" in low_q or "time" in low_a:
            return "How does time allow earlier states to remain available inside later experience?"

        return "What hidden relation beneath the current answer would make the next answer more faithful?"

    def _derive_internal_answer(
        self,
        *,
        derived_question: str,
        current_answer: str,
        domain: str,
        step_idx: int,
    ) -> str:
        q = derived_question.lower()

        if "remembered pattern active" in q:
            return "A remembered pattern stays active when emotion, repetition, and significance keep reactivating it inside the present."

        if "preserve, protect, or stay connected" in q:
            return "The feeling is often trying to preserve contact with what mattered, even when direct contact is no longer possible."

        if "earlier states to remain available" in q:
            return "Time does not preserve the past by freezing it. It preserves it through memory, trace, and the continued effects of what has already happened."

        if "underlying relation" in q:
            return "The underlying relation is that one state remains linked to another, so the later answer still carries pressure from the earlier one."

        return "The deeper answer is the one that keeps the original shape intact while revealing the relation that was implicit rather than spoken."

    # ---------------------------------------------------------
    # Scoring
    # ---------------------------------------------------------
    def _logic_score(self, q: str, a: str, domain: str) -> float:
        score = 0.54
        low_q = q.lower()
        low_a = a.lower()

        if "because" in low_a or "relation" in low_a:
            score += 0.08
        if any(x in low_a for x in ["when", "through", "so that", "therefore", "remains", "preserve"]):
            score += 0.08
        if domain in {"basic_query", "emotional_depth", "grief_support"}:
            score += 0.05
        return round(_clamp(score), 4)

    def _emotion_score(self, origin_prompt: str, q: str, a: str, emotion_weights: Dict[str, float]) -> float:
        score = 0.46 + min(0.18, 0.08 * len(emotion_weights))
        low = " ".join([origin_prompt, q, a]).lower()
        if any(x in low for x in ["grief", "loss", "miss", "pain", "hurt", "love", "ache"]):
            score += 0.14
        if any(x in low for x in ["preserve", "connected", "contact", "matter", "mattered"]):
            score += 0.08
        return round(_clamp(score), 4)

    def _hotspot_score(self, logic_score: float, emotion_score: float, q: str, a: str) -> float:
        blend = 1.0 - abs(logic_score - emotion_score)
        score = (logic_score * 0.35) + (emotion_score * 0.35) + (blend * 0.30)
        if "relation" in q.lower() and "preserve" in a.lower():
            score += 0.06
        return round(_clamp(score), 4)


__all__ = ["DialecticBraidEngine"]

