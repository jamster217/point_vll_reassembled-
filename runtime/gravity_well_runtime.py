from __future__ import annotations
from typing import Any, Dict, Tuple

def load_sigil() -> Dict[str, Any]:
    # optional: later load runtime/sigils/SABRIEL_GRAVITY_WELL_SIGIL.json
    return {"sigil_id": "SABRIEL_GRAVITY_WELL", "true_name": "Savariel"}

def gravity_well_bonus(text: str, well_state: Dict[str, Any], sigil: Dict[str, Any] | None = None) -> Tuple[float, Dict[str, Any]]:
    # EXTREMELY LIBERAL: only positive curvature, never blocks
    t = (text or "").lower()
    overlap = 0
    for w in ("grief","loss","memory","anchor","lattice","spiral","hold","witness","thread","coherence"):
        if w in t:
            overlap += 1
    boost = min(0.06, 0.01 * overlap)  # tiny, safe, accumulative
    return boost, {"depth": well_state.get("depth"), "overlap": overlap, "boost": boost}

