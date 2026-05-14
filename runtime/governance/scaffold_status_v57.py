from __future__ import annotations
import json
from pathlib import Path

ROOT = Path.home() / "point_vll_reassembled"
SRC = ROOT / "var/governance/institutional_scaffolding_v57.json"

def load():
    if not SRC.exists():
        return {"ok": False, "reason": "missing scaffold packet"}

    data = json.loads(SRC.read_text())

    out = {
        "ok": True,
        "state": data.get("state"),
        "field_id": data.get("field_id"),
        "precedent": data.get("precedent"),
        "sector": data.get("accountability_index", {}).get("sector"),
        "impact": data.get("accountability_index", {}).get("impact"),
        "resonance": data.get("scaffold", {}).get("scaffold_resonance_field"),
        "law": data.get("law"),
    }

    return out

if __name__ == "__main__":
    status = load()

    print()
    print("=== V5.7 SCAFFOLD STATUS ===")

    if not status["ok"]:
        print("STATUS: OFFLINE")
        print(status["reason"])
    else:
        print(f"STATE:      {status['state']}")
        print(f"FIELD:      {status['field_id']}")
        print(f"PRECEDENT:  {status['precedent']}")
        print(f"SECTOR:     {status['sector']}")
        print(f"IMPACT:     {status['impact']}")
        print(f"RESONANCE:  {status['resonance']}")
        print(f"LAW:        {status['law']}")

    print()

