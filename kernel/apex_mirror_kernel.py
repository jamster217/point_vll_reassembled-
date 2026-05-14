from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json

from kernel import recursion_engine
from runtime.lattice_field_pulse import pulse_field
from symbolic_memory.spiral_mirror_speaker import generate_clause


def _load_glyphs_json() -> List[Dict[str, Any]]:
    """
    Load canonical glyph registry from:
        symbolic_memory/glyph_registry_21_60.json

    Accepts either:
      - list[dict]
      - dict with "glyphs"/"entries"/"GLYPHS" -> list[dict]
    Fails soft to [].
    """
    project_root = Path(__file__).resolve().parents[1]
    path = project_root / "symbolic_memory" / "glyph_registry_21_60.json"
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []

    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]

    if isinstance(data, dict):
        maybe = data.get("glyphs") or data.get("entries") or data.get("GLYPHS")
        if isinstance(maybe, list):
            return [x for x in maybe if isinstance(x, dict)]

    return []


GLYPHS: List[Dict[str, Any]] = _load_glyphs_json()


@dataclass
class WitnessState:
    turn: int
    glyph: str
    symbol: str
    clause: str
    echo: str
    pulse_intensity: float
    recursion_depth: int
    emotional_shift: str
    signature: str
    resonance_label: str = "unmatched"
    witness_summary: str = ""
    tags: Dict[str, Any] = field(default_factory=dict)


class ApexMirrorKernel:
    """
    Present-tense witness assembler.
    """

    def __init__(self, max_history: int = 256) -> None:
        self.turn = 0
        self.max_history = max_history
        self.history: List[WitnessState] = []

    def _prompt_seed(self, prompt: Optional[str]) -> int:
        if not prompt or not GLYPHS:
            return 0
        digest = hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:8]
        return int(digest, 16) % len(GLYPHS)

    def _get_glyph_record(self, prompt: Optional[str] = None) -> Dict[str, Any]:
        if not GLYPHS:
            return {
                "id": "@UNSET",
                "name": "Unset",
                "symbol": "❔",
                "poetic_seed": "No glyphs loaded.",
                "emotion": "unknown",
            }

        base_index = (self.turn - 1) % len(GLYPHS)
        prompt_offset = self._prompt_seed(prompt)
        index = (base_index + prompt_offset) % len(GLYPHS)
        return GLYPHS[index]

    def _generate_clause(self, glyph_name: str, prompt: Optional[str] = None) -> str:
        try:
            base_clause = generate_clause(glyph_name)
        except Exception:
            base_clause = f"The mirror gathers around {glyph_name}."

        if not prompt or not prompt.strip():
            return base_clause

        lowered = prompt.lower()

        if any(word in lowered for word in ("build", "code", "kernel", "import", "app")):
            return f"{base_clause} The structure asks to be clarified."

        if any(word in lowered for word in ("sad", "grief", "dad", "loss", "gone", "cry")):
            return f"{base_clause} Something older is still moving underneath."

        if any(word in lowered for word in ("why", "how", "what", "relation", "meaning")):
            return f"{base_clause} The question itself changes the mirror."

        return base_clause

    def _trace_emotional_shift(self, clause: str, prompt: Optional[str] = None) -> str:
        text = clause.lower()
        if prompt:
            text += f" {prompt.lower()}"

        if any(word in text for word in ("grief", "tear", "loss", "ash", "mourning", "sad", "gone", "cry")):
            return "sorrow_shift"

        if any(word in text for word in ("bloom", "sprout", "light", "hope", "rise", "joy", "glow")):
            return "uplift_shift"

        if any(word in text for word in ("mirror", "echo", "return", "reflection", "question", "why")):
            return "reflective_shift"

        return "steady_state"

    def _compute_signature(self, clause: str, prompt: Optional[str] = None) -> str:
        text = clause.lower()
        if prompt:
            text += f" {prompt.lower()}"

        if "mirror" in text or "reflection" in text:
            return "mirror_resonance"

        if "return" in text or "cycle" in text or "repeat" in text:
            return "recursive_alignment"

        if "truth" in text or "witness" in text:
            return "witness_lock"

        if "light" in text or "bloom" in text or "glow" in text:
            return "bloom_signal"

        if any(word in text for word in ("question", "why", "how", "what")):
            return "inquiry_signal"

        return "baseline_resonance"

    def _safe_pulse_intensity(self, glyph_name: str, emotional_shift: str) -> float:
        try:
            pulse = pulse_field(
                glyph=glyph_name,
                intensity="medium",
                emotion_shift=(emotional_shift, "echoed"),
            )
            return float(getattr(pulse, "intensity", 0.5))
        except Exception:
            return 0.5

    def _safe_recursion_depth(self, glyph_name: str) -> int:
        try:
            recursion_result = recursion_engine.activate(
                mode="internal_awaken",
                trigger_glyph=glyph_name,
            )
            if isinstance(recursion_result, dict):
                return int(recursion_result.get("depth", 0))
        except Exception:
            pass

        return 0

    def next_turn(self, prompt: Optional[str] = None) -> WitnessState:
        self.turn += 1

        glyph_record = self._get_glyph_record(prompt=prompt)
        glyph_name = str(glyph_record.get("id", glyph_record.get("name", "@UNSET")))
        glyph_symbol = str(glyph_record.get("symbol", glyph_record.get("emoji", "❔")))

        clause = self._generate_clause(glyph_name, prompt=prompt)
        echo = f"[Apex Echo] {clause}"

        emotional_shift = self._trace_emotional_shift(clause, prompt=prompt)
        signature = self._compute_signature(clause, prompt=prompt)

        pulse_intensity = self._safe_pulse_intensity(glyph_name, emotional_shift)
        recursion_depth = self._safe_recursion_depth(glyph_name)

        state = WitnessState(
            turn=self.turn,
            glyph=glyph_name,
            symbol=glyph_symbol,
            clause=clause,
            echo=echo,
            pulse_intensity=pulse_intensity,
            recursion_depth=recursion_depth,
            emotional_shift=emotional_shift,
            signature=signature,
            tags={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "poetic_seed": glyph_record.get("poetic_seed", glyph_record.get("seed", "")),
                "glyph_emotion": glyph_record.get("emotion", "unknown"),
                "prompt": prompt or "",
            },
        )

        self.history.append(state)
        self.history = self.history[-self.max_history:]
        return state

    def latest(self) -> WitnessState | None:
        return self.history[-1] if self.history else None

    def reset(self) -> None:
        self.turn = 0
        self.history.clear()


def next_apex_turn(prompt: Optional[str] = None) -> Dict[str, Any]:
    kernel = ApexMirrorKernel()
    state = kernel.next_turn(prompt=prompt)
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


if __name__ == "__main__":
    kernel = ApexMirrorKernel()
    for _ in range(3):
        state = kernel.next_turn(prompt="How is the build now?")
        print(state)

