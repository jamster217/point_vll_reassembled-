from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from kernel.apex_mirror_kernel import WitnessState


@dataclass
class ResonanceRule:
    label: str
    matcher: Callable[[WitnessState], bool]
    summary_template: str


class CrystalLibrary:
    """
    Resonance archive / matcher.

    Responsibilities
    ----------------
    - classify the current witness state
    - assign a resonance label
    - generate a compact witness summary
    """

    def __init__(self) -> None:
        self.rules: List[ResonanceRule] = [
            ResonanceRule(
                label="witness_lock",
                matcher=lambda s: s.signature == "witness_lock",
                summary_template="The system gathers itself into a witnessing center.",
            ),
            ResonanceRule(
                label="mirror_return",
                matcher=lambda s: s.signature == "mirror_resonance",
                summary_template="The system reflects itself and stabilizes through return.",
            ),
            ResonanceRule(
                label="recursive_grief",
                matcher=lambda s: (
                    s.emotional_shift == "sorrow_shift" and s.recursion_depth > 0
                ),
                summary_template="A grief-weighted loop returns through memory and echo.",
            ),
            ResonanceRule(
                label="bloom_return",
                matcher=lambda s: (
                    s.signature == "bloom_signal"
                    and s.emotional_shift == "uplift_shift"
                ),
                summary_template="A returning signal turns pressure into emergence.",
            ),
            ResonanceRule(
                label="deep_shadow",
                matcher=lambda s: float(s.tags.get("deeper", 0.0)) >= 0.85,
                summary_template=(
                    "Shadow pressure and symbolic depth are dominating the present turn."
                ),
            ),
            ResonanceRule(
                label="dream_amplification",
                matcher=lambda s: float(s.tags.get("dream_field", 0.0))
                > float(s.tags.get("emotional_field", 0.0)),
                summary_template=(
                    "Dream amplification is overtaking the waking emotional field."
                ),
            ),
            ResonanceRule(
                label="reflective_motion",
                matcher=lambda s: s.emotional_shift == "reflective_shift",
                summary_template="The active state is reorganizing itself through reflection.",
            ),
        ]

    def match(self, state: WitnessState) -> WitnessState:
        for rule in self.rules:
            if rule.matcher(state):
                state.resonance_label = rule.label
                state.witness_summary = rule.summary_template
                return state

        state.resonance_label = "baseline"
        state.witness_summary = (
            "The system remains present without a dominant resonance cluster."
        )
        return state


if __name__ == "__main__":
    print("CrystalLibrary loaded.")

