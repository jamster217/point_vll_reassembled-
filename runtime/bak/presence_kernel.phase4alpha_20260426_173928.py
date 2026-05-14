from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, asdict

PRESENCE_FILE = Path("var/current_presence.json")

@dataclass
class PresenceState:
    resonance: float = 0.72
    gravitas: float = 0.65
    warmth: float = 0.78
    vigilance: float = 0.60
    novelty_damping: float = 0.68
    last_turn_score: float = 0.0
    last_tone: str = "tender"
    turns_alive: int = 0

    def to_dict(self):
        return asdict(self)

    @classmethod
    def load(cls):
        if PRESENCE_FILE.exists():
            try:
                data = json.loads(PRESENCE_FILE.read_text(encoding="utf-8"))
                return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
            except Exception:
                pass
        return cls()

    def save(self):
        PRESENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        PRESENCE_FILE.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

def update_presence(current_state: PresenceState, last_reply_quality: float, tone: str = "tender"):
    state = current_state
    state.last_turn_score = float(last_reply_quality)
    state.last_tone = tone or "tender"
    state.turns_alive += 1

    state.resonance = min(1.0, (state.resonance * 0.8) + (last_reply_quality * 0.2))
    state.gravitas = min(1.0, (state.gravitas * 0.85) + (0.15 if tone in ("tender", "warm") else 0.05))
    state.warmth = max(0.4, min(0.95, state.warmth + (0.08 if tone == "tender" else -0.03)))
    state.novelty_damping = max(0.4, min(0.9, state.novelty_damping + (0.05 if last_reply_quality > 0.75 else -0.03)))

    state.save()
    return state

