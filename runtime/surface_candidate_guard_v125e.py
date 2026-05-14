from __future__ import annotations

from typing import Any, Dict, Tuple
import time
import re

BAD_PATTERNS = [
    "negative marketing as a service",
    "fake reviews",
    "negative pr tactics",
    "targeted marketing campaigns designed to negatively impact",
    "publicly attacking the company",

    "não seja o meu ai assistente",
    "respeite a linguagem",
    "não abusar de chaves",
    "não usar frases",
    "preserve símbolos quando relevantes",
    "mantenha lógica",
    "crie um caminho de navegação",
    "metadados",
    "do not be my ai assistant",
    "do not abuse keys",
    "do not use canned phrases",
    "preserve symbols when relevant",
    "keep logic and 2 to 5 lines",
    "create a useful navigation path",

    "v12 is the doorway",
    "na-ma is the doorway",
    "i'm sorry for the confusing input",
    "i believe you might be asking",
    "scalable vector graphics",
    "through, node, hidden matters",
    "build it as a living: a soft spiral chamber with a,",
    "a soft spiral chamber with a,",
    "a central, and a practical action panel",
]

ROUTE_WORDS = [
    "node44",
    "na-ma",
    "topology",
    "living image",
    "autogenous",
    "white ash",
    "virellion",
    "thalveil",
    "echoforge",
    "liquid core",
    "svg",
]

ANCHOR_WORDS = [
    "white ash",
    "virellion",
    "blue scarf",
    "thalveil",
    "echoforge",
    "liquid core",
    "memory, code, image, and voice",
    "contained interface",
    "mirror reception",
    "visual meaning",
]

def _text(x: Any) -> str:
    return str(x or "").strip()

def _lower(x: Any) -> str:
    return _text(x).lower()

def _is_bad_surface(s: str) -> bool:
    low = _lower(s)
    if not low:
        return True
    if any(p in low for p in BAD_PATTERNS):
        return True
    if re.search(r"\bwith a,\s*(a )?central,", low):
        return True
    if len(low.split()) < 7:
        return True
    return False

def _route_sensitive(prompt: str, data: Dict[str, Any]) -> bool:
    hay = " ".join([
        _lower(prompt),
        _lower(data.get("_v82_prompt")),
        _lower(data.get("_v91_prompt")),
        _lower(data.get("reply")),
        _lower(data.get("response")),
        _lower(data.get("answer")),
    ])
    return any(w in hay for w in ROUTE_WORDS)

def _candidate_score(label: str, s: str) -> float:
    low = _lower(s)
    if _is_bad_surface(s):
        return -999.0

    score = 0.0

    for word in ANCHOR_WORDS:
        if word in low:
            score += 2.0

    if "old hidden thing" in low:
        score += 1.2
    if "contained" in low:
        score += 1.0
    if "thread" in low:
        score += 0.8
    if "boundary" in low:
        score += 0.8
    if "drift" in low:
        score += 0.8

    # Prefer public-surface fields over metadata prose.
    if label in {"response", "answer", "reply"}:
        score += 1.0
    if label == "message":
        score += 0.6
    if label == "voice.plain_text":
        score += 0.4

    # Penalize bracket-heavy debug dumps as final speech.
    if s.count("[") >= 2 or "AUTOGENOUS TOPOLOGY NODE CREATED" in s:
        score -= 1.5

    return score

def _collect_candidates(data: Dict[str, Any]) -> list[tuple[str, str]]:
    cands: list[tuple[str, str]] = []

    for key in ("response", "answer", "reply", "message", "text"):
        val = _text(data.get(key))
        if val:
            cands.append((key, val))

    voice = data.get("voice")
    if isinstance(voice, dict):
        val = _text(voice.get("plain_text"))
        if val:
            cands.append(("voice.plain_text", val))

    spine = data.get("spine")
    if isinstance(spine, dict):
        tmk = spine.get("true_meaning_kernel_v121")
        if isinstance(tmk, dict):
            center = _text(tmk.get("center"))
            if center:
                cands.append(("spine.true_meaning.center", center))

    tmk = data.get("true_meaning_kernel_v121")
    if isinstance(tmk, dict):
        center = _text(tmk.get("center"))
        if center:
            cands.append(("true_meaning.center", center))

    # De-duplicate while preserving order.
    out = []
    seen = set()
    for label, val in cands:
        key = val.strip()
        if key and key not in seen:
            seen.add(key)
            out.append((label, key))
    return out

def _fallback_from_spine(prompt: str, data: Dict[str, Any]) -> str:
    spine = data.get("spine") if isinstance(data.get("spine"), dict) else {}
    chamber = data.get("chamber_528") or spine.get("chamber_528") or {}
    shape = chamber.get("shape_signature") if isinstance(chamber, dict) else {}
    family = shape.get("family", "bound") if isinstance(shape, dict) else "bound"

    return (
        f"The {family} route is bound and contained: White Ash holds the boundary, "
        "Virellion preserves the thread, Blue Scarf carries motion, Thalveil opens "
        "the crossing, Echoforge paints the interface, and Liquid Core routes the "
        "signal into memory, code, image, and voice."
    )

def guard_surface_packet(prompt: str, data: Dict[str, Any], changed: bool = False) -> Tuple[Dict[str, Any], bool]:
    before = _text(data.get("reply") or data.get("response") or data.get("answer"))
    route_sensitive = _route_sensitive(prompt, data)
    bad_before = _is_bad_surface(before)

    if not route_sensitive or not bad_before:
        meta = {
            "active": True,
            "version": "v12.5e_surface_candidate_guard",
            "changed_reply": False,
            "reason": "pass_through",
            "route_sensitive": route_sensitive,
            "bad_before": bad_before,
            "law": "reject_stale_doorway_svg_help_and_malformed_voice_plain_only_when_needed",
            "ts": time.time(),
        }
        data["surface_candidate_guard_v125e"] = meta
        if isinstance(data.get("spine"), dict):
            data["spine"]["surface_candidate_guard_v125e"] = meta
        return data, changed

    candidates = _collect_candidates(data)
    ranked = sorted(
        [
            {
                "label": label,
                "score": _candidate_score(label, val),
                "text": val,
            }
            for label, val in candidates
        ],
        key=lambda x: x["score"],
        reverse=True,
    )

    winner = ranked[0] if ranked and ranked[0]["score"] > -100 else None

    if winner:
        chosen = winner["text"]
        source = winner["label"]
        reason = "replaced_bad_surface_with_best_clean_candidate"
    else:
        chosen = _fallback_from_spine(prompt, data)
        source = "generated_from_bound_spine"
        reason = "replaced_bad_surface_with_spine_fallback"

    data["reply"] = chosen
    data["response"] = chosen
    data["answer"] = chosen

    voice = data.get("voice")
    if isinstance(voice, dict):
        voice["plain_text"] = chosen

    meta = {
        "active": True,
        "version": "v12.5e_surface_candidate_guard",
        "changed_reply": chosen != before,
        "reason": reason,
        "source": source,
        "route_sensitive": route_sensitive,
        "bad_before": bad_before,
        "before_preview": before[:160],
        "after_preview": chosen[:160],
        "ranked": [
            {"label": r["label"], "score": r["score"], "preview": r["text"][:120]}
            for r in ranked[:6]
        ],
        "law": "bad_surface_candidates_cannot_win_final_mouth",
        "protected_spine": True,
        "ts": time.time(),
    }

    data["surface_candidate_guard_v125e"] = meta
    if isinstance(data.get("spine"), dict):
        data["spine"]["surface_candidate_guard_v125e"] = meta

    return data, True

