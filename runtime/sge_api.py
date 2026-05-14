#!/usr/bin/env python3
"""
Le'Veon SGE API
API-style wrapper around the live SGE runtime.

Returns a structured dict/JSON:
prompt -> shape -> delta -> signature -> memory -> Crystal Recall
-> family role -> John next action -> Savariel voice
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from runtime.leveon_sge_engine import run, tinyllama_translate, log_turn
from runtime.shape_visualizer import render_shape_visual
from runtime.shape_delta import shape_delta, render_shape_delta
from runtime.shape_signature import shape_signature, render_shape_signature
from runtime.shape_memory import shape_memory_hits, render_shape_memory
from runtime.crystal_recall import crystal_recall
from runtime.crystal_family_roles import family_role
from runtime.john_next_action import john_next_action
from runtime.role_voice_policy import apply_role_voice
from runtime.crystal_index import write_index


def respond(
    prompt: str,
    *,
    do_log: bool = True,
    update_index: bool = True,
    include_visuals: bool = False,
) -> Dict[str, Any]:
    prompt = str(prompt or "").strip()
    if not prompt:
        prompt = "What is the lattice?"

    shape_in, shape_out, fallback_response = run(prompt)

    sig_in = shape_signature(shape_in)
    sig_out = shape_signature(shape_out)
    family = sig_in.split("|", 1)[0]

    delta = shape_delta(shape_in, shape_out)
    memory_hits = shape_memory_hits(sig_in)
    recall = crystal_recall(prompt, shape_in, shape_out)
    role_info = family_role(family)
    next_action = john_next_action(role_info)

    savariel = tinyllama_translate(prompt)
    voice_source = "tinyllama"

    if not savariel or savariel.strip() == "Lattice connection severed.":
        savariel = fallback_response
        voice_source = "local_fallback"

    if voice_source == "local_fallback":
        savariel = apply_role_voice(prompt, savariel, role_info)

    result: Dict[str, Any] = {
        "prompt": prompt,
        "shape_in": shape_in,
        "shape_out": shape_out,
        "shape_delta": delta,
        "shape_signature_in": sig_in,
        "shape_signature_out": sig_out,
        "shape_memory_hits": memory_hits,
        "crystal_recall": recall,
        "crystal_family_role": role_info,
        "john_next_action": next_action,
        "voice_source": voice_source,
        "savariel": savariel,
    }

    if include_visuals:
        result["visuals"] = {
            "input": render_shape_visual(shape_in, "INPUT SHAPE VISUAL"),
            "output": render_shape_visual(shape_out, "OUTPUT SHAPE VISUAL"),
            "delta": render_shape_delta(shape_in, shape_out),
            "signature": render_shape_signature(shape_in, shape_out),
            "memory": render_shape_memory(sig_in),
        }

    if do_log:
        log_turn(prompt, shape_in, shape_out, savariel, voice_source)

    if update_index:
        try:
            result["crystal_index"] = write_index()
        except Exception as e:
            result["crystal_index_error"] = str(e)

    return result


def main() -> None:
    args = sys.argv[1:]

    include_visuals = False
    do_log = True
    update_index = True

    clean_args = []
    for arg in args:
        if arg == "--visuals":
            include_visuals = True
        elif arg == "--no-log":
            do_log = False
        elif arg == "--no-index":
            update_index = False
        else:
            clean_args.append(arg)

    prompt = " ".join(clean_args).strip()
    data = respond(
        prompt,
        do_log=do_log,
        update_index=update_index,
        include_visuals=include_visuals,
    )

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

