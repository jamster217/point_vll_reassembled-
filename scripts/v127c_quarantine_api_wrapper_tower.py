from __future__ import annotations

import json
import re
import time
from pathlib import Path

TARGET = Path("app_chatroom.py")
REPORT_DIR = Path("reports/v12_7/repair")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

MARKERS = [
    "CHAMBER_528_SERVER_PATCH_V1",
    "POINT_VLL_GATE_CHAMBER_SERVER_PATCH_V1",
    "FINAL SURFACE V5.3",
    "FINAL TELEMETRY V5.4",
    "V5.6 TELEMETRY",
    "V6.1 PRE ERROR",
]

text = TARGET.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines(True)

def_blocks = []
for i, line in enumerate(lines):
    m = re.match(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", line)
    if m:
        def_blocks.append((m.group(1), i))

functions = []
for idx, (name, start) in enumerate(def_blocks):
    end = def_blocks[idx + 1][1] if idx + 1 < len(def_blocks) else len(lines)
    body = "".join(lines[start:end])
    hits = [m for m in MARKERS if m in body]
    wraps_api_chat = 'app.view_functions["api_chat"]' in body or "app.view_functions['api_chat']" in body
    if hits and wraps_api_chat:
        functions.append({
            "name": name,
            "start_line": start + 1,
            "end_line": end,
            "markers": hits,
            "wraps_api_chat": wraps_api_chat,
        })

wrapper_names = {f["name"] for f in functions}

call_hits = []
new_lines = []
changed = False

for i, line in enumerate(lines):
    stripped = line.strip()
    call_match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\(\)\s*(#.*)?$", stripped)
    if call_match and call_match.group(1) in wrapper_names:
        name = call_match.group(1)
        call_hits.append({"line": i + 1, "name": name, "old": line.rstrip("\n")})
        indent = line[: len(line) - len(line.lstrip())]
        new_lines.append(
            f"{indent}# V12.7c quarantine: disabled legacy api_chat wrapper tower call: {name}()\n"
        )
        changed = True
    else:
        new_lines.append(line)

stamp = time.strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(f"app_chatroom.before_v127c_wrapper_quarantine_{stamp}.py")

report = {
    "created_at": time.time(),
    "version": "v12.7c_wrapper_tower_quarantine",
    "target": str(TARGET),
    "backup": str(backup),
    "functions_found": functions,
    "calls_quarantined": call_hits,
    "changed": changed,
    "law": "single_mouth_before_more_symbolic_layers",
}

report_path = REPORT_DIR / "v127c_wrapper_tower_quarantine_report.json"
txt_path = REPORT_DIR / "v127c_wrapper_tower_quarantine_report.txt"

if changed:
    backup.write_text(text, encoding="utf-8")
    TARGET.write_text("".join(new_lines), encoding="utf-8")

report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

with txt_path.open("w", encoding="utf-8") as f:
    f.write("=== V12.7c WRAPPER TOWER QUARANTINE ===\n")
    f.write(f"changed: {changed}\n")
    f.write(f"backup: {backup}\n\n")
    f.write("WRAPPER FUNCTIONS FOUND:\n")
    for item in functions:
        f.write(
            f"- {item['name']} L{item['start_line']}-L{item['end_line']} "
            f"markers={','.join(item['markers'])}\n"
        )
    f.write("\nCALLS QUARANTINED:\n")
    for item in call_hits:
        f.write(f"- L{item['line']}: {item['name']}()\n")

print("changed:", changed)
print("backup:", backup if changed else "none")
print("functions_found:", len(functions))
print("calls_quarantined:", len(call_hits))
print("report:", txt_path)
