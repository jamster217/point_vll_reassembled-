from __future__ import annotations

from typing import Dict, List
from memory.dialectical_synthesizer import synthesize_response
from memory.shape_compound_store import make_compound, append_compound


def build_contained_memory(
    *,
    source_text: str,
    thesis: str,
    counterforce: str,
    source_kind: str = "chat",
    meaning_tags: List[str] | None = None,
    symbolic_trace: List[str] | None = None,
    flow: float = 0.55,
    boundary: float = 0.65,
    memory: float = 0.72,
    novelty: float = 0.40,
    confidence: float = 0.80,
) -> Dict:
    meaning_tags = meaning_tags or []
    symbolic_trace = symbolic_trace or []

    packet = synthesize_response(source_text, thesis, counterforce)

    compound = make_compound(
        source_kind=source_kind,
        english_gloss=packet["final_point"],
        synthesis_summary=packet["synthesis"],
        logic_chain=packet["logic_chain"],
        meaning_tags=meaning_tags,
        symbolic_trace=symbolic_trace,
        flow=flow,
        boundary=boundary,
        memory=memory,
        novelty=novelty,
        confidence=confidence,
    )

    append_compound(compound)
    return {
        "dialectical_packet": packet,
        "shape_compound": compound,
    }

