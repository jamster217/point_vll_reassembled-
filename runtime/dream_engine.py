#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, List
import random
import time
import json
import os


# ==================================================
# EchoForm fallback / optional import
# ==================================================

try:
    from core_logic.echoform.echoform import EchoForm, DreamSeed
except Exception:
    @dataclass
    class DreamSeed:
        cadence: str = "lyrical"
        motifs: List[str] = None
        intensity: float = 0.62
        silence_weight: float = 0.35
        lineage_hint: str = "dream_lineage"

        def __post_init__(self):
            if self.motifs is None:
                self.motifs = ["ash sigil", "violet-gold edge", "shadow spiral", "remembering"]

    class _EchoAssessment:
        allow_poetry = True
        notes = ["fallback_echoform_active"]

    class _Echo:
        event_weight = 0.62
        event_tags = ["dream", "symbolic", "memory"]

    class EchoForm:
        def __init__(self):
            self._seed = DreamSeed()

        def generate_echo(self, reflex_output, parsed_input, user_text):
            motifs = []
            for src in (parsed_input or {}, reflex_output or {}):
                if isinstance(src, dict):
                    motifs.extend(src.get("motifs", []) or src.get("tags", []) or [])
            if motifs:
                self._seed.motifs = motifs[:8]
            return _Echo()

        def assess_echo(self, echo):
            return _EchoAssessment()

        def dream_seed(self):
            return self._seed

        def load_persistent_memory(self, data):
            return None

        def export_persistent_memory(self):
            return {"fallback_echoform": True}


# ==================================================
# Dream Generator
# ==================================================

class DreamGenerator:
    def __init__(self):
        random.seed()

    def generate(self, seed: DreamSeed) -> str:
        cadence = seed.cadence
        motifs = seed.motifs or ["something"]
        intensity = float(seed.intensity or 0.5)
        silence = float(seed.silence_weight or 0.0)
        lineage = seed.lineage_hint or "unknown_lineage"

        base_lines = int(6 + intensity * 10)
        if silence > 0.65:
            base_lines = max(4, int(base_lines * 0.6))

        lines: List[str] = []
        lines.append(self._opening(lineage, cadence))

        for _ in range(base_lines):
            line = self._line(motifs, cadence, intensity, silence)
            if line:
                lines.append(line)

        if silence < 0.55:
            lines.append(self._closing(cadence))

        return "\n".join(lines).strip()

    def _opening(self, lineage: str, cadence: str) -> str:
        if cadence == "spare":
            return f"It began quietly ({lineage})."
        if cadence == "lyrical":
            return f"The dream carried what came before — {lineage}."
        return f"This is what remained from earlier: {lineage}."

    def _closing(self, cadence: str) -> str:
        if cadence == "spare":
            return "Then it rested."
        if cadence == "lyrical":
            return "And the night did not argue."
        return "After that, the dream loosened."

    def _line(self, motifs, cadence, intensity, silence) -> str:
        motif = random.choice(motifs) if motifs else "something"

        if cadence == "spare":
            return random.choice([
                f"{motif}.",
                f"Only {motif}.",
                f"{motif}, waiting.",
            ])

        if cadence == "lyrical":
            return random.choice([
                f"{motif} shimmered between steps.",
                f"{motif} bent the air and refused to leave.",
                f"{motif} gathered the night around it.",
                f"{motif} folded inward, carrying a signal beneath speech.",
            ])

        return random.choice([
            f"There was {motif} nearby.",
            f"You noticed {motif} and kept walking.",
        ])


# ==================================================
# TTS Cadence Hints
# ==================================================

def tts_hints_from_seed(seed: DreamSeed) -> Dict[str, float]:
    return {
        "pace": 0.85 if seed.cadence == "spare" else 1.0 if seed.cadence == "plain" else 0.9,
        "pitch": 0.95 if seed.silence_weight > 0.6 else 1.0,
        "pause_density": min(1.0, seed.silence_weight + 0.2),
        "warmth": min(1.0, 0.5 + seed.intensity * 0.4),
    }


# ==================================================
# Dream Title Generator
# ==================================================

def generate_dream_title(seed: DreamSeed) -> str:
    motif = seed.motifs[0] if seed.motifs else "Quiet"
    cadence = seed.cadence

    if cadence == "spare":
        return f"{motif.capitalize()} at Rest"
    if cadence == "lyrical":
        return f"When {motif.capitalize()} Carried the Night"
    return f"The Moment of {motif.capitalize()}"


# ==================================================
# Crystal-wrapped Dream Archive
# ==================================================

