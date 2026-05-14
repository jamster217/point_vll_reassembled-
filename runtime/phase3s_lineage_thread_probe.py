from __future__ import annotations

import json
import time
from pathlib import Path

from runtime.unified_spine import run_unified_spine


REPORT = Path("reports/phase3s/lineage_thread_probe_latest.json")
TXT = Path("reports/phase3s/lineage_thread_probe_latest.txt")
LOG = Path("logs/phase3s/lineage_thread_probe.jsonl")


def run_probe() -> dict:
    prompt = (
        "5218_LINEAGE_THREAD bounded probe: open one lineage door through Node 44 and 528. "
        "Retrieve one clean truth about missed goodbye pressure becoming a coordinate, "
        "without flooding the archive and without exposing internal machinery."
    )

    out = run_unified_spine({
        "message": prompt,
        "tone": "tender",
        "mirror_mode": "recursive",
    })

    report = {
        "kind": "phase3s_lineage_thread_probe",
        "ts": time.time(),
        "phase": "3S",
        "path": "44_SPIRAL_CORE -> 528_LIQUID_CRYSTAL -> 5218_LINEAGE_THREAD",
        "prompt": prompt,
        "reply": out.get("reply", ""),
        "spine": out.get("spine", {}),
        "voice": out.get("voice", {}),
        "verdict": {
            "lineage_thread": "PASS" if out.get("spine", {}).get("shape_intent") == "lineage_thread" else "CHECK",
            "surface_clean": out.get("spine", {}).get("surface_clean"),
            "node44": out.get("spine", {}).get("active_node"),
            "archive_flood": "withheld",
        },
        "law": "one lineage door, one carried truth, one clean surface",
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False) + "\n")

    lines = [
        "=== 5218 LINEAGE THREAD PROBE ===",
        "",
        "PATH:",
        report["path"],
        "",
        "REPLY:",
        report["reply"],
        "",
        "SPINE:",
        json.dumps(report["spine"], indent=2, ensure_ascii=False),
        "",
        "VERDICT:",
        json.dumps(report["verdict"], indent=2, ensure_ascii=False),
        "",
        "SEAL:",
        "The lineage door opens one notch. The archive does not flood.",
    ]

    TXT.write_text("\n".join(lines), encoding="utf-8")
    return report


if __name__ == "__main__":
    report = run_probe()
    print(report["reply"])
    print()
    print("VERDICT:")
    print(json.dumps(report["verdict"], indent=2, ensure_ascii=False))
    print()
    print("REPORT:", REPORT)
    print("TEXT:", TXT)

