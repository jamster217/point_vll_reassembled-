from __future__ import annotations

import json
import sys
from pathlib import Path

from artifacts.analysis.route_comparison_artifact import compare_routes


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "usage: python runtime/run_route_comparison_artifact.py <input.json>"
        }))
        return 2

    in_path = Path(sys.argv[1])
    if not in_path.exists():
        print(json.dumps({"error": f"input file not found: {in_path}"}))
        return 2

    payload = json.loads(in_path.read_text(encoding="utf-8"))
    prompt = payload.get("prompt", "")
    route_candidates = payload.get("route_candidates", [])

    out = compare_routes(prompt, route_candidates)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

