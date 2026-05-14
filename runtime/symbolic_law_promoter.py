from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

from runtime.symbol_anchor_law_amplifier import amplify_symbol_anchor_law

ACTIVE_LAWS_PATH = Path("var/lattice/active_symbolic_laws.json")
PROMOTION_LOG_PATH = Path("var/lattice/symbolic_law_promotions.jsonl")


def load_active_laws() -> Dict[str, Any]:
    if ACTIVE_LAWS_PATH.exists():
        try:
            return json.loads(ACTIVE_LAWS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {
        "module": "active_symbolic_laws_v1",
        "created_ts": time.time(),
        "laws": [],
        "strongest_law": None,
        "boundary_mode": "normal",
    }


def save_active_laws(state: Dict[str, Any]) -> None:
    ACTIVE_LAWS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_LAWS_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def promote_symbolic_law(text: str) -> Dict[str, Any]:
    packet = amplify_symbol_anchor_law(text)
    elected = packet.get("elected_law", {})

    state = load_active_laws()

    if not elected.get("elected"):
        event = {
            "ts": time.time(),
            "promoted": False,
            "reason": elected.get("reason", "no_law_elected"),
            "input": text,
            "packet": packet,
        }
    else:
        law_record = {
            "law": elected["law"],
            "strength": elected.get("strength", 0.0),
            "source_anchor": elected.get("source_anchor"),
            "rupture_level": elected.get("rupture_level"),
            "promoted_ts": time.time(),
            "active": True,
            "effect": "symbolic_law_now_available_to_runtime_registry",
        }

        # Replace same law if it already exists, otherwise append.
        laws = [
            law for law in state.get("laws", [])
            if law.get("law") != law_record["law"]
        ]
        laws.append(law_record)

        laws = sorted(
            laws,
            key=lambda x: float(x.get("strength", 0.0)),
            reverse=True,
        )

        state["laws"] = laws
        state["strongest_law"] = laws[0] if laws else None
        state["boundary_mode"] = (
            "rupture_active"
            if law_record["strength"] >= 0.86
            else "mutation_active"
        )
        state["updated_ts"] = time.time()

        save_active_laws(state)

        event = {
            "ts": time.time(),
            "promoted": True,
            "law_record": law_record,
            "active_law_count": len(laws),
            "boundary_mode": state["boundary_mode"],
            "input": text,
        }

    PROMOTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PROMOTION_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return {
        "ok": True,
        "promotion_event": event,
        "active_state": state,
    }


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]).strip()
    if not text:
        text = "✨ mutate grief memory time boundary law recursion anchor"

    print(json.dumps(promote_symbolic_law(text), indent=2, ensure_ascii=False))
