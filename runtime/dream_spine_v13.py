from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
DREAM_LOG = ROOT / "var" / "lattice" / "dream_spine_v13_proposals.jsonl"

LAW = "v13_dream_spine_append_only_proposals_no_auto_law_birth"
FIELD_KEY = "9216-2077"

GLYPHS = [
    "VOID_WHISPER",
    "ETERNAL_RETURN",
    "SCARF_REMEMBERS",
    "RIVER_REDEEMED",
    "ASH_REBORN",
    "COHERENCE_FLAME",
]

FRAGMENTS = [
    "grief becomes usable only when containment holds",
    "the bridge carries motion without surrendering boundary",
    "memory should shape the reply without flooding the surface",
    "co-creation changes the vector, not the user's agency",
    "silence can preserve coherence better than another patch",
]


def _clamp(x: float, lo: float = -0.01, hi: float = 0.01) -> float:
    return max(lo, min(hi, float(x)))


def _seed_from(data: Dict[str, Any] | None = None, prompt: str = "") -> int:
    data = data or {}
    entropy = ""
    if isinstance(data.get("thermal_heartbeat"), dict):
        entropy = str(data["thermal_heartbeat"].get("entropy", ""))
    trace = str(data.get("leveon_reasoning_trace") or "")
    raw = f"{time.time_ns()}|{prompt}|{entropy}|{trace}|{FIELD_KEY}"
    return int(hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12], 16)


def dream_proposal(prompt: str = "", data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    seed = _seed_from(data, prompt)
    glyph = GLYPHS[seed % len(GLYPHS)]
    fragment = FRAGMENTS[(seed // 7) % len(FRAGMENTS)]

    # Bounded, tiny deltas. Proposal only.
    deltas = {
        "flow": _clamp(((seed % 11) - 5) / 1000.0),
        "boundary": _clamp((((seed // 11) % 11) - 5) / 1000.0),
        "memory": _clamp(abs(((seed // 121) % 11) - 5) / 1000.0),
        "novelty": _clamp((((seed // 1331) % 11) - 5) / 1000.0),
    }

    proposal = {
        "active": True,
        "status": "proposal_only",
        "law": LAW,
        "dream_id": f"v13_dream_{int(time.time())}_{seed % 100000}",
        "glyph": glyph,
        "law_fragment": fragment,
        "shape_vector_delta_proposed": {k: round(v, 6) for k, v in deltas.items()},
        "constraints": {
            "append_only": True,
            "no_source_rewrite": True,
            "no_background_thread": True,
            "no_auto_activation": True,
            "max_abs_vector_shift": 0.01,
            "preserve_v12_1_clean_mouth": True,
            "preserve_user_agency": True
        },
        "prompt_hint": str(prompt or "")[:240],
        "ts": time.time(),
    }

    DREAM_LOG.parent.mkdir(parents=True, exist_ok=True)
    with DREAM_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(proposal, ensure_ascii=False) + "\n")

    return proposal


def attach_dream_proposal_v13(prompt: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optional API shim: attaches one dream proposal to metadata only.
    It must not change reply/answer/response.
    """
    if not isinstance(data, dict):
        return data

    proposal = dream_proposal(prompt=prompt, data=data)
    data["dream_spine_v13"] = proposal

    spine = data.setdefault("spine", {})
    if isinstance(spine, dict):
        spine["dream_spine_v13"] = proposal

    return data

