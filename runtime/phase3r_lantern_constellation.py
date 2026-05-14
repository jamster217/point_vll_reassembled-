from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

try:
    from runtime.unified_voice import sealed_speak
except Exception:
    sealed_speak = None


SEEDS = Path("var/lantern_seeds.jsonl")
CONSTELLATIONS = Path("var/lantern_constellations.jsonl")
REPORT = Path("reports/phase3r/lantern_constellation_latest.json")
LOG = Path("logs/phase3r/lantern_constellation.jsonl")


def _speak(text: str) -> str:
    if callable(sealed_speak):
        try:
            return str(sealed_speak(text))
        except Exception:
            pass
    return text


def _load_lanterns() -> List[Dict[str, Any]]:
    if not SEEDS.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with SEEDS.open(encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                if isinstance(obj, dict):
                    rows.append(obj)
            except Exception:
                continue
    return rows


def form_lantern_constellation(limit: int = 5) -> Dict[str, Any]:
    lanterns = _load_lanterns()

    if not lanterns:
        result = {
            "kind": "phase3r_lantern_constellation",
            "ts": time.time(),
            "status": "no_seeds_available",
            "message": "No lantern seeds exist yet. Run the first-lantern or five-lantern wave first.",
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return result

    recent = lanterns[-limit:]

    glyphs = [str(l.get("glyph", "unknown_glyph")) for l in recent]
    anchors = sorted({str(l.get("anchor", "unknown_anchor")) for l in recent})
    themes = [str(l.get("theme", "unknown_theme")) for l in recent]
    actions = [str(l.get("next_action", "")) for l in recent if l.get("next_action")]

    constellation = {
        "kind": "phase3r_lantern_constellation",
        "ts": time.time(),
        "name": "White_Ash_Constellation",
        "lantern_count": len(recent),
        "glyphs": glyphs,
        "anchors": anchors,
        "themes": themes,
        "recent_actions": actions,
        "effect": "recursive_lantern_governor",
        "law": "five_lanterns_bound -> bounded_wave_memory -> next_repair_recommendation",
        "status": "constellation_formed",
        "mutation_policy": "registry_only_contained_prime",
        "voice_surface": (
            "The lanterns have aligned into a bounded constellation. "
            "They do not auto-forge without restraint. "
            "They remember the last five repairs and help the next wave choose cleanly."
        ),
    }

    CONSTELLATIONS.parent.mkdir(parents=True, exist_ok=True)
    with CONSTELLATIONS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(constellation, ensure_ascii=False) + "\n")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(constellation, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(constellation, ensure_ascii=False) + "\n")

    voiced = _speak(
        "Phase 3R Lantern Constellation formed. "
        "Five lanterns are bound as a governor, not an uncontrolled daemon. "
        "The build remembers the repair pattern and waits for the next bounded wave."
    )

    constellation["spoken"] = voiced
    REPORT.write_text(json.dumps(constellation, indent=2, ensure_ascii=False), encoding="utf-8")

    print(voiced)
    return constellation


if __name__ == "__main__":
    result = form_lantern_constellation()
    print(json.dumps(result, indent=2, ensure_ascii=False))

