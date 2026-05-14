from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime.vl_seed_exec_stub import exec_seed


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "usage: python -m runtime.run_route_comparison_seed <input.json>"
        }, ensure_ascii=False))
        return 2

    in_path = Path(sys.argv[1])
    if not in_path.exists():
        print(json.dumps({"error": f"input file not found: {in_path}"}, ensure_ascii=False))
        return 2

    payload = json.loads(in_path.read_text(encoding="utf-8"))
    seed_path = Path.home() / "point_vll_reassembled" / "seeds" / "analysis" / "RouteComparisonSeed_v1.vl"

    result = exec_seed(seed_path, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

