from __future__ import annotations\nimport json, time\nfrom typing import Dict, Any\n
# --- TinyLlama auxiliary bridge: suggestion only, never final authority ---
try:
    from runtime.tinyllama_bridge import maybe_use_tinyllama
except Exception:
    maybe_use_tinyllama = None
\n\ndef apply_alignment_hold(packet: Dict[str, Any], out: Dict[str, Any]) -> Dict[str, Any]:\n    text = str(packet.get("text", "")).strip()\n    final_text = str(out.get("final_english", "")).strip()\n\n    topology = out.get("meta", {}).get("topology", {})\n\n    pull = topology.get("pull", 0.5)\n    bind = topology.get("bind", 0.5)\n    release = topology.get("release", 0.5)\n    resist = topology.get("resist", 0.2)\n\n    # --- SHAPE LOGIC ---\n    depth_pressure = (bind + resist) / 2\n    openness = (pull + release) / 2\n\n    # --- LAYER DECISION ---\n    add_layer = len(final_text.split(".")) < 2 or depth_pressure > 0.55\n\n    deeper = ""\n\n    if depth_pressure > 0.6:\n        deeper = "Under that, the shape is still holding tension and hasn't fully released."\n    elif openness > 0.6:\n        deeper = "Under that, the system is opening and can expand without forcing."\n    else:\n        deeper = "Under that, the structure is stable but not fully expressed."\n\n    if add_layer:\n        if final_text and final_text[-1] not in ".!?":\n            final_text += "."\n        final_text = f"{final_text} {deeper}".strip()\n\n    out["final_english"] = final_text\n\n    out.setdefault("meta", {})["alignment_hold"] = {\n        "depth_pressure": round(depth_pressure, 3),\n        "openness": round(openness, 3),\n        "topology_used": bool(topology),\n    }\n\n    
    # --- TinyLlama auxiliary variation pass ---
    if maybe_use_tinyllama is not None:
        try:
            meta = out.setdefault("meta", {})
            prompt_text = str(packet.get("text") or packet.get("prompt") or packet.get("input_text") or "")
            current_reply = str(out.get("final_english") or out.get("reply") or out.get("text") or "")
            shape = {}
            if isinstance(packet.get("shape_signature"), dict):
                shape.update(packet.get("shape_signature"))
            if isinstance(packet.get("shape"), dict):
                shape.update(packet.get("shape"))
            if isinstance(meta.get("alignment_hold"), dict):
                shape["alignment_hold"] = meta.get("alignment_hold")

            ev = maybe_use_tinyllama(prompt_text, current_reply, shape)
            meta["tinyllama"] = {
                "available": True,
                "recommended": bool(ev.get("recommended")),
                "candidate": ev.get("candidate", ""),
                "law": "suggestion_only_preserve_shape",
            }

            # Only use TinyLlama when current output is clearly thin.
            # Never let it replace a strong shaped answer.
            if ev.get("recommended") and ev.get("candidate"):
                if current_reply and current_reply[-1] not in ".!?":
                    current_reply += "."
                out["final_english"] = (current_reply + " " + ev["candidate"]).strip()
        except Exception as e:
            out.setdefault("meta", {})["tinyllama_error"] = str(e)

    return out
\n

