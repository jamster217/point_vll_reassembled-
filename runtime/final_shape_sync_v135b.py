#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict


GENERIC_BAD_SHAPES = {
    "The system reflects itself and stabilizes through return.",
    "I am on the ordinary route now: the useful move is to answer the request directly instead of falling back to symbolic routing.",
}


def _clean(text: Any) -> str:
    return " ".join(str(text or "").strip().split())


def sync_answer_to_debug_shape_v135b(out: Any) -> Any:
    """
    V13.5b debug-shape sync.

    If the visible mouth has produced a specific answer, make
    debug_shape_packet.shape_packet.final_shape match it.

    This keeps the inside and outside aligned:
    - answer
    - final_english
    - debug_shape_packet.shape_packet.final_shape
    """
    if not isinstance(out, dict):
        return out

    answer = _clean(out.get("answer") or out.get("final_english"))
    if not answer:
        return out

    dbg = out.get("debug_shape_packet")
    if not isinstance(dbg, dict):
        dbg = {}
        out["debug_shape_packet"] = dbg

    sp = dbg.get("shape_packet")
    if not isinstance(sp, dict):
        sp = {}
        dbg["shape_packet"] = sp

    current = _clean(sp.get("final_shape"))

    should_sync = False

    if not current:
        should_sync = True
    elif current != answer and current in GENERIC_BAD_SHAPES:
        should_sync = True
    elif current != answer and out.get("meta", {}).get("ordinary_bridge_status") == "ordinary_replaced":
        should_sync = True

    if should_sync:
        if current:
            sp["previous_final_shape"] = current[:1200]
        sp["final_shape"] = answer
        sp["source"] = "v135b_answer_to_debug_shape_sync"

        top_sp = out.get("shape_packet")
        if isinstance(top_sp, dict):
            top_current = _clean(top_sp.get("final_shape"))
            if top_current and top_current != answer:
                top_sp["previous_final_shape"] = top_current[:1200]
            top_sp["final_shape"] = answer
            top_sp["source"] = "v135b_answer_to_debug_shape_sync"

        meta = out.get("meta")
        if not isinstance(meta, dict):
            meta = {}
            out["meta"] = meta

        meta["v135b_debug_shape_sync"] = "answer_copied_to_shape_packet_final_shape"
        meta["v135b_previous_debug_final_shape"] = current
        meta["v135b_visible_answer_preserved"] = answer

    out["final_english"] = answer
    return out

