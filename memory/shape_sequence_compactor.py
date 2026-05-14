from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import math
import re
import time
import uuid


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _clean(text: Any) -> str:
    return str(text or "").strip()


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9_']+", text.lower())


def _unique(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


EMOTION_LEXICON = {
    "grief": ["grief", "loss", "missing", "miss", "mourning", "bereaved", "gone", "death", "died", "wife", "husband", "dad", "mom", "mother", "father"],
    "pain": ["pain", "hurt", "hurting", "ache", "aching", "broken", "heartbroken"],
    "love": ["love", "beloved", "dear", "care", "caring", "tender"],
    "fear": ["afraid", "fear", "terrified", "scared", "panic"],
    "anger": ["angry", "rage", "furious", "mad", "resent"],
    "hope": ["hope", "healing", "heal", "recover", "forward"],
    "curiosity": ["why", "how", "what", "meaning", "relation", "understand", "explain"],
    "smalltalk": ["hi", "hello", "hey", "hiya", "howdy"],
}

RELATION_MARKERS = {
    "followup_why": ["why", "why?", "why is that", "and why"],
    "followup_how": ["how", "how?", "how so", "and how"],
    "clarification": ["what do you mean", "explain", "go on", "continue"],
    "topic_shift": ["new topic", "different topic", "another question", "unrelated"],
}


@dataclass
class ShapeSignature:
    flow: float = 0.5
    boundary: float = 0.5
    memory: float = 0.5
    novelty: float = 0.5
    confidence: float = 0.5
    emotion_weights: Dict[str, float] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)


@dataclass
class SequenceNode:
    text: str
    domain: str = ""
    shape: Dict[str, Any] = field(default_factory=dict)
    english_gloss: str = ""


@dataclass
class SequencePacket:
    packet_id: str
    created_at: float
    previous_prompt: SequenceNode
    previous_reply: SequenceNode
    current_prompt: SequenceNode
    current_reply: SequenceNode
    relation_chain: List[str]
    dominant_relation: str
    logical_coherence: float
    emotional_fidelity: float
    continuity_strength: float
    mutation_trace: List[str] = field(default_factory=list)
    sequence_family: str = ""
    english_enabled: bool = False


