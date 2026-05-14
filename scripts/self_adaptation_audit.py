#!/usr/bin/env python3
from pathlib import Path
import json
import time

state = Path("var/exponential_sovereign_state.json")

print("SELF-ADAPTATION AUDIT")
print("=" * 60)

if state.exists():
    stat = state.stat()
    print("state_file:", state)
    print("modified_epoch:", stat.st_mtime)
    print("modified_age_seconds:", round(time.time() - stat.st_mtime, 2))
    try:
        data = json.loads(state.read_text())
        print("status:", data.get("status"))
        print("mode:", data.get("mode"))
        print("generation:", data.get("generation"))
        print("multiplier:", data.get("multiplier"))
        print("seed:", data.get("seed"))
    except Exception as e:
        print("state_parse_error:", e)
else:
    print("state_file: missing")

print()
print("source_files_modified_last_10_min:")
roots = [Path("runtime"), Path("core"), Path("kernel"), Path("config"), Path("templates")]
now = time.time()
hits = []

for root in roots:
    if not root.exists():
        continue
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in {".py", ".json", ".html"}:
            continue
        if now - p.stat().st_mtime <= 600:
            hits.append(str(p))

if hits:
    for h in sorted(hits):
        print("-", h)
else:
    print("none")

print()
print("VERDICT:")
if state.exists() and not hits:
    print("runtime self-adaptation present; source body stable")
elif state.exists() and hits:
    print("runtime state present; source files changed recently")
else:
    print("no adaptation state detected")
