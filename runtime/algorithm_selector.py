import re
import json
import datetime
from pathlib import Path

from runtime.pulse_context_reader import latest_pulse_context
from runtime.english_mouth import shape_from_prompt, realize, grammar_candidates
from runtime.wind_tunnel_adapter import wind_tunnel_integrate
from runtime.shape_compound_memory import find_nearest_shape
from runtime.birth_point_mapper import build_birth_packet

LOG_PATH = Path("runtime/logs/algorithm_selector.log")

BAD_PHRASES = [
    "savariel answers",
    "akasha echo",
    "crystal library injected",
    "the answer stays plain",
    "symbolic machinery",
    "direct answer:",
    "current state:",
    "works as a",
    "stays continuous while the situation changes",
    "same thing moving through time instead of resetting",
]

def _words(text):
    return re.findall(r"[a-zA-Z']+", text.lower())

def _overlap_score(prompt, reply):
    p = set(_words(prompt))
    r = set(_words(reply))
    if not p:
        return 0.0
    return len(p & r) / max(1, len(p))

def _badness(reply):
    low = reply.lower()
    return sum(1 for p in BAD_PHRASES if p in low)

def _clarity(reply):
    words = _words(reply)
    if not words:
        return 0.0
    if len(words) < 8:
        return 0.35
    if len(words) > 180:
        return 0.55
    return 1.0

def _beauty(reply):
    words = _words(reply)
    if not words:
        return 0.0
    concrete = {"love","memory","time","loss","change","bond","absence","pressure","pattern","return","thread","build","lattice"}
    return min(1.0, 0.35 + (len(set(words) & concrete) * 0.12))

def _score(prompt, reply):
    return (
        0.40 * _clarity(reply)
        + 0.30 * _overlap_score(prompt, reply)
        + 0.20 * _beauty(reply)
        - 0.25 * _badness(reply)
    )

def _mouth_plain(prompt, pulse, shape):
    return realize(prompt, pulse_context=pulse, show_shape=False)

def _mouth_shape(prompt, pulse, shape):
    subject = shape.get("subject", "this")
    relations = shape.get("relations", [])

    if not relations:
        return f"{subject.capitalize()} carries the main pressure of the prompt."

    primary = relations[0].replace("-", " ")
    rest = [r.replace("-", " ") for r in relations[1:]]

    if rest:
        return f"{subject.capitalize()} begins in {primary}, then bends through {', '.join(rest)}."
    return f"{subject.capitalize()} gathers around {primary} and turns that pressure into a usable answer."

def _mouth_reasoning(prompt, pulse, shape):
    subject = shape.get("subject", "this")
    relations = shape.get("relations", [])

    if not relations:
        return f"{subject.capitalize()} is the main pressure in the prompt, and the answer follows that pressure into plain English."

    rel = relations[0]

    if len(relations) > 1:
        tail = " while also carrying " + ", ".join(relations[1:])
    else:
        tail = ""

    return (
        f"{subject.capitalize()} moves through {rel}{tail}. "
        f"It keeps the prior pulse present without repeating it, so the meaning can continue forward in clear English."
    )

def _mouth_poetic(prompt, pulse, shape):
    subject = shape.get("subject", "the line")
    relations = shape.get("relations", [])
    rel = relations[0] if relations else "meaning"

    return (
        f"{subject.capitalize()} moves through {rel}: "
        f"not as a fixed label, but as a pressure that keeps returning with a slightly changed face."
    )

def _mouth_wind(prompt, pulse, shape):
    packet = wind_tunnel_integrate("John-co-creator-sigil", prompt)
    return str(packet.get("wind_tuned", "")).strip()

def generate_candidates(prompt):
    pulse = latest_pulse_context(max_chars=1800)
    shape = shape_from_prompt(prompt, pulse_context=pulse)
    memory_match = find_nearest_shape(prompt, shape)
    birth_packet = build_birth_packet(prompt, pulse_context=pulse, memory_match=memory_match)

    candidates = [
        ("plain_mouth", _mouth_plain(prompt, pulse, shape)),
        ("shape_mouth", _mouth_shape(prompt, pulse, shape)),
        ("reasoning_mouth", _mouth_reasoning(prompt, pulse, shape)),
        ("poetic_mouth", _mouth_poetic(prompt, pulse, shape)),
        ("wind_tunnel", _mouth_wind(prompt, pulse, shape)),
    ]

    for gname, greply, _gshape in grammar_candidates(prompt, pulse_context=pulse, birth_packet=birth_packet):
        candidates.append((f"grammar_{gname}", greply))

    scored = []
    for name, reply in candidates:
        scored.append({
            "name": name,
            "score": round(_score(prompt, reply), 4),
            "reply": reply,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {
        "prompt": prompt,
        "pulse_used": pulse[:800],
        "shape": shape,
        "birth_packet": birth_packet,
        "memory_match": memory_match,
        "candidates": scored,
        "winner": scored[0],
    }

def select_best_reply(prompt):
    result = generate_candidates(prompt)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": datetime.datetime.now().isoformat(),
            **result
        }, ensure_ascii=False) + "\n")

    return result

