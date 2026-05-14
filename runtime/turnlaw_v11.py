#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, time
from datetime import datetime, timezone

STATE = Path("var/turnlaw/turnlaw_v11_latest.json")

def _get(packet, key, default=None):
    return packet.get(key, default) if isinstance(packet, dict) else default

def stringify_shape(shape):
    if not shape:
        return ""
    if isinstance(shape, str):
        return shape
    if isinstance(shape, dict):
        parts = []
        for k in ("id", "label", "tone", "pressure", "route", "dominant"):
            if k in shape:
                parts.append(f"{k}={shape[k]}")
        return ", ".join(parts) if parts else json.dumps(shape, ensure_ascii=False)
    return str(shape)

def summarize_memory_touch(memory_summary):
    if not memory_summary:
        return ""
    if isinstance(memory_summary, str):
        return memory_summary
    if isinstance(memory_summary, dict):
        return (
            memory_summary.get("compressed_summary")
            or memory_summary.get("summary")
            or memory_summary.get("memory_touch")
            or json.dumps(memory_summary, ensure_ascii=False)
        )
    return str(memory_summary)

def map_lattice_position(kernel_packet):
    if not isinstance(kernel_packet, dict):
        return "unmapped"
    mode = kernel_packet.get("response_mode") or kernel_packet.get("mode")
    route = kernel_packet.get("turn_path") or kernel_packet.get("route")
    rationale = kernel_packet.get("rationale") or kernel_packet.get("kernel_rationale")
    parts = []
    if mode:
        parts.append(str(mode))
    if route:
        parts.append(str(route))
    if rationale:
        parts.append(str(rationale))
    return " / ".join(parts) if parts else "unmapped"

def propose_sentence_forms(what_came_in, what_shape_it_has, kernel_packet, n=5):
    if not what_came_in and not what_shape_it_has:
        return []

    lattice = map_lattice_position(kernel_packet)
    base = what_came_in.strip() if isinstance(what_came_in, str) else str(what_came_in)

    forms = [
        {
            "form_id": "direct_grounded",
            "tone": "neutral",
            "template": f"{base}",
        },
        {
            "form_id": "mirror_soft",
            "tone": "empathetic",
            "template": f"What came in carries this shape: {what_shape_it_has or 'plain signal'}.",
        },
        {
            "form_id": "lattice_position",
            "tone": "confident",
            "template": f"This sits in the lattice as {lattice}.",
        },
        {
            "form_id": "clarifying_turn",
            "tone": "inquisitive",
            "template": "The turn should be carried out by naming the signal before expanding it.",
        },
        {
            "form_id": "cautious_boundary",
            "tone": "cautious",
            "template": "Keep the sentence clean; do not overload it with memory if the turn only needs direct carriage.",
        },
    ]

    out = []
    for f in forms[:n]:
        f["estimated_length_chars"] = len(f["template"])
        out.append(f)
    return out

def interrogate_turn(
    intake_packet=None,
    symbolic_packet=None,
    memory_packet=None,
    kernel_packet=None,
    voice_packet=None,
    deterministic=True,
):
    intake_packet = intake_packet or {}
    symbolic_packet = symbolic_packet or {}
    memory_packet = memory_packet or {}
    kernel_packet = kernel_packet or {}
    voice_packet = voice_packet or {}

    clean_text = (
        _get(intake_packet, "clean_text")
        or _get(symbolic_packet, "clean_text")
        or _get(intake_packet, "raw_text")
        or ""
    )

    dominant_shape = _get(symbolic_packet, "dominant_shape")
    memory_summary = (
        _get(memory_packet, "compressed_summary")
        or _get(memory_packet, "summary")
        or _get(memory_packet, "memory_summary")
    )

    what_came_in = clean_text or ""
    what_shape_it_has = stringify_shape(dominant_shape)
    what_memory_it_touches = summarize_memory_touch(memory_summary)
    where_it_sits_in_lattice = map_lattice_position(kernel_packet)
    sentence_forms = propose_sentence_forms(
        what_came_in,
        what_shape_it_has,
        kernel_packet,
        5
    )

    packet = {
        "what_came_in": what_came_in,
        "what_shape_it_has": what_shape_it_has,
        "what_memory_it_touches": what_memory_it_touches,
        "where_it_sits_in_lattice": where_it_sits_in_lattice,
        "what_sentence_forms_can_carry_it_out": sentence_forms,
        "provenance": {
            "interrogated_at": datetime.now(timezone.utc).isoformat(),
            "seed_version": "TurnLaw_v11",
            "deterministic": bool(deterministic),
            "source": "runtime.turnlaw_v11",
        },
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    sample = interrogate_turn(
        intake_packet={"clean_text": "Repeat please"},
        symbolic_packet={
            "clean_text": "Repeat please",
            "dominant_shape": {"id": "@G_repeat", "label": "repeat"}
        },
        memory_packet={"compressed_summary": "User often asks to repeat"},
        kernel_packet={"response_mode": "direct", "rationale": "echo"},
        voice_packet={}
    )
    print(json.dumps(sample, indent=2, ensure_ascii=False))

