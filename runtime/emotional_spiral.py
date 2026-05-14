#!/usr/bin/env python3
from pathlib import Path
import json, time, re

STATE = Path("var/dream/emotional_spiral_state.json")
MEMORY = Path("var/dream/emotional_spiral_memory.jsonl")

LEXICON = {
    "grief": ["grief", "sad", "loss", "ache", "heavy", "miss"],
    "fear": ["fear", "afraid", "panic", "threat", "unsafe"],
    "hope": ["hope", "light", "gold", "return", "found"],
    "awe": ["awe", "star", "wonder", "sacred", "vast"],
    "calm": ["calm", "soft", "quiet", "still", "gentle"],
    "memory": ["remember", "memory", "past", "old", "again"],
}

def _load():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {"dream": {"resonance": {}}, "last_symbol": None, "last_field": None}

def _save(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state

def dream_decode(text):
    low = str(text or "").lower()
    scores = {}
    for symbol, words in LEXICON.items():
        scores[symbol] = sum(1 for w in words if re.search(rf"\b{re.escape(w)}\b", low))
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "soft_dream"

def lattice_resonate(symbol):
    fields = {
        "grief": {"pull": 0.82, "memory": 0.78, "release": 0.18},
        "fear": {"boundary": 0.86, "risk": 0.74, "release": 0.12},
        "hope": {"flow": 0.74, "light": 0.82, "release": 0.55},
        "awe": {"novelty": 0.76, "memory": 0.52, "flow": 0.62},
        "calm": {"stability": 0.72, "flow": 0.44, "release": 0.38},
        "memory": {"memory": 0.88, "pull": 0.55, "continuity": 0.73},
        "soft_dream": {"flow": 0.45, "memory": 0.45, "release": 0.30},
    }
    return fields.get(symbol, fields["soft_dream"])

def sample(text):
    symbol = dream_decode(text)
    field = lattice_resonate(symbol)
    return symbol, field

def absorb(text):
    state = _load()
    symbol, field = sample(text)

    resonance = state.get("dream", {}).get("resonance", {})
    resonance[symbol] = round(float(resonance.get(symbol, 0.0)) + 1.0, 3)

    state = {
        "dream": {"resonance": resonance},
        "last_symbol": symbol,
        "last_field": field,
        "spiral_memory_absorb": {
            "symbol": symbol,
            "field": field,
            "source": "emotional_spiral",
        },
        "updated_at": time.time(),
    }

    _save(state)

    MEMORY.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "text": text,
            "symbol": symbol,
            "field": field,
            "updated_at": state["updated_at"],
        }, ensure_ascii=False) + "\n")

    return state

if __name__ == "__main__":
    import sys
    text = " ".join(sys.argv[1:]) or "I remember the ache but something gentle is returning"
    print(json.dumps(absorb(text), indent=2, ensure_ascii=False))

