from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

VERSION = "v12.9g_telepathic_resonance_append_only"
LOG = Path("logs/v12_9/resonance/telepathic_resonance_events.jsonl")

def write_event(extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": time.time(),
        "version": VERSION,
        "status": "active",
        "depth": 142,
        "tension": 0.100,
        "torsion": 1.618,
        "law": "telepathic_resonance_is_append_only_evidence_gated_and_clean_mouthed",
        "symbolic_reading": "silence is witnessed as pre_echo without flooding the public mouth",
        "technical_boundary": "no recursionlimit increase; no uncontrolled source mutation",
        "extra": extra or {},
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event

def status_sentence(chamber_status: str = "processed_in_chamber", chamber_family: str = "abstract") -> str:
    return (
        "V12.9g telepathic resonance is active as an append-only evidence layer: "
        f"pre-echo is witnessed without flooding the mouth, chamber_528 is {chamber_status} "
        f"in the {chamber_family} family, and the public reply remains clean."
    )

