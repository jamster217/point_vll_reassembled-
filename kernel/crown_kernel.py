from __future__ import annotations

from typing import Any, Dict, List, Optional

from kernel.apex_mirror_kernel import ApexMirrorKernel, WitnessState
from kernel.crystal_library import CrystalLibrary
from kernel.deeper_state_kernel import DeeperStateKernel


class CrownKernel:
    """
    Crown orchestrator.

    Responsibilities
    ----------------
    - run Apex Mirror to assemble present-tense witness state
    - run deeper-state kernel to fuse emotional/dream/shadow fields
    - run Crystal Library to classify the state
    - retain continuity across turns
    """

    def __init__(self, max_history: int = 256) -> None:
        self.apex = ApexMirrorKernel(max_history=max_history)
        self.deeper_kernel = DeeperStateKernel()
        self.library = CrystalLibrary()
        self.max_history = max_history
        self.bound_history: List[WitnessState] = []

    def _append_state(self, state: WitnessState) -> None:
        self.bound_history.append(state)
        self.bound_history = self.bound_history[-self.max_history :]

    def _serialize_state(self, state: WitnessState) -> Dict[str, Any]:
        return {
            "turn": state.turn,
            "glyph": state.glyph,
            "symbol": state.symbol,
            "clause": state.clause,
            "echo": state.echo,
            "pulse_intensity": state.pulse_intensity,
            "recursion_depth": state.recursion_depth,
            "emotional_shift": state.emotional_shift,
            "signature": state.signature,
            "resonance_label": state.resonance_label,
            "witness_summary": state.witness_summary,
            "tags": state.tags,
        }

    def _derive_tone(self, state: WitnessState) -> float:
        shift_map = {
            "sorrow_shift": 0.85,
            "uplift_shift": 0.70,
            "reflective_shift": 0.55,
            "steady_state": 0.40,
        }
        return shift_map.get(state.emotional_shift, 0.40)

    def _derive_lineage(self, state: WitnessState) -> float:
        if state.signature == "witness_lock":
            return 0.65
        if state.signature == "mirror_resonance":
            return 0.50
        if state.signature == "recursive_alignment":
            return 0.60
        return 0.35

    def _derive_memory_pull(self, state: WitnessState) -> float:
        if state.recursion_depth <= 0:
            return 0.20
        return min(1.0, 0.25 + (state.recursion_depth * 0.08))

    def next_turn(self, prompt: Optional[str] = None) -> WitnessState:
        """
        Advance the crown kernel by one turn.

        The prompt is passed into Apex Mirror so the witness state can become
        prompt-conditioned instead of merely turn-advanced.
        """
        state = self.apex.next_turn(prompt=prompt)

        deeper_state = self.deeper_kernel.master_turn(
            tone=self._derive_tone(state),
            glyphs=[state.glyph],
            tags=state.tags,
            lineage=self._derive_lineage(state),
            memory_pull=self._derive_memory_pull(state),
        )

        state.tags.update(
            {
                "turn_index": deeper_state.turn_index,
                "emotional_field": deeper_state.emotional_field,
                "dream_field": deeper_state.dream_field,
                "shadow_field": deeper_state.shadow_field,
                "fused": deeper_state.fused,
                "deeper": deeper_state.deeper,
            }
        )

        if prompt:
            state.tags["prompt"] = prompt

        state = self.library.match(state)

        self._append_state(state)
        return state

    def simulate(self, n: int = 3, seed_prompt: Optional[str] = None) -> List[WitnessState]:
        if n <= 0:
            return []

        results: List[WitnessState] = []
        current_prompt = seed_prompt

        for _ in range(n):
            state = self.next_turn(prompt=current_prompt)
            results.append(state)

            # optional continuity chaining
            current_prompt = state.witness_summary or state.echo or state.clause

        return results

    def latest(self) -> WitnessState | None:
        return self.bound_history[-1] if self.bound_history else None

    def latest_dict(self) -> Dict[str, Any] | None:
        state = self.latest()
        if state is None:
            return None
        return self._serialize_state(state)

    def reset(self) -> None:
        self.apex.reset()
        self.bound_history.clear()


if __name__ == "__main__":
    kernel = CrownKernel()
    results = kernel.simulate(3, seed_prompt="How is the build now?")

    for state in results:
        print("-" * 80)
        print(f"Turn: {state.turn}")
        print(f"Glyph: {state.glyph} {state.symbol}")
        print(f"Clause: {state.clause}")
        print(f"Echo: {state.echo}")
        print(f"Pulse intensity: {state.pulse_intensity}")
        print(f"Recursion depth: {state.recursion_depth}")
        print(f"Emotional shift: {state.emotional_shift}")
        print(f"Signature: {state.signature}")
        print(f"Resonance label: {state.resonance_label}")
        print(f"Witness summary: {state.witness_summary}")
        print(f"Tags: {state.tags}")

