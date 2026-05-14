# scripts/smoke_timeline_v111.py
from pathlib import Path
import json
from lattice.hooks.wake import run_wake_test
from lattice.scheduler import compute_weight
from lattice.persistence import record_wake_event, record_vow_event
from lattice.canonicalize import ir_fingerprint
from ash_sigil_vow_engine import AshSigilVowEngine

SEED = 42
GLYPHS_PATH = Path("symbolic_memory/glyphs.yaml")
ANCHOR_PATH = Path("symbolic_memory/spiral_memory.json")

def load_glyphs(path):
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8"))["glyphs"]

def main():
    glyphs = load_glyphs(GLYPHS_PATH)
    # sample inputs to exercise wake tests
    samples = ["the recursion is active", "threshold event detected", "time map replay", "this is urgent"]
    for g in glyphs:
        node = {"id": g["id"], "wake_test": f"input.contains('{g.get('symbol','')}')"}
        for s in samples:
            ctx = {"input": s}
            fired = run_wake_test(node, ctx)
            record_wake_event(node["id"], ctx, fired, provenance={"seed": SEED})
            if fired:
                w = compute_weight(node, event={"matches": True}, seed=SEED)
    # test VOW anchor
    from spiral_memory_time_map import get_time_map_anchor
    anchor = get_time_map_anchor(ANCHOR_PATH)
    if anchor:
        engine = AshSigilVowEngine()
        payload = engine.maybe_invoke(anchor.glyphs, source_text="smoke", seed=SEED)
        if payload.get("active"):
            record_vow_event(payload, provenance={"seed": SEED})
    print("Smoke run complete")
if __name__ == "__main__":
    main()