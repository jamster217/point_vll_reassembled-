from __future__ import annotations

from typing import Any, Dict
import re

CLEAN_REQUEST_MARKERS = (
    "one clean sentence",
    "one sentence",
    "single sentence",
    "short answer",
    "answer only",
    "just answer",
    "clean sentence",
    "without exposing",
    "no scaffold",
    "no telemetry",
    "no metrics",
    "concise",
)

NOISY_REPLY_MARKERS = (
    "[TRUE MEANING KERNEL]",
    "[AUTOGENOUS TOPOLOGY NODE",
    "image=static/generated/",
    "prompt_image=",
    "score=",
    "…already forming…",
    "The old hidden thing is becoming",
)


def _clean_text(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _first_sentence(x: str) -> str:
    x = _clean_text(x)
    if not x:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", x, maxsplit=1)
    return parts[0].strip()


def _wants_clean(prompt: str) -> bool:
    low = _clean_text(prompt).lower()
    return any(m in low for m in CLEAN_REQUEST_MARKERS)


def _is_noisy(reply: str) -> bool:
    return any(m.lower() in str(reply or "").lower() for m in NOISY_REPLY_MARKERS)


def apply_clean_mouth_v12(prompt: str, data: Dict[str, Any]) -> tuple[Dict[str, Any], bool]:
    """
    V12 clean mouth selector:
    For prompts requesting one clean sentence / answer-only output,
    choose the clean voice/plain text lane over topology/autogenous expansion.
    Preserve all spine/thermal metadata underneath.
    """
    if not isinstance(data, dict):
        return data, False

    prompt = str(prompt or "")
    reply = str(data.get("reply") or data.get("response") or data.get("answer") or "")

    if not _wants_clean(prompt):
        return data, False

    voice_plain = ""
    voice = data.get("voice")
    if isinstance(voice, dict):
        voice_plain = _clean_text(voice.get("plain_text"))

    text_plain = _clean_text(data.get("text"))
    candidate = voice_plain or text_plain

    if not candidate:
        candidate = reply

    candidate = _first_sentence(candidate)

    if not candidate:
        return data, False

    # For ghost heartbeat confirmations, make the sentence actually answer the prompt.
    low_prompt = prompt.lower()
    thermal = data.get("thermal_heartbeat")
    if "ghost heartbeat" in low_prompt and isinstance(thermal, dict):
        entropy = thermal.get("entropy")
        pulse = thermal.get("pulse")
        if pulse == "active":
            candidate = f"The ghost heartbeat is active, with finite entropy currently reading {entropy}."

    changed = candidate != reply or _is_noisy(reply)

    data["answer"] = candidate
    data["reply"] = candidate
    data["response"] = candidate
    data["clean_mouth_v12"] = {
        "active": True,
        "changed_reply": changed,
        "law": "one_clean_sentence_prompts_choose_clean_public_mouth_preserve_spine",
    }

    spine = data.setdefault("spine", {})
    if isinstance(spine, dict):
        spine["clean_mouth_v12"] = data["clean_mouth_v12"]

    return data, changed

