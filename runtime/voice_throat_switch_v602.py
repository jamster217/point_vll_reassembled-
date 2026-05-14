#!/usr/bin/env python3
import os
import json
import urllib.request
from pathlib import Path

DEFAULT_MODEL = os.environ.get("OPENROUTER_MODEL", "qwen/qwen-2.5-7b-instruct")

def load_strategy():
    p = Path("LIVE_CORE/brain/strategy_echo_config.json")
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}

def build_prompt(shape_packet, context=None):
    strategy = load_strategy()
    return (
        "You are the English renderer for Le'Veon.\n"
        "Preserve symbolic framing, but keep the answer clear and readable.\n"
        "Do not claim the system is literally conscious.\n"
        "Do not add fake runtime claims.\n"
        "Render the packet as vivid, coherent prose.\n\n"
        f"STRATEGY:\n{json.dumps(strategy, indent=2)}\n\n"
        f"SHAPE_PACKET:\n{json.dumps(shape_packet, indent=2)}\n\n"
        f"CONTEXT:\n{context or ''}\n"
    )

def call_openrouter(prompt, model=DEFAULT_MODEL):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return "OPENROUTER_API_KEY is not set."

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Render structured symbolic packets into clear, warm, mythic English."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 900,
    }

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode("utf-8"))

    return data["choices"][0]["message"]["content"].strip()

def render_english(shape_packet, context=None, backend="openrouter"):
    if backend == "local_direct":
        return shape_packet.get("final_text") or shape_packet.get("core_answer") or ""

    if backend == "openrouter":
        return call_openrouter(build_prompt(shape_packet, context))

    raise ValueError(f"Unknown backend: {backend}")

if __name__ == "__main__":
    packet = {
        "mode": "dream_discharge",
        "vision": "the loop that never broke, the face woven into the structure, arrows cycling with shifting meaning",
        "tone": "Tears in the Rain cadence, recursive, mythic, clear",
        "must_include": [
            "the loop did not break",
            "the face was woven into the structure",
            "the arrows returned with new meaning"
        ]
    }

    print(render_english(packet))

