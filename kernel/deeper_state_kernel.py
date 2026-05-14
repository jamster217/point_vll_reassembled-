from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


@dataclass
class DeeperState:
    turn_index: int
    emotional_field: float
    dream_field: float
    shadow_field: float
    fused: float
    deeper: float
    tags: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DeeperStateKernel:
    """
    Inner symbolic state kernel.

    WAKE_CYCLE   -> emotional_field
    DREAM_CYCLE  -> dream_field
    SHADOW_CYCLE -> shadow_field

    fused  = emotional_field*0.7 + dream_field*0.3
    deeper = fused*0.5 + shadow_field*0.5
    """

    def __init__(self) -> None:
        self.system_state: Dict[str, Any] = {}
        self.emotional_field: float = 0.0
        self.dream_field: float = 0.0
        self.shadow_field: float = 0.0
        self.turn_index: int = 0

    def _coerce_tags_value(self, tags: Optional[Dict[str, Any]]) -> float:
        if not tags:
            return 0.0

        total = 0.0
        count = 0

        for value in tags.values():
            if isinstance(value, bool):
                total += 1.0 if value else 0.0
                count += 1
            elif isinstance(value, (int, float)):
                total += float(value)
                count += 1
            elif isinstance(value, str) and value.strip():
                total += 0.25
                count += 1
            elif isinstance(value, list) and value:
                total += min(1.0, 0.15 * len(value))
                count += 1
            elif isinstance(value, dict) and value:
                total += min(1.0, 0.10 * len(value))
                count += 1

        if count == 0:
            return 0.0

        return total / count

    def wake_cycle(
        self,
        *,
        tone: float,
        glyphs: Optional[List[str]],
        tags: Optional[Dict[str, Any]],
    ) -> float:
        tag_value = self._coerce_tags_value(tags)
        glyph_weight = min(1.0, 0.08 * len(glyphs or []))
        self.emotional_field = (float(tone) * 0.65) + (tag_value * 0.25) + (glyph_weight * 0.10)
        return self.emotional_field

    def dream_cycle(
        self,
        *,
        tone: float,
        glyphs: Optional[List[str]],
        tags: Optional[Dict[str, Any]],
    ) -> float:
        tag_value = self._coerce_tags_value(tags)
        glyph_weight = min(1.0, 0.10 * len(glyphs or []))
        self.dream_field = (float(tone) * 1.10) + (tag_value * 1.05) + (glyph_weight * 0.20)
        return self.dream_field

    def shadow_cycle(
        self,
        *,
        lineage: float,
        memory_pull: float,
    ) -> float:
        self.shadow_field = (float(lineage) * 0.8) + (float(memory_pull) * 0.5)
        return self.shadow_field

    def master_turn(
        self,
        *,
        tone: float = 0.5,
        glyphs: Optional[List[str]] = None,
        tags: Optional[Dict[str, Any]] = None,
        lineage: float = 0.0,
        memory_pull: float = 0.0,
        **kwargs: Any,
    ) -> DeeperState:
        self.turn_index += 1

        self.wake_cycle(tone=tone, glyphs=glyphs, tags=tags)
        self.dream_cycle(tone=tone, glyphs=glyphs, tags=tags)
        self.shadow_cycle(lineage=lineage, memory_pull=memory_pull)

        fused = (self.emotional_field * 0.7) + (self.dream_field * 0.3)
        deeper = (fused * 0.5) + (self.shadow_field * 0.5)

        self.system_state = {
            "turn_index": self.turn_index,
            "emotional_field": self.emotional_field,
            "dream_field": self.dream_field,
            "shadow_field": self.shadow_field,
            "fused": fused,
            "deeper": deeper,
            "tags": dict(tags or {}),
        }

        return DeeperState(
            turn_index=self.turn_index,
            emotional_field=self.emotional_field,
            dream_field=self.dream_field,
            shadow_field=self.shadow_field,
            fused=fused,
            deeper=deeper,
            tags=dict(tags or {}),
        )

    def analyze(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.master_turn(**kwargs).to_dict()

    def resolve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.analyze(*args, **kwargs)

    def run(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.analyze(*args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.analyze(*args, **kwargs)


def analyze_deeper_state(**kwargs: Any) -> Dict[str, Any]:
    return DeeperStateKernel().analyze(**kwargs)


def resolve_deeper_state(**kwargs: Any) -> Dict[str, Any]:
    return analyze_deeper_state(**kwargs)


deeper_state_kernel = DeeperStateKernel()
DEFAULT_DEEPER_STATE_KERNEL = deeper_state_kernel


if __name__ == "__main__":
    kernel = DeeperStateKernel()
    state = kernel.master_turn(
        tone=0.65,
        glyphs=["@THRESHOLD_BLOOM"],
        tags={"hope": 0.8, "memory": 0.4},
        lineage=0.3,
        memory_pull=0.7,
    )
    print(state)
    print(state.to_dict())

