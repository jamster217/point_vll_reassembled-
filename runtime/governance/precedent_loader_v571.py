from pathlib import Path
import json

ROOT = Path.home() / "point_vll_reassembled"
FILES = [
    ROOT / "var/governance/institutional_scaffolding_v57.json",
    ROOT / "var/governance/precedent_case_002.json",
]

def load_precedents():
    items = []
    for p in FILES:
        if p.exists():
            items.append(json.loads(p.read_text()))
    return items

if __name__ == "__main__":
    items = load_precedents()
    print("=== V5.7.1 PRECEDENT LOAD ===")
    print("COUNT:", len(items))
    for x in items:
        print("-", x.get("precedent", "PRECEDENT_CASE_0.01"), "|", x.get("sector", x.get("accountability_index", {}).get("sector")), "|", x.get("impact", x.get("accountability_index", {}).get("impact")), "|", x.get("law"))

