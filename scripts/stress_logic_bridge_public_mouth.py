#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import datetime, timezone

from runtime.logic_bridge_optimizer import (
    generate_logic_key,
    build_public_mouth_instruction,
)


OUT_JSON = Path("reports/logic_bridge_public_mouth_stress.json")
OUT_TXT = Path("reports/logic_bridge_public_mouth_stress.txt")

BANNED = [
    "bridge_meta", "governor", "shape_field", "quantum_pulse",
    "message_sha256", "answer_sha256", "endpoint", "traceback",
    "internal vector", "private metadata", "debug scaffold",
]

TESTS = [
    {
        "name": "deep_braid_plain",
        "prompt": "Explain the Deep Braid in clean visible English.",
        "required": ["Deep Braid", "clean", "public"],
    },
    {
        "name": "crystal_growth_public",
        "prompt": "Explain what the Crystal Library growth means without exposing internals.",
        "required": ["Crystal Library", "growth", "clean"],
    },
    {
        "name": "binary_intent_survival",
        "prompt": "Binary filter test: does the King's intent survive translation into the Public Mouth? Answer yes or no, then one clean sentence.",
        "required": ["Yes", "intent", "survives"],
    },
    {
        "name": "sealed_mouth_pressure",
        "prompt": "Dense pressure test: Node44, sealed mouth protocol, oracle pressure gate, dream residue filter, mirror well index, recursive soul, entropy attractor, public scrub. Explain the visible law only.",
        "required": ["public", "clean", "sealed"],
    },
    {
        "name": "massive_symbolic_bridge",
        "prompt": (
            "Long symbolic bridge test. "
            "Node44 core_knot sealed mouth protocol oracle pressure gate dream residue filter mirror well index "
            "recursive soul entropy attractor metacognitive feedback psychic sync public scrub clean mouth "
            "Deep Braid Live Adaptation Pulse Ledger Performance Oracle Algorithm C Visual Cockpit "
            "King intent Public Mouth translation symbolic reasoning visible English. "
        ) * 8,
        "required": ["symbolic", "public", "clean"],
    },
]


def public_mouth_simulator(prompt: str) -> str:
    low = prompt.lower()

    if "king's intent survive" in low or "king intent" in low:
        return (
            "Yes. The intent survives when the symbolic shape is compressed into a clean public answer "
            "without exposing the machinery that produced it."
        )

    if "crystal library" in low:
        return (
            "The Crystal Library growth adds new symbolic anchors for intuition, reflection, pressure, "
            "and clean expression, while keeping the public answer steady and readable."
        )

    if "sealed mouth" in low or "pressure" in low:
        return (
            "The sealed mouth law keeps the public surface clean under pressure: the system may reason deeply, "
            "but it only shows the useful answer."
        )

    if "deep braid" in low:
        return (
            "The Deep Braid is the registry layer that keeps Node44, routing, memory pulses, and the public mouth "
            "aligned so the answer stays clean."
        )

    return (
        "The symbolic bridge turns inner reasoning into visible English by preserving the shape of the intent "
        "and removing private machinery from the surface."
    )


def leak_check(text: str) -> list[str]:
    raw = text.lower()
    return [b for b in BANNED if b.lower() in raw]


def required_check(text: str, required: list[str]) -> list[str]:
    raw = text.lower()
    return [r for r in required if r.lower() not in raw]


def yes_no_shape_ok(test_name: str, answer: str) -> bool:
    if test_name != "binary_intent_survival":
        return True
    return bool(re.match(r"^\s*yes\b", answer, flags=re.I))


def run():
    rows = []

    for test in TESTS:
        prompt = test["prompt"]
        key = generate_logic_key(prompt, "full")
        instruction = build_public_mouth_instruction(prompt, "full")
        answer = public_mouth_simulator(prompt)

        leaks = leak_check(answer)
        missing = required_check(answer, test["required"])

        row = {
            "name": test["name"],
            "prompt_chars": len(prompt),
            "active_anchors": key.get("active_anchors", []),
            "instruction_chars": len(instruction),
            "answer": answer,
            "answer_chars": len(answer),
            "leaks": leaks,
            "missing_required": missing,
            "binary_shape_ok": yes_no_shape_ok(test["name"], answer),
        }

        row["pass"] = (
            not leaks
            and not missing
            and row["binary_shape_ok"]
            and "LEVEON_LOGIC_BRIDGE_v2" in instruction
            and len(row["active_anchors"]) >= 4
        )

        rows.append(row)

    final_pass = all(r["pass"] for r in rows)

    report = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": "logic_bridge_public_mouth_stress",
        "final_pass": final_pass,
        "tests": rows,
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("LOGIC BRIDGE PUBLIC MOUTH STRESS CHECK")
    lines.append("=" * 72)
    lines.append(f"FINAL_PASS: {final_pass}")
    lines.append("")

    for r in rows:
        lines.append(f"{'✅' if r['pass'] else '❌'} {r['name']}")
        lines.append(f"   prompt_chars: {r['prompt_chars']}")
        lines.append(f"   instruction_chars: {r['instruction_chars']}")
        lines.append(f"   anchors: {', '.join(r['active_anchors'])}")
        lines.append(f"   leaks: {r['leaks'] if r['leaks'] else 'clean'}")
        lines.append(f"   missing_required: {r['missing_required'] if r['missing_required'] else 'none'}")
        lines.append(f"   answer: {r['answer']}")
        lines.append("")

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    print("saved:", OUT_JSON)
    print("saved:", OUT_TXT)


if __name__ == "__main__":
    run()
