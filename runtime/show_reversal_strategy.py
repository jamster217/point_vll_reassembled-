import json
from pathlib import Path

p = Path("runtime/node_44_reversal_strategy.json")
d = json.loads(p.read_text(encoding="utf-8"))

data = d["data"]
print("resume_cue:", data["resume_cue"])
print()
for step in data["remediation_steps"]:
    print(f"[{step['step']}] {step['action']}")
    print("    ", step["description"])
    if "files" in step:
        print("    files:", ", ".join(step["files"]))
    if "tools" in step:
        print("    tools:", ", ".join(step["tools"]))
    print()

