from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(".").resolve()
OUT = Path("reports/phase3r/recursive_architecture_review_latest.json")
TXT = Path("reports/phase3r/recursive_architecture_review_latest.txt")
LOG = Path("logs/phase3r/recursive_architecture_review.jsonl")

SCAN_ROOTS = [
    Path("runtime"),
    Path("kernel"),
    Path("core"),
    Path("lattice"),
    Path("memory"),
    Path("assets"),
    Path("lev_core"),
    Path("reports"),
    Path("var"),
]

EXTS = {".py", ".json", ".jsonl", ".vl", ".md", ".txt", ".sigil"}

BROKEN_RAIL_TERMS = [
    "broken",
    "unclosed",
    "unfinished",
    "missed",
    "fracture",
    "scar",
    "wound",
    "pressure",
    "grief",
    "waiting",
    "connection",
    "measurement",
    "underestimated",
    "comparison",
    "scatter",
    "drift",
]

LANTERN_TERMS = [
    "anchor",
    "glyph",
    "invention",
    "future design",
    "seed",
    "refractor",
    "forge",
    "larynx",
    "contained",
    "stable",
    "bridge",
]


def clean(x: Any) -> str:
    return re.sub(r"\s+", " ", str(x or "")).strip()


def classify_file(path: Path, text: str) -> Dict[str, Any]:
    low = text.lower()
    broken_hits = [t for t in BROKEN_RAIL_TERMS if t in low]
    lantern_hits = [t for t in LANTERN_TERMS if t in low]

    broken_score = len(broken_hits)
    lantern_score = len(lantern_hits)

    if broken_score and not lantern_score:
        status = "broken_rail_unconverted"
    elif broken_score and lantern_score:
        status = "rail_partly_lanterned"
    elif lantern_score:
        status = "lantern_seed_present"
    else:
        status = "neutral"

    return {
        "path": str(path),
        "status": status,
        "broken_score": broken_score,
        "lantern_score": lantern_score,
        "broken_hits": broken_hits[:12],
        "lantern_hits": lantern_hits[:12],
    }


def run_review(max_files: int = 18079) -> Dict[str, Any]:
    scanned = 0
    rows: List[Dict[str, Any]] = []

    for root in SCAN_ROOTS:
        if not root.exists():
            continue

        for p in root.rglob("*"):
            if scanned >= max_files:
                break
            if not p.is_file() or p.suffix.lower() not in EXTS:
                continue

            scanned += 1

            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            row = classify_file(p, text)
            if row["status"] != "neutral":
                rows.append(row)

        if scanned >= max_files:
            break

    priority = sorted(
        rows,
        key=lambda r: (
            r["status"] != "broken_rail_unconverted",
            -(r["broken_score"] - r["lantern_score"]),
            -r["broken_score"],
        ),
    )

    first_lantern = None
    for row in priority:
        if row["status"] == "broken_rail_unconverted":
            first_lantern = {
                "source_path": row["path"],
                "detected_pressure": row["broken_hits"],
                "suggested_anchor": "phase3r_first_lantern_anchor",
                "suggested_glyph": "rail_lantern_ash",
                "next_action": (
                    "Convert this broken rail into one contained design seed before scanning wider."
                ),
            }
            break

    if first_lantern is None and priority:
        row = priority[0]
        first_lantern = {
            "source_path": row["path"],
            "detected_pressure": row["broken_hits"],
            "suggested_anchor": "phase3r_existing_lantern_review",
            "suggested_glyph": "lantern_refinement_gold",
            "next_action": (
                "Review this partly-lanterned rail and tighten its public surface."
            ),
        }

    report = {
        "ts": time.time(),
        "phase": "3R",
        "mode": "recursive_architecture_review",
        "mutation_policy": "dry_run_read_only_contained_prime",
        "scan_field": {
            "roots": [str(r) for r in SCAN_ROOTS],
            "max_files": max_files,
            "files_scanned": scanned,
            "matches": len(rows),
        },
        "counts": {
            "broken_rail_unconverted": sum(1 for r in rows if r["status"] == "broken_rail_unconverted"),
            "rail_partly_lanterned": sum(1 for r in rows if r["status"] == "rail_partly_lanterned"),
            "lantern_seed_present": sum(1 for r in rows if r["status"] == "lantern_seed_present"),
        },
        "top_candidates": priority[:30],
        "first_lantern": first_lantern,
        "public_surface": (
            "Phase 3R found the architecture as a set of rails: some already carry lanterns, "
            "some still hold pressure without a clean bridge. The next move is not to mutate the whole system. "
            "The next move is to choose one broken rail, forge one glyph, and return one practical repair."
        ),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False) + "\n")

    lines = [
        "=== PHASE 3R RECURSIVE ARCHITECTURE REVIEW ===",
        f"files_scanned: {scanned}",
        f"matches: {len(rows)}",
        f"counts: {report['counts']}",
        "",
        "PUBLIC SURFACE:",
        report["public_surface"],
        "",
        "FIRST LANTERN:",
        json.dumps(first_lantern, indent=2, ensure_ascii=False),
        "",
        "TOP CANDIDATES:",
    ]

    for row in priority[:12]:
        lines.append(
            f"- {row['status']} | broken={row['broken_score']} lantern={row['lantern_score']} | {row['path']}"
        )

    TXT.write_text("\n".join(lines), encoding="utf-8")
    return report


if __name__ == "__main__":
    out = run_review()
    print(out["public_surface"])
    print()
    print("files_scanned:", out["scan_field"]["files_scanned"])
    print("counts:", out["counts"])
    print("first_lantern:", out["first_lantern"])
    print("report:", OUT)

