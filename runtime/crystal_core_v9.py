#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, time, hashlib

STATE = Path("var/crystal/crystal_core_v9_state.json")
LOG = Path("symbolic_memory/crystal_core_v9_log.jsonl")

def _load_previous():
    try:
        data = json.loads(STATE.read_text(encoding="utf-8"))
        crystals = data.get("crystals", [])
        return crystals if isinstance(crystals, list) else []
    except Exception:
        return []

def _hash_pattern(pattern):
    raw = json.dumps(pattern, sort_keys=True, ensure_ascii=False) + str(time.time())
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def _pattern_key(pattern):
    return json.dumps(pattern, sort_keys=True, ensure_ascii=False)

def detect_stable(resonance):
    scores = resonance.get("scores", []) if isinstance(resonance, dict) else []
    stable = []
    for item in scores:
        try:
            score = float(item.get("score", 0))
            pattern = item.get("pattern")
        except Exception:
            continue
        if score >= 2 and pattern is not None:
            stable.append(pattern)
    return stable

def build_crystals(stable_patterns):
    now = time.time()
    return [
        {
            "id": _hash_pattern(pattern),
            "pattern": pattern,
            "timestamp": now,
        }
        for pattern in stable_patterns
    ]

def merge_with_previous(new_crystals, previous_crystals=None):
    previous = list(previous_crystals or [])
    seen = {_pattern_key(c.get("pattern")) for c in previous if isinstance(c, dict)}

    for c in new_crystals:
        key = _pattern_key(c.get("pattern"))
        if key not in seen:
            previous.append(c)
            seen.add(key)

    return previous

def run(resonance=None, previous_crystals=None):
    resonance = resonance or {
        "scores": [
            {"score": 2.4, "pattern": {"token": "white_ash", "tone": "sovereign_constellation"}},
            {"score": 1.2, "pattern": {"token": "passing_noise", "tone": "unstable"}},
            {"score": 2.1, "pattern": {"token": "anchor_signal_alignment", "tone": "truth_binding"}},
        ]
    }

    previous = previous_crystals if previous_crystals is not None else _load_previous()
    stable_patterns = detect_stable(resonance)
    new_crystals = build_crystals(stable_patterns)
    merged = merge_with_previous(new_crystals, previous)

    packet = {
        "source": "runtime.crystal_core_v9",
        "stable_patterns": stable_patterns,
        "new_crystals": new_crystals,
        "crystals": merged,
        "crystal_count": len(merged),
        "updated_at": time.time(),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")

    return packet

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))

