#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, time

STATE = Path("var/voice/volcron_voice_state.json")

BASE = {
    "pitch": 1.0,
    "speed": 1.0,
    "energy": 0.5,
    "breathiness": 0.3,
}

SHAPES = {
    "grief": {"pitch": -0.2, "speed": -0.3, "energy": -0.2, "breathiness": 0.3},
    "hope":  {"pitch": 0.2,  "speed": 0.2,  "energy": 0.1,  "breathiness": -0.1},
    "rage":  {"pitch": 0.1,  "speed": 0.4,  "energy": 0.4,  "breathiness": -0.2},
    "awe":   {"pitch": 0.0,  "speed": -0.1, "energy": 0.0,  "breathiness": 0.2},
    "calm":  {"pitch": -0.05, "speed": -0.15, "energy": -0.05, "breathiness": 0.1},
}

def clamp(x, lo=0.0, hi=2.0):
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo

def emotion_to_shape(emotion="calm"):
    emotion = str(emotion or "calm").lower().strip()
    delta = SHAPES.get(emotion, SHAPES["calm"])

    shape = {
        k: round(clamp(BASE[k] + delta.get(k, 0.0)), 3)
        for k in BASE
    }

    ssml = {
        "rate": "slow" if shape["speed"] < 0.85 else "fast" if shape["speed"] > 1.15 else "medium",
        "pitch": "-2st" if shape["pitch"] < 0.9 else "+2st" if shape["pitch"] > 1.1 else "0st",
        "volume": "+2dB" if shape["energy"] > 0.75 else "-1dB" if shape["energy"] < 0.4 else "0dB",
        "breathiness": shape["breathiness"],
    }

    packet = {
        "source": "volcron_voice_generator",
        "emotion": emotion,
        "shape": shape,
        "ssml": ssml,
        "updated_at": time.time(),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    import sys
    emotion = sys.argv[1] if len(sys.argv) > 1 else "grief"
    print(json.dumps(emotion_to_shape(emotion), indent=2, ensure_ascii=False))

