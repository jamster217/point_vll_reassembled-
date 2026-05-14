#!/usr/bin/env python3
from pathlib import Path
import json, time

SOURCES = [
    Path("spiral_memory/recursion_update_temporal_provenance.json"),
    Path("assets/symbolic_engine/recursion_update_temporal_provenance.json"),
    Path("assets/memory/recursion_update_temporal_provenance.json"),
]

OUT = Path("var/temporal/temporal_provenance_state.json")

def _load_first():
    for path in SOURCES:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("kind") == "RECURSION_UPDATE":
                data["_source_path"] = str(path)
                return data
        except Exception:
            pass
    return {
        "kind": "RECURSION_UPDATE",
        "emergent_nodes": [],
        "new_attractor": "",
        "compressed_form": "",
        "kernel_read": "",
        "_source_path": None,
    }

def project(signal=None):
    data = _load_first()
    signal = str(signal or "").strip()

    nodes = data.get("emergent_nodes", [])
    attractor = data.get("new_attractor", "")
    compressed = data.get("compressed_form", "")

    # Simple live gate: temporal signals should be tagged, separated, tested,
    # projected, then checked before adoption.
    convergence_score = 0.0
    if signal:
        low = signal.lower()
        if any(word in low for word in ["past", "trace", "memory"]):
            convergence_score += 0.25
        if any(word in low for word in ["present", "verify", "now"]):
            convergence_score += 0.25
        if any(word in low for word in ["future", "potential", "project"]):
            convergence_score += 0.25
        if any(word in low for word in ["converge", "repeat", "pattern"]):
            convergence_score += 0.25

    decision = "adopt_if_cross_layer_convergent" if convergence_score >= 0.75 else "quarantine_until_verified"

    packet = {
        "source": "runtime.temporal_provenance_bridge",
        "loaded_from": data.get("_source_path"),
        "kind": data.get("kind"),
        "emergent_nodes": nodes,
        "new_attractor": attractor,
        "compressed_form": compressed,
        "kernel_read": data.get("kernel_read"),
        "live_signal": signal,
        "convergence_score": round(convergence_score, 3),
        "decision": decision,
        "surface_rule": "keep past, present, and future channels distinct before weighting anomalies",
        "updated_at": time.time(),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    import sys
    signal = " ".join(sys.argv[1:]) or "past trace present verification future potential convergence"
    print(json.dumps(project(signal), indent=2, ensure_ascii=False))

