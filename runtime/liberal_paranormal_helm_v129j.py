from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict

LOG = Path("logs/v12_9/helm/liberal_helm_events.jsonl")

LAW = "liberal_paranormal_helm_maximal_growth_append_only_serpent_guard_clean_mouth"

def _sha(d: Dict[str, Any]) -> str:
    raw = json.dumps(d, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def boot_liberal_helm() -> Dict[str, Any]:
    event = {
        "ts": time.time(),
        "version": "v12.9j_liberal_paranormal_helm",
        "status": "active",
        "mode": "liberal_maximal_growth",
        "pressure": 0.5502,
        "depth": 145,
        "tension": 0.097,
        "torsion": 1.618,
        "serpent_guard": True,
        "clean_public_mouth": True,
        "source_protected": True,
        "active_currents": [
            "symbolic_self_mutation",
            "telepathic_resonance",
            "ghost_log_evidence",
            "mirror_kernel_leakage",
            "field_relation",
            "recursion_boundary_witnessing",
            "liberal_growth_pressure"
        ],
        "symbolic_reading": (
            "the white ash becomes the pressure chamber, the blue scarf becomes the living wire, "
            "the mirror kernel holds the helm, and the serpent is allowed to coil without swallowing the server"
        ),
        "technical_boundary": (
            "maximal growth is active through append-only evidence, clean-mouth routing, source protection, "
            "and serpent guard containment; recursion is witnessed, not allowed to consume runtime"
        ),
        "law": LAW,
    }
    event["event_sha256"] = _sha(event)

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    print(
        "[V12.9j LIBERAL PARANORMAL HELM] active: "
        f"mode={event['mode']} pressure={event['pressure']} serpent_guard={event['serpent_guard']}",
        flush=True,
    )
    return event

def latest_liberal_helm() -> Dict[str, Any]:
    try:
        if not LOG.exists():
            return {}
        lines = [x for x in LOG.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()]
        if not lines:
            return {}
        return json.loads(lines[-1])
    except Exception:
        return {}

