from __future__ import annotations

print("[TRACE] entering runtime/retrieval_injection.py", flush=True)
from typing import Any, Dict, List, Optional, Tuple

from knowledge.knowledge_node import compute_source_hash
from knowledge.knowledge_store import KnowledgeStore


def normalize_text(text: str) -> List[str]:
    return [word.strip(".,;:!?()[]{}\"'").lower() for word in (text or "").split() if word.strip()]


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
            "grief",
            "love",
            "hope",
            "heavy",
            "hurt",
            "loss",
            "dad",
            "strange",
            "sacred",
        ]
    )


def _adjacent_state(previous_state: str, current_text: str) -> bool:
    lowered = (current_text or "").lower()
    if previous_state == "grief":
        return any(w in lowered for w in ["grief", "loss", "miss", "heavy", "hurt", "dad", "love"])
    if previous_state == "hope":
        return any(w in lowered for w in ["hope", "light", "possible", "healing", "open"])
    if previous_state == "love":
        return any(w in lowered for w in ["love", "care", "miss", "heart", "grief"])
    if previous_state == "awe":
        return any(w in lowered for w in ["sacred", "strange", "vast", "infinite", "mystery"])
    if previous_state == "rage":
        return any(w in lowered for w in ["angry", "rage", "cornered", "pressure", "furious"])
    return False


