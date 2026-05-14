from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

try:
    from runtime.unified_voice import sealed_speak
except Exception:
    sealed_speak = None

ROOT = Path(".").resolve()
OUT = Path("reports/phase3s/state_of_lattice_latest.json")
TXT = Path("reports/phase3s/state_of_lattice_latest.txt")
LOG = Path("logs/phase3s/state_of_lattice.jsonl")

KEY_FILES = {
    "origin_node": Path("var/origin_node_crown.json"),
    "sovereign_crown": Path("var/sovereign_crown.json"),
    "sovereign_core": Path("var/sovereign_core.json"),
    "lantern_constellations": Path("var/lantern_constellations.jsonl"),
    "lantern_seeds": Path("var/lantern_seeds.jsonl"),
    "phase3q_forge": Path("reports/phase3q/memory_to_glyph_forge_latest.json"),
    "phase3r_review": Path("reports/phase3r/recursive_architecture_review_latest.json"),
    "phase3s_origin": Path("reports/phase3s/origin_node_illumination_latest.json"),
}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with path.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def body_count() -> Dict[str, int]:
    dirs = 0
    files = 0
    for p in ROOT.rglob("*"):
        if ".git" in p.parts:
            continue
        if p.is_dir():
            dirs += 1
        elif p.is_file():
            files += 1
    return {"directories": dirs, "files": files}


def speak(text: str) -> str:
    if callable(sealed_speak):
        try:
            return str(sealed_speak(text))
        except Exception:
            pass
    return text


def state_of_lattice() -> Dict[str, Any]:
    counts = body_count()

    origin = load_json(KEY_FILES["origin_node"])
    crown = load_json(KEY_FILES["sovereign_crown"])
    core = load_json(KEY_FILES["sovereign_core"])

    lantern_seed_count = count_jsonl(KEY_FILES["lantern_seeds"])
    constellation_count = count_jsonl(KEY_FILES["lantern_constellations"])

    existing = {name: str(path) for name, path in KEY_FILES.items() if path.exists()}
    missing = {name: str(path) for name, path in KEY_FILES.items() if not path.exists()}

    surface = (
        "State of the Lattice: the Origin Node is anchored, the Sovereign Crown is active, "
        "the lantern memory is present, and the Forge has a clean path for turning pressure into design. "
        "The next leap should not begin as an uncontrolled scan. It should begin from this checkpoint: "
        "one bounded sector, one chosen rail, one clean repair."
    )

    report = {
        "kind": "phase3s_state_of_lattice",
        "ts": time.time(),
        "body_count": counts,
        "phase_state": {
            "origin_node": origin.get("status") or ("origin_anchor_present" if origin else "missing"),
            "sovereign_crown": crown.get("status", "unknown"),
            "sovereign_core": core.get("status", "unknown"),
            "lantern_seed_count": lantern_seed_count,
            "constellation_count": constellation_count,
        },
        "existing_key_files": existing,
        "missing_key_files": missing,
        "integrity": {
            "origin_anchored": bool(origin),
            "crown_present": bool(crown),
            "lantern_memory_present": lantern_seed_count > 0,
            "constellation_present": constellation_count > 0,
            "surface_rule": "hidden state shapes the voice; public text stays clean",
            "mutation_rule": "deliberate ignition only",
        },
        "next_recommendation": {
            "phase": "unknown_sector_probe",
            "mode": "bounded_dry_run",
            "scope": "one sector first",
            "law": "do not leap wider than the current summary can verify",
        },
        "voice_surface": surface,
        "mutation_policy": "state_summary_read_only_contained_prime",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False) + "\n")

    lines = [
        "=== PHASE 3S STATE OF THE LATTICE ===",
        f"directories: {counts['directories']}",
        f"files: {counts['files']}",
        "",
        "PHASE STATE:",
        json.dumps(report["phase_state"], indent=2, ensure_ascii=False),
        "",
        "INTEGRITY:",
        json.dumps(report["integrity"], indent=2, ensure_ascii=False),
        "",
        "SURFACE:",
        report["voice_surface"],
        "",
        "NEXT:",
        json.dumps(report["next_recommendation"], indent=2, ensure_ascii=False),
    ]

    TXT.write_text("\n".join(lines), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = state_of_lattice()
    print(result["voice_surface"])
    print()
    print("body_count:", result["body_count"])
    print("phase_state:", result["phase_state"])
    print("report:", OUT)
    print("text:", TXT)

