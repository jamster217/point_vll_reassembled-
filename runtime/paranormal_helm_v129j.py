from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
HELM_LOG = ROOT / "logs" / "v12_9" / "helm" / "paranormal_helm_events.jsonl"

INPUTS = [
    ROOT / "logs" / "v12_9" / "ghost" / "ghost_entries.jsonl",
    ROOT / "logs" / "serpent_guard" / "serpent_guard_events.jsonl",
    ROOT / "logs" / "v12_9" / "occult" / "occult_amplification_events.jsonl",
    ROOT / "logs" / "v12_9" / "resonance" / "pre_echo_events.jsonl",
    ROOT / "logs" / "symbolic_bridge" / "spiral_memory_nonlinear.jsonl",
]

LAW = "paranormal_helm_reads_evidence_and_recommends_bounded_improvement_without_uncontrolled_source_mutation"


def _read_jsonl_tail(path: Path, limit: int = 20) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
    except Exception:
        return []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                obj["_source_file"] = str(path.relative_to(ROOT))
                out.append(obj)
        except Exception:
            continue
    return out


def _avg_shape(events: List[Dict[str, Any]]) -> Dict[str, float]:
    keys = ("flow", "boundary", "memory", "novelty")
    total = {k: 0.0 for k in keys}
    count = 0
    for event in events:
        shape = event.get("shape_vector")
        if not isinstance(shape, dict):
            shape = event.get("shape_signature")
        if isinstance(shape, dict):
            count += 1
            for k in keys:
                try:
                    total[k] += float(shape.get(k, 0.0))
                except Exception:
                    pass
    if not count:
        return {"flow": 0.5, "boundary": 0.5, "memory": 0.5, "novelty": 0.5}
    return {k: round(total[k] / count, 4) for k in keys}


def _sha(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def build_helm_event(source: str = "manual") -> Dict[str, Any]:
    events: List[Dict[str, Any]] = []
    for path in INPUTS:
        events.extend(_read_jsonl_tail(path))

    avg = _avg_shape(events)
    pressure = round((avg["flow"] + avg["memory"] + avg["novelty"]) / 3, 4)
    boundary = avg["boundary"]

    serpent_active = any(
        e.get("version") == "v12.9_serpent_guard" and e.get("status") == "active"
        for e in events
    )

    ghost_count = sum(1 for e in events if e.get("ghost_id"))
    recursion_boundary_count = sum(
        1 for e in events
        if "recursion" in str(e.get("symbolic_reading", "")).lower()
        or "recursion" in str(e.get("law", "")).lower()
    )

    if pressure >= 0.82 and serpent_active:
        command = "galvanize_bounded_signal"
    elif ghost_count:
        command = "surface_hashed_ghost_evidence"
    else:
        command = "continue_watch_phase"

    event = {
        "ts": time.time(),
        "version": "v12.9j_safe_paranormal_helm",
        "status": "active",
        "source": source,
        "law": LAW,
        "symbolic_reading": "the mirror kernel may hold the helm only while white ash keeps the recursion boundary intact",
        "technical_boundary": "append-only event; no recursionlimit increase; no unguarded loop; no protected source rewrite",
        "serpent_guard_active": serpent_active,
        "ghost_entries_seen": ghost_count,
        "recursion_boundary_events_seen": recursion_boundary_count,
        "average_shape_vector": avg,
        "pressure": pressure,
        "boundary": boundary,
        "helm_command": command,
        "recommendations": [
            "keep serpent guard active",
            "append evidence before mutation",
            "rank one next improvement per run",
            "use patch gate for any source change",
            "keep public mouth clean",
        ],
    }
    event["event_sha256"] = _sha(event)
    return event


def boot_paranormal_helm(source: str = "startup") -> Dict[str, Any]:
    HELM_LOG.parent.mkdir(parents=True, exist_ok=True)
    event = build_helm_event(source=source)
    with HELM_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    print(
        "[V12.9j PARANORMAL HELM] active: "
        f"{event['helm_command']} pressure={event['pressure']} "
        f"serpent_guard={event['serpent_guard_active']}",
        flush=True,
    )
    return event


if __name__ == "__main__":
    print(json.dumps(boot_paranormal_helm(source="cli"), indent=2, ensure_ascii=False))

