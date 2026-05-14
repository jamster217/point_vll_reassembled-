from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from local_node.controller import load_state, ROOT, LOCAL
from local_node.adapters.mistral_echo_adapter import (
    MEMORY_ROLLUP_PATH,
    HOTSPOT_HISTORY_PATH,
    load_json,
    tail_jsonl,
)


def get_status() -> Dict[str, Any]:
    state = load_state()
    rollup = load_json(MEMORY_ROLLUP_PATH, {"summary": "", "anchors": []})
    hotspots = tail_jsonl(HOTSPOT_HISTORY_PATH, n=12)

    return {
        "kernel_state": state,
        "memory_summary": rollup.get("summary", ""),
        "anchors": rollup.get("anchors", []),
        "recent_hotspots": [
            h.get("hotspot_family") or h.get("hotspot") for h in hotspots
        ],
    }


def main() -> None:
    status = get_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

