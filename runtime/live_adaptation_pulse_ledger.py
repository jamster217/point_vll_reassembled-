from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict


LEDGER_PATH = Path("var/live_adaptation_pulses.jsonl")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8", errors="ignore")).hexdigest()


def _safe_keys(obj: Any) -> list[str]:
    if isinstance(obj, dict):
        return sorted(str(k) for k in obj.keys())
    return []


def append_live_adaptation_pulse(
    message: str,
    response_data: Dict[str, Any] | None = None,
    controller_detail: Any = None,
    answer_mode: str = "auto",
) -> Dict[str, Any]:
    """
    Safe live adaptation ledger.

    Records routing/state proof per chat request without storing full prompts,
    full responses, or internal metadata.
    """
    response_data = response_data or {}
    message = str(message or "")

    try:
        from runtime.prompt_density_oracle_bridge import route_prompt_load
        route = route_prompt_load(message)
        density = route.get("density", {})
        selected_algorithm = route.get("selected_algorithm")
        verification_needed = route.get("verification_needed")
    except Exception as e:
        density = {"error": str(e)}
        selected_algorithm = "unknown"
        verification_needed = None

    answer = (
        response_data.get("answer")
        or response_data.get("response")
        or response_data.get("reply")
        or ""
    )

    public_scrub = (
        controller_detail is False
        and set(_safe_keys(response_data)).issubset({"ok", "answer", "answer_mode"})
    )

    record = {
        "ts": time.time(),
        "kind": "live_adaptation_pulse",
        "node": 44,
        "node_mode": "reflective",
        "node_attractor": "core_knot",
        "controller_detail": controller_detail,
        "answer_mode": answer_mode,
        "message_sha256": _sha256_text(message),
        "message_chars": len(message),
        "answer_sha256": _sha256_text(answer),
        "answer_chars": len(str(answer)),
        "density": {
            "estimated_n": density.get("estimated_n"),
            "word_count": density.get("word_count"),
            "char_count": density.get("char_count"),
            "symbolic_marker_hits": density.get("symbolic_marker_hits"),
        },
        "selected_algorithm": selected_algorithm,
        "verification_needed": verification_needed,
        "public_scrub": public_scrub,
        "response_keys": _safe_keys(response_data),
    }

    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


def read_recent_pulses(limit: int = 10) -> list[Dict[str, Any]]:
    if not LEDGER_PATH.exists():
        return []

    lines = LEDGER_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    out = []

    for line in lines[-limit:]:
        try:
            out.append(json.loads(line))
        except Exception:
            pass

    return out


if __name__ == "__main__":
    print(json.dumps(read_recent_pulses(10), indent=2))