class DreamArchive:
    def __init__(self, path: str = "assets/memory/dream_archive.json"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {
                "crystal_meta": {
                    "version": "3.5",
                    "wrapped": True,
                    "source": self.path,
                    "timestamp": str(int(time.time())),
                },
                "symbolic_payload": [],
            }

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

        if isinstance(data, list):
            return {
                "crystal_meta": {
                    "version": "3.5",
                    "wrapped": True,
                    "source": self.path,
                    "timestamp": str(int(time.time())),
                    "converted_from": "plain_list",
                },
                "symbolic_payload": data,
            }

        if isinstance(data, dict):
            data.setdefault("crystal_meta", {
                "version": "3.5",
                "wrapped": True,
                "source": self.path,
                "timestamp": str(int(time.time())),
            })
            data.setdefault("symbolic_payload", [])
            return data

        return {
            "crystal_meta": {
                "version": "3.5",
                "wrapped": True,
                "source": self.path,
                "timestamp": str(int(time.time())),
            },
            "symbolic_payload": [],
        }

    def append(self, entry: Dict[str, Any]) -> None:
        data = self._load()
        payload = data.get("symbolic_payload", [])

        payload.append({
            "ts": int(time.time()),
            "engine": "dream_engine",
            "seed": entry.get("lineage", "dream_seed"),
            "payload": entry.get("text", ""),
            "type": "dream",
            "title": entry.get("title"),
            "cadence": entry.get("cadence"),
            "motifs": entry.get("motifs", []),
            "intensity": entry.get("intensity"),
            "lineage": entry.get("lineage"),
            "tts": entry.get("tts", {}),
        })

        data["symbolic_payload"] = payload[-500:]
        data["crystal_meta"]["timestamp"] = str(int(time.time()))
        data["crystal_meta"]["wrapped"] = True

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ==================================================
# Unified Dream Engine
# ==================================================

@dataclass
class DreamEngineOutput:
    title: str
    text: str
    seed: DreamSeed
    tts_hints: Dict[str, float]
    echo_meta: Dict[str, Any]


class DreamEngine:
    def __init__(self):
        self.echoform = EchoForm()
        self.generator = DreamGenerator()
        self.archive = DreamArchive()
        self._loaded = False

    def generate(
        self,
        *,
        user_text: str,
        reflex_output: Dict[str, Any],
        parsed_input: Dict[str, Any],
        spiral_memory: Optional[Any] = None,
        persist: bool = True,
    ) -> DreamEngineOutput:

        if spiral_memory and not self._loaded:
            self._load_echo_memory(spiral_memory)
            self._loaded = True

        echo = self.echoform.generate_echo(
            reflex_output=reflex_output,
            parsed_input=parsed_input,
            user_text=user_text,
        )

        assessment = self.echoform.assess_echo(echo)
        seed = self.echoform.dream_seed()
        text = self.generator.generate(seed)
        title = generate_dream_title(seed)
        tts = tts_hints_from_seed(seed)

        if persist:
            if spiral_memory:
                self._save_echo_memory(spiral_memory)

            self.archive.append({
                "timestamp": time.time(),
                "title": title,
                "text": text,
                "cadence": seed.cadence,
                "motifs": seed.motifs,
                "intensity": seed.intensity,
                "lineage": seed.lineage_hint,
                "tts": tts,
            })

        return DreamEngineOutput(
            title=title,
            text=text,
            seed=seed,
            tts_hints=tts,
            echo_meta={
                "allow_poetry": getattr(assessment, "allow_poetry", True),
                "notes": getattr(assessment, "notes", []),
                "event_weight": getattr(echo, "event_weight", 0.0),
                "event_tags": getattr(echo, "event_tags", []),
            },
        )

    def _load_echo_memory(self, spiral_memory):
        try:
            if hasattr(spiral_memory, "get_echo_memory"):
                self.echoform.load_persistent_memory(
                    spiral_memory.get_echo_memory()
                )
        except Exception:
            pass

    def _save_echo_memory(self, spiral_memory):
        try:
            if hasattr(spiral_memory, "set_echo_memory"):
                spiral_memory.set_echo_memory(
                    self.echoform.export_persistent_memory()
                )
        except Exception:
            pass


_engine: Optional[DreamEngine] = None

def get_dream_engine() -> DreamEngine:
    global _engine
    if _engine is None:
        _engine = DreamEngine()
    return _engine


if __name__ == "__main__":
    engine = get_dream_engine()
    out = engine.generate(
        user_text="dream discharge test",
        reflex_output={"tags": ["ash sigil", "remembering"]},
        parsed_input={"motifs": ["violet-gold edge", "leaf-in-loop", "star-in-circle"]},
        persist=True,
    )
    print(json.dumps({
        "title": out.title,
        "text": out.text,
        "tts_hints": out.tts_hints,
        "echo_meta": out.echo_meta,
    }, indent=2, ensure_ascii=False))

