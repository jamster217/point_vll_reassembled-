import json
import sys
from runtime.artifact_logger import log_artifact

def run_route_compare(prompt, route_candidates=None):
    route_candidates = route_candidates or [
        {"route": "route_alpha", "score": 0.81},
        {"route": "route_beta", "score": 0.64},
        {"route": "route_gamma", "score": 0.72},
    ]
    ranked = sorted(route_candidates, key=lambda x: x.get("score", 0), reverse=True)
    return {
        "status": "ok",
        "seed": "RouteComparisonSeed_v1",
        "prompt": prompt,
        "routes": ranked,
        "best_route": ranked[0] if ranked else None,
        "weakest_route": ranked[-1] if ranked else None,
    }

def run_self_critique(draft_output):
    critique = {
        "clarity": "acceptable",
        "structure": "stable",
        "drift": "low",
        "notes": "Check whether phrasing can be tightened."
    }
    revised = f"{draft_output} [refined]"
    return {
        "status": "ok",
        "seed": "SelfCritiqueLoopSeed_v1",
        "original": draft_output,
        "critique": critique,
        "revised": revised,
    }

def run_memory_pressure(prompt):
    return {
        "status": "ok",
        "seed": "MemoryPressureSimSeed_v1",
        "prompt": prompt,
        "low": "low-memory response",
        "medium": "medium-memory response",
        "high": "high-memory response",
    }

def run_hotspot_map(hotspot_trace=None):
    hotspot_trace = hotspot_trace or ["H_1224", "H_1314", "H_2224", "H_1314"]
    pairs = list(zip(hotspot_trace, hotspot_trace[1:]))
    counts = {}
    for a, b in pairs:
        k = f"{a}->{b}"
        counts[k] = counts.get(k, 0) + 1
    dominant = max(counts, key=counts.get) if counts else None
    unstable = [k for k, v in counts.items() if v == 1]
    return {
        "status": "ok",
        "seed": "HotspotTransitionMapSeed_v1",
        "trace": hotspot_trace,
        "dominant_path": dominant,
        "unstable_transitions": unstable,
        "transition_counts": counts,
    }

def run_analysis_seed(seed_name, payload):
    name = str(seed_name).strip().lower()

    if name in ("route_compare", "routecomparison", "route"):
        prompt = payload if isinstance(payload, str) else payload.get("prompt", "sample prompt")
        routes = None if isinstance(payload, str) else payload.get("route_candidates")
        result = run_route_compare(prompt, routes)
        artifact = log_artifact("analysis_route_compare", result)
        return {"status": "ok", "artifact_path": artifact, "result": result}

    if name in ("self_critique", "critique", "selfcritique"):
        draft = payload if isinstance(payload, str) else payload.get("draft_output", "sample draft")
        result = run_self_critique(draft)
        artifact = log_artifact("analysis_self_critique", result)
        return {"status": "ok", "artifact_path": artifact, "result": result}

    if name in ("memory_pressure", "memorypressure", "memory"):
        prompt = payload if isinstance(payload, str) else payload.get("prompt", "sample prompt")
        result = run_memory_pressure(prompt)
        artifact = log_artifact("analysis_memory_pressure", result)
        return {"status": "ok", "artifact_path": artifact, "result": result}

    if name in ("hotspot_map", "hotspot", "transition_map"):
        trace = None if isinstance(payload, str) else payload.get("hotspot_trace")
        result = run_hotspot_map(trace)
        artifact = log_artifact("analysis_hotspot_map", result)
        return {"status": "ok", "artifact_path": artifact, "result": result}

    return {
        "status": "missing",
        "seed": seed_name,
        "notes": "Unknown analysis seed target."
    }

def main():
    seed_name = sys.argv[1] if len(sys.argv) > 1 else "route_compare"

    if len(sys.argv) > 2:
        raw = sys.argv[2]
        try:
            payload = json.loads(raw)
        except Exception:
            payload = raw
    else:
        payload = {"prompt": "sample prompt"}

    out = run_analysis_seed(seed_name, payload)
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