class ShapeSequenceCompactor:
    """
    Le'Veon seed:
    prompt -> reply -> prompt -> reply
    stored as compact shape sequence, not raw English-first memory.
    """

    def __init__(self, db_path: str = "memory/shape_sequence_db.jsonl") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------
    def observe_exchange(
        self,
        previous_prompt: str,
        previous_reply: str,
        current_prompt: str,
        current_reply: str,
        *,
        previous_domain: str = "",
        current_domain: str = "",
        previous_meta: Optional[Dict[str, Any]] = None,
        current_meta: Optional[Dict[str, Any]] = None,
        enable_english_gloss: bool = False,
    ) -> Dict[str, Any]:
        previous_meta = previous_meta or {}
        current_meta = current_meta or {}

        prev_prompt_node = SequenceNode(
            text=_clean(previous_prompt),
            domain=_clean(previous_domain),
            shape=self._shape_signature(previous_prompt),
            english_gloss=self._english_gloss(previous_prompt) if enable_english_gloss else "",
        )
        prev_reply_node = SequenceNode(
            text=_clean(previous_reply),
            domain=_clean(previous_domain),
            shape=self._shape_signature(previous_reply),
            english_gloss=self._english_gloss(previous_reply) if enable_english_gloss else "",
        )
        cur_prompt_node = SequenceNode(
            text=_clean(current_prompt),
            domain=_clean(current_domain),
            shape=self._shape_signature(current_prompt),
            english_gloss=self._english_gloss(current_prompt) if enable_english_gloss else "",
        )
        cur_reply_node = SequenceNode(
            text=_clean(current_reply),
            domain=_clean(current_domain),
            shape=self._shape_signature(current_reply),
            english_gloss=self._english_gloss(current_reply) if enable_english_gloss else "",
        )

        relation_chain = self._infer_relation_chain(
            prev_prompt_node.text,
            prev_reply_node.text,
            cur_prompt_node.text,
            cur_reply_node.text,
        )
        dominant_relation = relation_chain[0] if relation_chain else "unclassified"

        logical_coherence = self._score_logical_coherence(
            prev_prompt_node, prev_reply_node, cur_prompt_node, cur_reply_node, relation_chain
        )
        emotional_fidelity = self._score_emotional_fidelity(
            prev_prompt_node, prev_reply_node, cur_prompt_node, cur_reply_node
        )
        continuity_strength = self._score_continuity_strength(
            prev_prompt_node, prev_reply_node, cur_prompt_node
        )

        sequence_family = self._sequence_family(
            previous_domain=prev_prompt_node.domain or prev_reply_node.domain,
            current_domain=cur_prompt_node.domain or cur_reply_node.domain,
            dominant_relation=dominant_relation,
            cur_prompt_shape=cur_prompt_node.shape,
        )

        packet = SequencePacket(
            packet_id=f"seq_{uuid.uuid4().hex[:12]}",
            created_at=time.time(),
            previous_prompt=prev_prompt_node,
            previous_reply=prev_reply_node,
            current_prompt=cur_prompt_node,
            current_reply=cur_reply_node,
            relation_chain=relation_chain,
            dominant_relation=dominant_relation,
            logical_coherence=logical_coherence,
            emotional_fidelity=emotional_fidelity,
            continuity_strength=continuity_strength,
            mutation_trace=[],
            sequence_family=sequence_family,
            english_enabled=enable_english_gloss,
        )

        payload = asdict(packet)
        self._append_packet(payload)
        return payload

    def correlate_prompt(
        self,
        prompt_text: str,
        *,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        target_shape = self._shape_signature(prompt_text)
        rows = self._read_packets()

        scored: List[Tuple[float, Dict[str, Any]]] = []
        for row in rows:
            cur_prompt = ((row.get("current_prompt") or {}).get("shape") or {})
            prev_prompt = ((row.get("previous_prompt") or {}).get("shape") or {})
            score = max(
                self._shape_similarity(target_shape, cur_prompt),
                self._shape_similarity(target_shape, prev_prompt),
            )
            if score > 0.18:
                scored.append((score, row))

        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for score, row in scored[:limit]:
            row = dict(row)
            row["correlation_score"] = round(score, 4)
            out.append(row)
        return out

    def mutate_packet(
        self,
        packet: Dict[str, Any],
        *,
        mutation_strength: float = 0.08,
    ) -> Dict[str, Any]:
        packet = dict(packet)
        packet["mutation_trace"] = list(packet.get("mutation_trace") or [])

        lc = float(packet.get("logical_coherence", 0.5))
        ef = float(packet.get("emotional_fidelity", 0.5))
        cs = float(packet.get("continuity_strength", 0.5))

        # bounded mutation: improve weak dimensions slightly
        if lc < 0.72:
            lc = _clamp(lc + mutation_strength)
            packet["mutation_trace"].append("coherence_reinforcement")

        if ef < 0.72:
            ef = _clamp(ef + mutation_strength * 0.8)
            packet["mutation_trace"].append("emotional_fidelity_reinforcement")

        if cs < 0.68:
            cs = _clamp(cs + mutation_strength * 0.9)
            packet["mutation_trace"].append("continuity_reinforcement")

        packet["logical_coherence"] = round(lc, 4)
        packet["emotional_fidelity"] = round(ef, 4)
        packet["continuity_strength"] = round(cs, 4)
        return packet

    def render_sequence_gloss(self, packet: Dict[str, Any]) -> str:
        relation = str(packet.get("dominant_relation", "unclassified"))
        cur_prompt = (((packet.get("current_prompt") or {}).get("text")) or "").strip()
        cur_reply = (((packet.get("current_reply") or {}).get("text")) or "").strip()
        prev_prompt = (((packet.get("previous_prompt") or {}).get("text")) or "").strip()

        if relation == "followup_why":
            return f"The current turn asks why in relation to the previous exchange. Prior question: {prev_prompt}"
        if relation == "grief_deepening":
            return "The sequence deepens an emotionally weighted thread and keeps memory pressure active."
        if relation == "clarification":
            return "The sequence requests clarification while preserving continuity with the prior reply."
        if relation == "topic_shift":
            return "The sequence breaks from the prior thread and starts a fresh route."
        if cur_prompt and cur_reply:
            return f"The sequence links the current prompt to a shaped reply through {relation}."
        return f"Sequence relation: {relation}"

    # ---------------------------------------------------------
    # Core shaping
    # ---------------------------------------------------------
    def _shape_signature(self, text: str) -> Dict[str, Any]:
        text = _clean(text)
        toks = _tokens(text)

        flow = 0.5
        boundary = 0.5
        memory = 0.5
        novelty = 0.5
        confidence = 0.5

        lower = text.lower()

        if len(toks) <= 2:
            boundary += 0.08
            novelty -= 0.04

        if any(x in lower for x in ["why", "how", "what", "explain", "relation"]):
            flow += 0.08
            novelty += 0.06

        if any(x in lower for x in ["miss", "grief", "loss", "wife", "dad", "mom", "pain", "hurt"]):
            memory += 0.18
            boundary += 0.10
            confidence += 0.04

        if any(x in lower for x in ["new topic", "different topic", "unrelated"]):
            novelty += 0.18
            boundary += 0.10

        if any(x in lower for x in ["hi", "hello", "hey", "hiya"]):
            boundary += 0.05
            confidence += 0.03
            novelty -= 0.08

        emotion_weights = {}
        for emo, words in EMOTION_LEXICON.items():
            hit_count = sum(1 for w in words if w in lower)
            if hit_count:
                emotion_weights[emo] = _clamp(0.35 + 0.12 * hit_count)

        keywords = _unique([t for t in toks if len(t) > 2][:8])

        return asdict(
            ShapeSignature(
                flow=_clamp(flow),
                boundary=_clamp(boundary),
                memory=_clamp(memory),
                novelty=_clamp(novelty),
                confidence=_clamp(confidence),
                emotion_weights=emotion_weights,
                keywords=keywords,
            )
        )

    def _infer_relation_chain(
        self,
        previous_prompt: str,
        previous_reply: str,
        current_prompt: str,
        current_reply: str,
    ) -> List[str]:
        cur = current_prompt.lower().strip()
        prev_r = previous_reply.lower().strip()
        rels: List[str] = []

        if any(x in cur for x in RELATION_MARKERS["topic_shift"]):
            rels.append("topic_shift")

        if cur.rstrip("?.! ") in RELATION_MARKERS["followup_why"] or cur.startswith("why"):
            rels.append("followup_why")

        if cur.rstrip("?.! ") in RELATION_MARKERS["followup_how"] or cur.startswith("how "):
            rels.append("followup_how")

        if any(x in cur for x in RELATION_MARKERS["clarification"]):
            rels.append("clarification")

        if any(x in cur for x in ["miss", "grief", "pain", "loss"]) and any(
            x in prev_r for x in ["miss", "grief", "pain", "loss", "memory", "ache"]
        ):
            rels.append("grief_deepening")

        if not rels:
            overlap = self._keyword_overlap(previous_reply, current_prompt)
            if overlap >= 0.34:
                rels.append("continuity")
            else:
                rels.append("fresh_turn")

        return _unique(rels)

    # ---------------------------------------------------------
    # Scoring
    # ---------------------------------------------------------
    def _score_logical_coherence(
        self,
        prev_prompt: SequenceNode,
        prev_reply: SequenceNode,
        cur_prompt: SequenceNode,
        cur_reply: SequenceNode,
        relation_chain: List[str],
    ) -> float:
        score = 0.55

        overlap_pr_cp = self._keyword_overlap(prev_reply.text, cur_prompt.text)
        overlap_cp_cr = self._keyword_overlap(cur_prompt.text, cur_reply.text)

        score += overlap_pr_cp * 0.18
        score += overlap_cp_cr * 0.20

        if "followup_why" in relation_chain and "because" in cur_reply.text.lower():
            score += 0.10
        if "topic_shift" in relation_chain:
            score += 0.05
        if "clarification" in relation_chain and len(cur_reply.text.split()) > 4:
            score += 0.06

        return round(_clamp(score), 4)

    def _score_emotional_fidelity(
        self,
        prev_prompt: SequenceNode,
        prev_reply: SequenceNode,
        cur_prompt: SequenceNode,
        cur_reply: SequenceNode,
    ) -> float:
        pp = prev_prompt.shape.get("emotion_weights", {})
        pr = prev_reply.shape.get("emotion_weights", {})
        cp = cur_prompt.shape.get("emotion_weights", {})
        cr = cur_reply.shape.get("emotion_weights", {})

        shared_prev = self._emotion_overlap(pp, pr)
        shared_cur = self._emotion_overlap(cp, cr)
        carried = self._emotion_overlap(pr, cp)

        score = 0.48 + (shared_prev * 0.16) + (shared_cur * 0.22) + (carried * 0.14)
        return round(_clamp(score), 4)

    def _score_continuity_strength(
        self,
        prev_prompt: SequenceNode,
        prev_reply: SequenceNode,
        cur_prompt: SequenceNode,
    ) -> float:
        score = 0.42
        score += self._keyword_overlap(prev_reply.text, cur_prompt.text) * 0.28
        score += self._shape_similarity(prev_reply.shape, cur_prompt.shape) * 0.20

        cp = cur_prompt.text.lower().strip()
        if cp in {"why?", "why", "how?", "how", "what do you mean?", "what do you mean"}:
            score += 0.18

        return round(_clamp(score), 4)

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    def _sequence_family(
        self,
        previous_domain: str,
        current_domain: str,
        dominant_relation: str,
        cur_prompt_shape: Dict[str, Any],
    ) -> str:
        prev = previous_domain or "unknown"
        cur = current_domain or "unknown"
        emo = sorted((cur_prompt_shape.get("emotion_weights") or {}).keys())
        emo_tag = emo[0] if emo else "neutral"
        return f"{prev}->{cur}:{dominant_relation}:{emo_tag}"

    def _shape_similarity(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        keys = ["flow", "boundary", "memory", "novelty", "confidence"]
        if not a or not b:
            return 0.0
        dist = 0.0
        for k in keys:
            dist += abs(float(a.get(k, 0.5)) - float(b.get(k, 0.5)))
        dist /= len(keys)
        return round(_clamp(1.0 - dist), 4)

    def _keyword_overlap(self, a: str, b: str) -> float:
        sa = set(_tokens(a))
        sb = set(_tokens(b))
        if not sa or not sb:
            return 0.0
        inter = len(sa & sb)
        base = max(1, min(len(sa), len(sb)))
        return round(_clamp(inter / base), 4)

    def _emotion_overlap(self, a: Dict[str, float], b: Dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        shared = set(a.keys()) & set(b.keys())
        if not shared:
            return 0.0
        vals = []
        for k in shared:
            vals.append(min(float(a.get(k, 0.0)), float(b.get(k, 0.0))))
        if not vals:
            return 0.0
        return round(_clamp(sum(vals) / max(1, len(vals))), 4)

    def _english_gloss(self, text: str) -> str:
        text = _clean(text)
        if not text:
            return ""
        return text[:220]

    def _append_packet(self, payload: Dict[str, Any]) -> None:
        with self.db_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _read_packets(self) -> List[Dict[str, Any]]:
        if not self.db_path.exists():
            return []
        rows = []
        for line in self.db_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
        return rows


__all__ = ["ShapeSequenceCompactor"]

