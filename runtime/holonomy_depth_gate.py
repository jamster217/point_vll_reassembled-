#!/usr/bin/env python3
from pathlib import Path
import json, time

OUT = Path("var/holonomy/holonomy_depth_state.json")

RULES = {
    "locked":  {"max_depth": 0, "cross_pass_allowed": False},
    "shallow": {"max_depth": 1, "cross_pass_allowed": False},
    "medium":  {"max_depth": 3, "cross_pass_allowed": True},
    "deep":    {"max_depth": 7, "cross_pass_allowed": True},
}

def resolve(governor_directive=None):
    governor_directive = governor_directive or {}
    cap = str(governor_directive.get("holonomy_depth_cap", "shallow")).lower().strip()
    result = dict(RULES.get(cap, RULES["shallow"]))
    result["holonomy_depth_cap"] = cap
    result["source"] = "runtime.holonomy_depth_gate"
    result["updated_at"] = time.time()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

if __name__ == "__main__":
    import sys
    cap = sys.argv[1] if len(sys.argv) > 1 else "medium"
    print(json.dumps(resolve({"holonomy_depth_cap": cap}), indent=2))
