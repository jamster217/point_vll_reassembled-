from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


DEFAULT_SPEC_PATH = Path("config/algorithm_performance_routing.json")


def load_performance_spec(path: str | Path = DEFAULT_SPEC_PATH) -> Dict[str, Any]:
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8"))


def choose_algorithm(n: int | float, spec: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Adaptive performance selector.

    Routing law:
    - N < 100  -> Algorithm B
    - N >= 100 -> Algorithm C

    Algorithm C is flagged for verification because its timing decreases
    at large N, which may indicate caching, batching, vectorization, warmup,
    or measurement artifact.
    """
    spec = spec or load_performance_spec()
    n = float(n)

    if n < 100:
        algorithm = "Algorithm B"
        reason = "Small input: Algorithm B is fastest at N=10 in the benchmark."
        verification_needed = False
    else:
        algorithm = "Algorithm C"
        reason = "Medium/large input: Algorithm C is fastest for N >= 100 in the benchmark."
        verification_needed = True

    return {
        "input_size": n,
        "selected_algorithm": algorithm,
        "reason": reason,
        "verification_needed": verification_needed,
        "chart_id": spec.get("chart", {}).get("id"),
        "routing_rule": spec.get("routingRule", {})
    }


def summarize_routing() -> str:
    spec = load_performance_spec()
    interp = spec.get("interpretation", {})
    return (
        "Performance routing active. "
        "Use Algorithm B for N < 100. "
        "Use Algorithm C for N >= 100. "
        f"Note: {interp.get('problemDetected', '')}"
    )


if __name__ == "__main__":
    for n in [10, 50, 100, 1000, 10000]:
        print(json.dumps(choose_algorithm(n), indent=2))

