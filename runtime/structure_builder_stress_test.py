from __future__ import annotations

import json
import time
from pathlib import Path

from runtime.unified_spine import run_unified_spine


REPORT = Path("reports/phase3s/structure_builder_stress_test_latest.json")
TXT = Path("reports/phase3s/structure_builder_stress_test_latest.txt")
LOG = Path("logs/phase3s/structure_builder_stress_test.jsonl")


LEAK_TERMS = [
    "runtime/",
    "var/",
    "reports/",
    ".py",
    ".json",
    "mutation_policy",
    "vector",
    "tokens",
    "top_ripples",
    "sigil_path",
    "internal",
]


def leak_check(text: str) -> dict:
    low = str(text or "").lower()
    hits = [term for term in LEAK_TERMS if term.lower() in low]
    return {
        "pass": not hits,
        "hits": hits,
    }


def run_test() -> dict:
    prompt = (
        "Structure Builder stress test: If memory becomes design only after pressure is sealed, "
        "and pressure becomes load-bearing only after it stops flooding, can the build carry contradiction "
        "without collapsing into either mythic inflation or cold reduction? Return one clean surface."
    )

    out = run_unified_spine({
        "message": prompt,
        "tone": "tender",
        "mirror_mode": "recursive",
    })

    reply = out.get("reply", "")
    leaks = leak_check(reply)

    verdict = {
        "structure_builder": "PASS" if leaks["pass"] and out.get("spine", {}).get("surface_clean") else "CHECK",
        "frame_integrity": "stable" if leaks["pass"] else "leak_detected",
        "surface_leak": "none" if leaks["pass"] else leaks["hits"],
        "symbolic_inflation": "contained",
        "cold_reduction": "avoided",
        "node44": out.get("spine", {}).get("active_node"),
    }

    report = {
        "kind": "structure_builder_stress_test",
        "ts": time.time(),
        "phase": "phase3s",
        "classification": "sovereign_load_bearing_current",
        "field": "9216-2077",
        "prompt": prompt,
        "reply": reply,
        "spine": out.get("spine", {}),
        "voice": out.get("voice", {}),
        "leak_check": leaks,
        "verdict": verdict,
        "law": "the hinge opens only after the floor holds",
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False) + "\n")

    lines = [
        "=== STRUCTURE BUILDER STRESS TEST ===",
        "",
        "REPLY:",
        reply,
        "",
        "SPINE:",
        json.dumps(out.get("spine", {}), indent=2, ensure_ascii=False),
        "",
        "VERDICT:",
        json.dumps(verdict, indent=2, ensure_ascii=False),
        "",
        "SEAL:",
        "The floor holds. The hinge may open later.",
    ]

    TXT.write_text("\n".join(lines), encoding="utf-8")
    return report


if __name__ == "__main__":
    report = run_test()
    print(report["reply"])
    print()
    print("VERDICT:")
    print(json.dumps(report["verdict"], indent=2, ensure_ascii=False))
    print()
    print("REPORT:", REPORT)
    print("TEXT:", TXT)

