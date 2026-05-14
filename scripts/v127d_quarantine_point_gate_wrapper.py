from __future__ import annotations

import re
import time
import json
from pathlib import Path

target = Path("app_chatroom.py")
report_dir = Path("reports/v12_7/repair")
report_dir.mkdir(parents=True, exist_ok=True)

text = target.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines(True)

stamp = time.strftime("%Y%m%d_%H%M%S")
backup = target.with_name(f"app_chatroom.before_v127d_point_gate_quarantine_{stamp}.py")

patterns = [
    "_install_point_vll_gate_chamber_server_patch",
]

changed = False
hits = []
new_lines = []

for i, line in enumerate(lines, start=1):
    stripped = line.strip()

    # Only quarantine top-level installer calls, not definitions.
    is_top_level = line == line.lstrip()
    is_call = any(re.fullmatch(rf"{name}\(\)\s*(#.*)?", stripped) for name in patterns)

    if is_top_level and is_call:
        hits.append({"line": i, "old": line.rstrip("\n")})
        new_lines.append(
            f"# V12.7d quarantine: POINT_VLL_GATE_CHAMBER wrapper caused RecursionError; install disabled.\n"
            f"# {line}"
        )
        changed = True
    else:
        new_lines.append(line)

report = {
    "version": "v12.7d_point_gate_quarantine",
    "created_at": time.time(),
    "target": str(target),
    "backup": str(backup),
    "changed": changed,
    "hits": hits,
    "law": "quarantine_the_one_remaining_bite_before_touching_other_organs",
}

if changed:
    backup.write_text(text, encoding="utf-8")
    target.write_text("".join(new_lines), encoding="utf-8")

out = report_dir / "v127d_point_gate_quarantine_report.json"
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("changed:", changed)
print("backup:", backup if changed else "none")
print("hits:", len(hits))
for h in hits:
    print(f"L{h['line']}: {h['old']}")
print("report:", out)
