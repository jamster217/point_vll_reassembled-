from __future__ import annotations

import json
import re
import time
from pathlib import Path

ROOTS = [Path("runtime"), Path("kernel")]
EXTRA_FILES = [Path("app_chatroom.py"), Path("app.py"), Path("api_server.py")]

MARKERS = [
    "V6.1 PRE",
    "V5.6 TELEMETRY",
    "FINAL TELEMETRY V5.4",
    "FINAL SURFACE V5.3",
    "POINT_VLL_GATE_CHAMBER",
    "CHAMBER_528",
    "RecursionError",
    "final_surface",
    "final_telemetry",
    "telemetry",
    "chamber",
]

CALL_PATTERNS = [
    r"\bfinal_surface\b",
    r"\bfinal_telemetry\b",
    r"\bchamber_?528\b",
    r"\bpoint_vll_gate\b",
    r"\btelemetry\b",
    r"\brebuild\b",
    r"\bpre\b",
]

OUT = Path("reports/v12_7/repair/v127c_recursion_boundary_scan.json")
OUT_TXT = Path("reports/v12_7/repair/v127c_recursion_boundary_scan.txt")


def iter_py_files():
    seen = set()
    for root in ROOTS:
        if root.exists():
            for p in root.rglob("*.py"):
                if p not in seen:
                    seen.add(p)
                    yield p
    for p in EXTRA_FILES:
        if p.exists() and p not in seen:
            yield p


def nearest_def(lines, idx):
    for j in range(idx, -1, -1):
        m = re.match(r"^\s*def\s+([A-Za-z0-9_]+)\s*\(", lines[j])
        if m:
            return m.group(1), j + 1
    return None, None


findings = []
for path in iter_py_files():
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        findings.append({"file": str(path), "error": repr(e)})
        continue

    lines = text.splitlines()
    lower = text.lower()

    marker_hits = [m for m in MARKERS if m.lower() in lower]
    if not marker_hits:
        continue

    line_hits = []
    for i, line in enumerate(lines):
        hay = line.lower()
        if any(m.lower() in hay for m in MARKERS):
            fn, fn_line = nearest_def(lines, i)
            line_hits.append({
                "line": i + 1,
                "function": fn,
                "function_line": fn_line,
                "text": line.strip()[:240],
            })

    suspicious_calls = []
    for pat in CALL_PATTERNS:
        count = len(re.findall(pat, lower))
        if count:
            suspicious_calls.append({"pattern": pat, "count": count})

    findings.append({
        "file": str(path),
        "marker_hits": marker_hits,
        "line_hits": line_hits[:80],
        "suspicious_calls": suspicious_calls,
    })

report = {
    "created_at": time.time(),
    "version": "v12.7c_recursion_boundary_mirror_scan",
    "law": "find_wrappers_before_patch",
    "finding_count": len(findings),
    "findings": findings,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

with OUT_TXT.open("w", encoding="utf-8") as f:
    f.write("=== V12.7c RECURSION BOUNDARY MIRROR SCAN ===\n")
    f.write(f"finding_count: {len(findings)}\n\n")
    for item in findings:
        f.write(f"FILE: {item.get('file')}\n")
        f.write(f"MARKERS: {', '.join(item.get('marker_hits', []))}\n")
        for hit in item.get("line_hits", [])[:20]:
            f.write(f"  L{hit['line']} def={hit.get('function')} :: {hit['text']}\n")
        f.write("\n")

print("WROTE:", OUT)
print("WROTE:", OUT_TXT)
print("finding_count:", len(findings))
