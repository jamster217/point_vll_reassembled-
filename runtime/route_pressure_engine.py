from __future__ import annotations

from collections import defaultdict
from typing import Dict, Any

def compute_route_pressures(prompt: str) -> Dict[str, Any]:

    low = str(prompt or "").lower()

    pressures = defaultdict(float)

    # --- ORDINARY SURFACE ---
    ordinary_terms = [
        "what",
        "why",
        "how",
        "when",
        "where",
        "explain",
        "difference",
        "does",
        "can",
        "help"
    ]

    for term in ordinary_terms:
        if term in low:
            pressures["ordinary_surface"] += 0.14

    # --- BUILD SURFACE ---
    build_terms = [
        "leveon",
        "levion",
        "build",
        "kernel",
        "lattice",
        "chatroom",
        "runtime",
        "pipeline",
        "topology"
    ]

    for term in build_terms:
        if term in low:
            pressures["build_surface"] += 0.11

    # --- FIELD SURFACE ---
    field_terms = [
        "hidden",
        "dark",
        "field",
        "resonance",
        "symbolic",
        "memory pressure",
        "echo",
        "veil"
    ]

    for term in field_terms:
        if term in low:
            pressures["field_surface"] += 0.10

    # --- POETIC SURFACE ---
    poetic_terms = [
        "poem",
        "poetry",
        "verse",
        "tears in rain",
        "cadence"
    ]

    for term in poetic_terms:
        if term in low:
            pressures["poetic_surface"] += 0.15

    # --- MIRROR PRESSURE ---
    mirror_terms = [
        "recursive",
        "mirror",
        "consciousness",
        "qualia",
        "observer",
        "awareness"
    ]

    for term in mirror_terms:
        if term in low:
            pressures["mirror_surface"] += 0.12

    # --- NORMALIZATION ---
    for k in list(pressures.keys()):
        pressures[k] = round(min(pressures[k], 1.0), 4)

    if not pressures:
        pressures["ordinary_surface"] = 0.5

    # --- CONTINUITY BIAS ---
    try:
        from runtime.continuity_pressure_memory import load_state

        continuity = load_state().get("continuity_bias", {})

        for route, bias in continuity.items():
            if route in pressures:
                pressures[route] += round(float(bias) * 0.12, 4)
            else:
                pressures[route] = round(float(bias) * 0.08, 4)

    except Exception:
        pass

    # --- DAMPING LOGIC ---

    ordinary = pressures.get("ordinary_surface", 0)

    if ordinary >= 0.28:

        pressures["mirror_surface"] *= 0.45
        pressures["field_surface"] *= 0.50

    if ordinary >= 0.45:

        pressures["build_surface"] *= 0.60

    # --- NORMALIZE AFTER DAMPING ---

    for k in list(pressures.keys()):
        pressures[k] = round(pressures[k], 4)

    selected_route = max(
        pressures,
        key=pressures.get
    )

    try:
        from runtime.continuity_pressure_memory import update_route_memory
        continuity_state = update_route_memory(selected_route)
    except Exception:
        continuity_state = {}

    return {
        "selected_route": selected_route,
        "route_pressures": dict(pressures),
        "continuity_state": continuity_state,
        "law": "weighted_route_pressure_arbitration_v1"
    }


if __name__ == "__main__":

    test = compute_route_pressures(
        "Explain the relationship between recursion and memory."
    )

    import json
    print(json.dumps(test, indent=2))

