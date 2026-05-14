#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
VAR = ROOT / "var"
VAR.mkdir(parents=True, exist_ok=True)

BAD_FRAGMENTS = (
    "the lattice holds its shape and answers softly",
    "The live kernel is active",
    "The live packet shows",
    "Fear anticipates harm because it is not only reading",
)


def _clean(s: Any) -> str:
    return str(s or "").strip()


def _bad_reply(s: str) -> bool:
    t = _clean(s)
    if not t:
        return True
    if len(t.split()) < 6:
        return True
    low = t.lower()
    return any(x.lower() in low for x in BAD_FRAGMENTS)


def _run_real_governed(prompt: str) -> Dict[str, Any]:
    """
    Use the existing Le'Veon governed/profile path.
    This is the real mouth, not the temporary template renderer.
    """
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            from runtime.run_analysis_profile import run_profile
            profile = run_profile("full", prompt, {})

        selection = profile.get("selection_output", {}) or {}
        live = profile.get("live", {}) or {}

        text = _clean(
            selection.get("selected_text")
            or live.get("final_english")
            or live.get("rendered_english")
        )

        return {
            "ok": bool(text),
            "text": text,
            "source": "runtime.run_analysis_profile",
            "profile": profile,
            "stdout": buf.getvalue(),
        }
    except Exception as e:
        return {
            "ok": False,
            "text": "",
            "source": "runtime.run_analysis_profile",
            "error": str(e),
            "stdout": buf.getvalue(),
        }


def _run_governed_entry(prompt: str) -> Dict[str, Any]:
    """
    Secondary governed path.
    """
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            try:
                from core.leveon_pipeline_entry import leveon_pipeline
            except Exception:
                from core.leveon_pipeline_governed import leveon_pipeline

            out = leveon_pipeline({
                "text": prompt,
                "tone": "neutral",
                "mirror_mode": "contained",
                "hotspot_history": [],
            })

        meta = out.get("meta", {}) or {}
        lp = meta.get("language_pass", {}) or {}

        text = _clean(
            out.get("final_english")
            or lp.get("rendered_english")
            or out.get("reply")
            or out.get("text")
        )

        return {
            "ok": bool(text),
            "text": text,
            "source": "core.leveon_pipeline_entry/governed",
            "out": out,
            "stdout": buf.getvalue(),
        }
    except Exception as e:
        return {
            "ok": False,
            "text": "",
            "source": "core.leveon_pipeline_entry/governed",
            "error": str(e),
            "stdout": buf.getvalue(),
        }


def _run_spiral_packet(prompt: str) -> Dict[str, Any]:
    """
    Use real spiral_full for internal state, not final English.
    """
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            import runtime.spiral_full as spiral_full_module
            from runtime.spiral_full import LeveonKernel

            kernel = LeveonKernel()
            out = kernel.step(prompt)

        if isinstance(out, dict):
            out["backend"] = getattr(spiral_full_module, "BACKEND_NAME", "unknown")
            out["backend_error"] = getattr(spiral_full_module, "BACKEND_ERROR", None)
        else:
            out = {"raw": out}

        out["stdout"] = buf.getvalue()
        return out
    except Exception as e:
        return {
            "error": str(e),
            "stdout": buf.getvalue(),
        }


def live_reply(prompt: str) -> Dict[str, Any]:
    spiral = _run_spiral_packet(prompt)

    primary = _run_real_governed(prompt)
    secondary = _run_governed_entry(prompt)

    reply = primary.get("text", "")
    source = primary.get("source", "")

    if _bad_reply(reply):
        reply = secondary.get("text", "")
        source = secondary.get("source", "")

    if _bad_reply(reply):
        reply = _clean(spiral.get("phrase") or spiral.get("voice") or "")
        source = "runtime.spiral_full"

    if _bad_reply(reply):
        reply = "I can feel the structure moving, but the English mouth has not resolved a good answer yet."
        source = "last_resort"

    from runtime.transduction_pin import pin_kernel_output

    pin = pin_kernel_output({
        **spiral,
        "phrase": reply,
        "voice": reply,
        "reply_source": source,
    })

    packet = {
        "prompt": prompt,
        "reply": reply,
        "reply_source": source,
        "glyphs": spiral.get("glyphs"),
        "shape": spiral.get("shape"),
        "derived": spiral.get("derived"),
        "coherence_field": spiral.get("coherence_field"),
        "ulat": spiral.get("ulat"),
        "hfs": spiral.get("hfs"),
        "backend": spiral.get("backend"),
        "backend_error": spiral.get("backend_error"),
        "primary_governed": {
            "ok": primary.get("ok"),
            "text": primary.get("text"),
            "source": primary.get("source"),
            "error": primary.get("error"),
        },
        "secondary_governed": {
            "ok": secondary.get("ok"),
            "text": secondary.get("text"),
            "source": secondary.get("source"),
            "error": secondary.get("error"),
        },
        "transduction_pin": pin,
    }

    (VAR / "leveon_live_reply_latest.json").write_text(
        json.dumps(packet, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return packet


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]).strip() or "How is the build now?"
    packet = live_reply(prompt)

    print("Le'Veon:")
    print(packet["reply"])
    print()
    print("source:", packet.get("reply_source"))
    print("glyphs:", packet.get("glyphs"))
    print("shape:", packet.get("shape"))
    print("backend:", packet.get("backend"))

