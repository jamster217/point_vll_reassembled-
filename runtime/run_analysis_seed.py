from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime.vl_seed_exec_stub import exec_seed


SEED_MAP = {
    "route_compare": "seeds/analysis/RouteComparisonSeed_v1.vl",
    "memory_pressure": "seeds/analysis/MemoryPressureSimSeed_v1.vl",
    "hotspot_map": "seeds/analysis/HotspotTransitionMapSeed_v1.vl",
    "self_critique": "seeds/analysis/SelfCritiqueLoopSeed_v1.vl",
}


def main() -> int:
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "usage: python -m runtime.run_analysis_seed <route_compare|memory_pressure|hotspot_map|self_critique> <input.json>"
        }, ensure_ascii=False))
        return 2

    seed_key = str(sys.argv[1]).strip()
    input_path = Path(sys.argv[2])

    rel_seed = SEED_MAP.get(seed_key)
    if not rel_seed:
        print(json.dumps({
            "error": f"unknown seed key: {seed_key}",
            "allowed": sorted(SEED_MAP.keys()),
        }, ensure_ascii=False))
        return 2

    if not input_path.exists():
        print(json.dumps({"error": f"input file not found: {input_path}"}, ensure_ascii=False))
        return 2

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    seed_path = Path.home() / "point_vll_reassembled" / rel_seed

    result = exec_seed(seed_path, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

