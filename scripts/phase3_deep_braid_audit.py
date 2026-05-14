#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(".")
OUT = Path("reports/phase3_deep_braid_audit.json")
OUT_TXT = Path("reports/phase3_deep_braid_audit.txt")

SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "snapshots", "logs", "runtime/bak", "var"
}

TERMS = [
    "api_chat",
    "/api/chat",
    "master_reply",
    "classify_shape",
    "Hard Master Gate",
    "HARD_MASTER_GATE",
    "LIVE_MASTER_GATE",
    "Node44",
    "NODE44",
    "node_44",
    "Performance Oracle",
    "PERF ORACLE",
    "prompt_density",
    "controller_detail",
    "answer_mode",
    "jsonify",
    "render_template",
    "app.run",
]


def should_skip(path: Path) -> bool:
    rel = path.as_posix()
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return True
    for d in SKIP_DIRS:
        if rel.startswith(d + "/"):
            return True
    if path.suffix not in {".py", ".html", ".js", ".json", ".md"}:
        return True
    return False


results = []

for path in ROOT.rglob("*"):
    if not path.is_file() or should_skip(path):
        continue

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue

    hits = []
    for term in TERMS:
        if term in text:
            hits.append(term)

    if hits:
        results.append({
            "file": path.as_posix(),
            "hits": hits,
            "score": len(hits)
        })

results.sort(key=lambda x: (-x["score"], x["file"]))

OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

lines = []
lines.append("PHASE 3 DEEP BRAID AUDIT")
lines.append("=" * 72)
lines.append(f"files_with_hits: {len(results)}")
lines.append("")

for row in results[:80]:
    lines.append(f"{row['score']:02d}  {row['file']}")
    lines.append("    " + ", ".join(row["hits"]))

OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("\n".join(lines[:160]))
print()
print("saved:", OUT)
print("saved:", OUT_TXT)