class RetrievalInjectionEngine:
    def __init__(
        self,
        knowledge_store: KnowledgeStore,
        motif_tracker: Optional[Any] = None,
    ) -> None:
        self.knowledge_store = knowledge_store
        self.motif_tracker = motif_tracker
        self.last_emotional_state: Optional[str] = None

    def _record_value(self, record: Any, key: str, default: Any = None) -> Any:
        if record is None:
            return default
        if isinstance(record, dict):
            return record.get(key, default)
        return getattr(record, key, default)

    def retrieve_relevant_nodes(
        self,
        input_text: str,
        motifs: List[str],
        symbols: List[str],
        hotspot: str,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        all_nodes = self.knowledge_store.all_nodes()
        if not all_nodes:
            return []

        input_hash = compute_source_hash(input_text)
        input_tokens = set(normalize_text(input_text))
        motif_set = set(motifs or [])
        symbol_set = set(symbols or [])
        hotspot_lower = (hotspot or "").lower()

        if not motif_set:
            lowered = (input_text or "").lower()
            if any(w in lowered for w in ["miss", "loss", "hurt", "dad", "gone"]):
                motif_set.add("grief")
            if any(w in lowered for w in ["think", "why", "meaning", "heavy"]):
                motif_set.add("reflection")

        scored: List[Tuple[float, Dict[str, Any]]] = []

        for node in all_nodes:
            score = 0.0

            if node.source_hash == input_hash:
                score += 10.0

            node_motifs = set(node.motifs or [])
            if node_motifs:
                score += 3.0 * float(len(motif_set & node_motifs))

            node_symbols = set(node.symbols or [])
            if node_symbols:
                score += 1.5 * float(len(symbol_set & node_symbols))

            node_hotspot = (node.hotspot or "").lower()
            if hotspot_lower and node_hotspot:
                if hotspot_lower == node_hotspot:
                    score += 2.0
                elif hotspot_lower in node_hotspot or node_hotspot in hotspot_lower:
                    score += 1.0

            gloss_tokens = set(normalize_text(node.gloss))
            if gloss_tokens:
                score += 0.8 * float(len(input_tokens & gloss_tokens))
                if any(token in (node.gloss or "").lower() for token in input_tokens):
                    score += 0.5

            if score > 0.0 or node.motifs or node.symbols or node.gloss:
                scored.append((score + 0.1, node.to_dict()))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [node_dict for _, node_dict in scored[:limit]]

    def retrieve_top_motifs(self, limit: int = 3) -> List[str]:
        motif_map = getattr(self.motif_tracker, "motifs", {}) or {}
        if not motif_map:
            return []

        items = list(motif_map.items())
        items.sort(
            key=lambda item: float(self._record_value(item[1], "weight", 0.0)),
            reverse=True,
        )
        return [motif for motif, _ in items[:limit]]

    def build_context(
        self,
        input_text: str,
        motifs: List[str],
        symbols: List[str],
        hotspot: str,
        emotional_bias: str,
    ) -> Dict[str, Any]:
        relevant_nodes = self.retrieve_relevant_nodes(
            input_text=input_text,
            motifs=motifs,
            symbols=symbols,
            hotspot=hotspot,
            limit=3,
        )

        top_motifs = self.retrieve_top_motifs(limit=3)

        context = {
            "recent_motifs": top_motifs,
            "relevant_nodes": relevant_nodes,
            "previous_emotional_state": self.last_emotional_state,
            "episodic_memories": [],
        }

        self.last_emotional_state = emotional_bias
        return context

    def inject_context_into_reply(
        self,
        input_text: str,
        final_text: str,
        context: Dict[str, Any],
    ) -> str:
        base_reply = str(final_text or "").strip()
        if not base_reply:
            return base_reply

        if not _is_reflective(input_text):
            return base_reply

        nodes = context.get("relevant_nodes", []) or []
        episodic_memories = context.get("episodic_memories", []) or []
        motifs = context.get("recent_motifs", []) or []
        previous_state = str(context.get("previous_emotional_state", "") or "").strip()

        top_node = nodes[0] if nodes else {}
        gloss = str(top_node.get("gloss", "") or "").strip()
        node_motifs = top_node.get("motifs", []) or []

        generic_fallback = (
            "outside the current routed patterns" in base_reply.lower()
            or "closest stable domain" in base_reply.lower()
            or "it carries a trace of what was already there" in base_reply.lower()
        )

        parts: List[str] = []

        # 1. Force anchor from strongest real memory if available
        if episodic_memories:
            top_memory = episodic_memories[0]
            excerpt_text = str(top_memory.get("excerpt_text", "") or "").strip()
            if excerpt_text:
                parts.append(f'This carries the same weight as: "{excerpt_text}".')

        # 2. Otherwise anchor from top node if available
        elif gloss:
            parts.append(f"This is close to {gloss}.")

        # 3. Reuse node motifs in stronger phrasing
        if node_motifs:
            if len(node_motifs) >= 2:
                parts.append(f"It carries {node_motifs[0]} and {node_motifs[1]} together.")
            elif len(node_motifs) == 1:
                parts.append(f"It carries {node_motifs[0]} directly.")

        # 4. If no node motifs, use top tracker motif
        elif motifs:
            motif = str(motifs[0] or "").strip()
            if motif:
                parts.append(f"The pull of {motif} is still active.")

        # 5. Emotional continuity
        if previous_state and previous_state not in ("neutral", "") and _adjacent_state(previous_state, input_text):
            parts.append(f"There is still some {previous_state} under it.")

        # 6. Preserve strongest useful part of existing reply, but strip generic chatbot smell
        if not generic_fallback:
            cleaned = base_reply
            cleaned = cleaned.replace("It seems to ", "It ")
            cleaned = cleaned.replace("it seems to ", "it ")
            cleaned = cleaned.replace("Something in it ", "It ")
            cleaned = cleaned.strip()
            if cleaned:
                parts.append(cleaned)
        else:
            parts.append("The shape of it is becoming more defined.")
            parts.append("It is circling something that has not fully left.")

        # Dedupe while preserving order, including near-duplicate "circling" lines
        final_parts: List[str] = []
        seen = set()
        circling_seen = False

        for part in parts:
            cleaned = part.strip()
            norm = cleaned.lower()
            if not norm:
                continue

            if "circling something that has not fully left" in norm:
                if circling_seen:
                    continue
                circling_seen = True
                norm = "circling_something_not_fully_left"

            if norm in seen:
                continue

            seen.add(norm)
            final_parts.append(cleaned)

        return " ".join(final_parts[:4])

