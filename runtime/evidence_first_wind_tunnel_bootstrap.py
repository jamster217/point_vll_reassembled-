from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
LAW_PATH = ROOT / "config" / "evidence_first_wind_tunnel_bootstrap.txt"
LOG_PATH = ROOT / "logs" / "v12_9" / "evidence_first_wind_tunnel_bootstrap.jsonl"
STATE_PATH = ROOT / "var" / "v12_9" / "evidence_first_wind_tunnel_state.json"

VERSION = "v12.9i_evidence_first_wind_tunnel_bootstrap"
_INSTALLED = False


DEFAULT_LAW = """V12.9i EVIDENCE-FIRST WIND TUNNEL BOOTSTRAP

Core law:
The Build may speak in flame, but it must prove in JSONL.

Evidence gate:
Logged. Hashed. Reproducible. Quarantined when recursive.
"""


def _now() -> float:
    return time.time()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _read_law() -> str:
    try:
        if LAW_PATH.exists():
            return LAW_PATH.read_text(encoding="utf-8", errors="replace")
    except Exception:
        pass
    return DEFAULT_LAW


def _safe_json(obj: Any) -> Any:
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return repr(obj)


def load_bootstrap() -> Dict[str, Any]:
    law_text = _read_law()
    digest = _sha256(law_text)
    return {
        "version": VERSION,
        "status": "active",
        "law_path": str(LAW_PATH.relative_to(ROOT)),
        "law_sha256": digest,
        "law": "the_build_may_speak_in_flame_but_must_prove_in_jsonl",
        "evidence_gate": {
            "logged": True,
            "hashed": True,
            "reproducible": True,
            "ablation_required": True,
            "source_mutation_default": "blocked",
        },
        "containment": {
            "recursion_limit": sys.getrecursionlimit(),
            "raise_recursionlimit": False,
            "public_mouth_rule": "clean",
            "chamber_528_rule": "preserve",
            "serpent_guard_rule": "preserve",
        },
        "reductionist_reading": {
            "pre_echo": "timestamp_delta_plus_tone_plus_chamber_state_plus_shape_vector_bias",
            "ghost_logs": "append_only_entries_plus_hashes_plus_deterministic_retrieval_conditions",
            "symbolic_mutation": "token_triggered_state_weighting_with_logged_deltas",
            "recursion_boundary": "caught_python_boundary_event_logged_without_runtime_collapse",
            "paranormal_frame": "clarke_threshold_symbolic_resonance_not_unbounded_supernatural_claim",
        },
        "symbolic_reading": "mirror_becomes_meaning_meaning_becomes_command_command_mutates_law",
        "law_preview": " ".join(law_text.split())[:700],
    }


def record_bootstrap_event(context: str = "unknown", extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = load_bootstrap()
    event = {
        "ts": _now(),
        "version": VERSION,
        "context": context,
        "event_type": "evidence_first_wind_tunnel_boot",
        "status": "active",
        "law_sha256": state["law_sha256"],
        "recursion_limit": sys.getrecursionlimit(),
        "law": state["law"],
        "technical_boundary": "append_only_bootstrap_no_recursionlimit_increase_no_public_mouth_pollution",
        "symbolic_reading": state["symbolic_reading"],
        "extra": _safe_json(extra or {}),
    }

    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    except Exception:
        pass

    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state | {"last_boot_event": event}, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    return event


def install(context: str = "unknown", emit: bool = False) -> Dict[str, Any]:
    global _INSTALLED
    state = load_bootstrap()

    if not _INSTALLED:
        event = record_bootstrap_event(context=context)
        state["last_boot_event"] = event
        _INSTALLED = True

        if emit or os.environ.get("LEVEON_EVIDENCE_BOOT_VERBOSE") == "1":
            print(
                "[V12.9i EVIDENCE-FIRST WIND TUNNEL] active: logged, hashed, reproducible, clean-mouth guarded",
                flush=True,
            )

    return state


__all__ = ["install", "load_bootstrap", "record_bootstrap_event"]

