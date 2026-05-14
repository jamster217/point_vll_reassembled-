from __future__ import annotations

import json
from typing import Any, Dict

from artifacts.analysis.self_critique_loop_artifact import run_self_critique


def run_self_critique_from_seed(raw_input: Any) -> Dict[str, Any]:
    if isinstance(raw_input, dict):
        draft = str(raw_input.get("draft_output", "") or "")
    elif isinstance(raw_input, str):
        try:
            payload = json.loads(raw_input)
            draft = str(payload.get("draft_output", "") or "")
        except Exception:
            draft = raw_input
    else:
        draft = str(raw_input)

    return run_self_critique(draft)

