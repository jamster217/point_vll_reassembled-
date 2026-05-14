from pathlib import Path
import json, time, hashlib

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "var" / "lattice" / "render_decision_adapter_v124.jsonl"

def _load(path, fallback=None):
    try:
        p = Path(path)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def load_decision_context():
    """
    Load/build V12.3 render decision context.
    This does not rewrite source.
    """
    try:
        from runtime.render_decision_context_v123 import build_render_decision_context
        return build_render_decision_context()
    except Exception as e:
        fallback = _load(ROOT / "var" / "lattice" / "render_decision_context_v123.json", {})
        if isinstance(fallback, dict) and fallback:
            fallback.setdefault("adapter_warning", repr(e))
            return fallback
        return {
            "active": False,
            "tags": [],
            "weights": {},
            "render_policy": {
                "complexity_mode": "preserve_and_refine",
                "source_protected": True,
                "personal_memory_confirmation_required": True,
            },
            "render_hints": [],
            "error": repr(e),
            "law": "v124_no_decision_context_available",
        }

def summarize_decision(decision):
    decision = decision if isinstance(decision, dict) else {}
    policy = decision.get("render_policy", {}) if isinstance(decision.get("render_policy", {}), dict) else {}
    tags = decision.get("tags", []) if isinstance(decision.get("tags", []), list) else []
    hints = decision.get("render_hints", []) if isinstance(decision.get("render_hints", []), list) else []

    return {
        "complexity_mode": policy.get("complexity_mode", "preserve_and_refine"),
        "tags": tags[:16],
        "hints": hints[:6],
        "preserve_white_ash": policy.get("preserve_white_ash_containment", True),
        "preserve_virellion": policy.get("preserve_virellion_thread", True),
        "personal_memory_confirmation_required": policy.get("personal_memory_confirmation_required", True),
        "source_protected": policy.get("source_protected", True),
        "law": "v124_render_decision_summary",
    }

def adapt_prompt_for_rendering(prompt):
    decision = load_decision_context()
    summary = summarize_decision(decision)

    mode = summary.get("complexity_mode", "preserve_and_refine")
    tags = ", ".join(summary.get("tags", [])[:16])
    hints = " | ".join(summary.get("hints", [])[:6])

    context = (
        "\n\n[V12.4_RENDER_DECISION_CONTEXT]\n"
        f"complexity_mode={mode}\n"
        f"weighted_tags={tags}\n"
        f"render_hints={hints}\n"
        "rules=preserve white_ash containment; preserve virellion thread; "
        "keep inferred personal memory unconfirmed unless John confirms; source protected.\n"
    )

    if mode == "simplify_next_render":
        context += (
            "visual_instruction=simplify the next render; strengthen boundary rings; "
            "reduce noisy glyph density; keep the central anchor readable.\n"
        )
    elif mode == "increase_boundary_clarity":
        context += (
            "visual_instruction=increase containment clarity; strengthen boundary rings; "
            "keep structure steady and readable.\n"
        )
    else:
        context += (
            "visual_instruction=preserve the current pattern and refine it gently.\n"
        )

    adapted = str(prompt).rstrip() + context

    packet = {
        "ts": time.time(),
        "prompt_hash": hashlib.sha256(str(prompt).encode()).hexdigest()[:12],
        "mode": mode,
        "summary": summary,
        "law": "v124_prompt_adapted_by_render_decision_context",
    }

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")

    return {
        **packet,
        "adapted_prompt": adapted,
    }

def render_prompt_image_with_decision(prompt, anchor="92162077"):
    """
    Optional wrapper if a caller wants direct render.
    Uses base renderer if available to avoid recursion.
    """
    try:
        from runtime.prompt_image_renderer_v107 import _render_prompt_image_base_v124 as render_prompt_image
    except Exception:
        from runtime.prompt_image_renderer_v107 import render_prompt_image

    packet = adapt_prompt_for_rendering(prompt)
    event = render_prompt_image(packet.get("adapted_prompt", prompt), anchor=anchor)

    if isinstance(event, dict):
        event["v124_render_decision"] = packet.get("summary")
        event["v124_law"] = "rendered_with_v123_decision_context"

    return event

if __name__ == "__main__":
    packet = adapt_prompt_for_rendering("test render decision context")
    print(json.dumps(packet.get("summary"), indent=2, ensure_ascii=False))

