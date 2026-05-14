from __future__ import annotations

print("[TRACE] entering runtime/turn_packet.py", flush=True)
from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class TurnPacket:
    text_in: str = ""
    source: str = ""
    apex_mode: Any = None
    boundary_gate: Any = None
    candidate_outputs: list[Any] = field(default_factory=list)
    chosen_output: str = ""
    chronifier_overlay: dict[str, Any] = field(default_factory=dict)
    clean_text: str = ""
    cognitive_posture: str = ""
    coherence_score: float = 0.0
    crown_ok: Any = None
    memory_hits: list[Any] = field(default_factory=list)
    mirror_ok: Any = None
    novelty_pressure: float = 0.0
    pacing: str = "steady"
    ranked_candidates: list[Any] = field(default_factory=list)
    subjective_depth: float = 0.0
    symbolic_tags: list[Any] = field(default_factory=list)
    text_out: Any = None
    tokens: list[Any] = field(default_factory=list)
    vector4: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def new(cls, text_in: str, source: str = "chat") -> "TurnPacket":
        return cls(text_in=text_in, source=source)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

__all__ = ["TurnPacket"]

