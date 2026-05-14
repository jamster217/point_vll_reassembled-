import json
from pathlib import Path

def load_latest_shape():
    base = Path("var")

    # try multiple known sources
    candidates = [
        base / "lattice" / "autogenous_v106_full_self_improvement.jsonl",
        base / "lattice" / "layer5_latest_answer.txt",
        base / "lattice" / "topology.json",
        base / "shape_packet.json",
    ]

    for path in candidates:
        if path.exists():
            try:
                if path.suffix == ".jsonl":
                    lines = path.read_text().strip().splitlines()
                    return json.loads(lines[-1])
                elif path.suffix == ".json":
                    return json.loads(path.read_text())
                else:
                    return {"raw": path.read_text()}
            except:
                continue

    return {"fallback": True}

def extract_variables(state):
    # safe extraction (works even if fields missing)
    return {
        "tension": state.get("tension", 0.2),
        "coherence": state.get("coherence", 0.6),
        "novelty": state.get("novelty", 0.5),
        "memory_depth": state.get("memory_depth", 10),
        "symbols": state.get("symbols", []),
    }
