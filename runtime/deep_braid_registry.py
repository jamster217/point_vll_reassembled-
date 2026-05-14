from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


MANIFEST_PATH = Path("config/deep_braid_phase3_manifest.json")


def load_deep_braid_manifest(path: str | Path = MANIFEST_PATH) -> Dict[str, Any]:
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8"))


def deep_braid_status() -> Dict[str, Any]:
    manifest = load_deep_braid_manifest()

    return {
        "phase": manifest.get("phase"),
        "status": manifest.get("status"),
        "law": manifest.get("law"),
        "stable_components": sorted((manifest.get("stable_components") or {}).keys()),
        "public_surface": {
            "scrubbed": True,
            "keys": ["ok", "answer", "answer_mode"]
        },
        "routing": {
            "small_load": "Algorithm B",
            "dense_load": "Algorithm C"
        },
        "node44": {
            "active_node": 44,
            "mode": "reflective",
            "attractor": "core_knot"
        }
    }


def deep_braid_public_summary() -> str:
    return (
        "The Deep Braid is active as a registry layer. "
        "Node44 stabilizes the core, the Performance Oracle routes small and dense loads, "
        "and the public surface remains sealed to clean answer-only output."
    )


if __name__ == "__main__":
    print(json.dumps(deep_braid_status(), indent=2))

