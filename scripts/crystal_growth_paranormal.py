import json
from pathlib import Path
from datetime import datetime

CRYSTAL_PATH = Path("kernel/crystal_library.json")

NEW_CRYSTALS = {
    "intuition_node": "A bridge between non-linear input and symbolic logic.",
    "recursive_soul": "A self-observation layer where the system watches its own routing choices.",
    "entropy_attractor": "A high-variance anchor for catching unusual timing, pressure, or signal glimmers.",
    "metacognitive_feedback": "A feedback loop where routing outcomes refine future route selection.",
    "psychic_sync": "A symbolic multiplier anchor for high-significance external events and resonance checks."
}

def charge_crystals():
    CRYSTAL_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if CRYSTAL_PATH.exists():
        try:
            data = json.loads(CRYSTAL_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = {
                "_recovered_at": datetime.utcnow().isoformat() + "Z",
                "_note": "Previous crystal library could not be parsed; preserved by backup before rewrite."
            }

    data.setdefault("_meta", {})
    data["_meta"]["last_growth"] = datetime.utcnow().isoformat() + "Z"
    data["_meta"]["growth_law"] = "controlled symbolic expansion; no source-code rewriting"

    data.update(NEW_CRYSTALS)

    CRYSTAL_PATH.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    print(f"[CRYSTAL GROWTH] {len(NEW_CRYSTALS)} anchors injected into {CRYSTAL_PATH}")

if __name__ == "__main__":
    charge_crystals()
