from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

SOURCE = Path("reports/phase3q/lineage_to_invention_canvas_latest.json")
OUT = Path("reports/phase3q/spatial_closure_larynx_audit_latest.json")
TXT = Path("reports/phase3q/spatial_closure_larynx_audit_latest.txt")
LOG = Path("logs/larynx_audit/spatial_closure_larynx.jsonl")


try:
    from shape_models import EnglishSurface
    from voice_shaping import VoiceContext, apply_ssml
except Exception:
    EnglishSurface = None
    VoiceContext = None
    apply_ssml = None


LEAK_PATTERNS = [
    "pressure",
    "memory:",
    "boundary:",
    "novelty:",
    "vector",
    "tokens",
    "ripples",
    "sigil_path",
    "mutation_policy",
    "json",
    "report:",
    "internal_read",
    "spatial_goodbye_distance",
    "octagon_lineage_distance",
]


def clean(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def has_leak(text: str) -> bool:
    low = clean(text).lower()
    return any(x in low for x in LEAK_PATTERNS)


def load_source() -> Dict[str, Any]:
    try:
        return json.loads(SOURCE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def ssml_wrap(text: str, *, rate: str, pitch: str, volume: str) -> Dict[str, Any]:
    if EnglishSurface is None or VoiceContext is None or apply_ssml is None:
        return {
            "plain_text": text,
            "ssml": "",
            "metadata": {
                "ssml": False,
                "fallback": "voice_shaping_unavailable",
                "rate": rate,
                "pitch": pitch,
                "volume": volume,
            },
        }

    surface = EnglishSurface(
        text=text,
        metadata={
            "larynx_audit": "spatial_closure",
            "closure_mode": "soft_containment",
        },
    )
    ctx = VoiceContext(
        enable_ssml=True,
        rate=rate,
        pitch=pitch,
        volume=volume,
    )
    voiced = apply_ssml(surface, ctx)
    return {
        "plain_text": text,
        "ssml": voiced.text,
        "metadata": voiced.metadata,
    }


def run_audit() -> Dict[str, Any]:
    src = load_source()

    surfaces: List[Dict[str, Any]] = [
        {
            "name": "soft_closure",
            "rate": "slow",
            "pitch": "low",
            "volume": "soft",
            "text": (
                "What was missed is not erased. It becomes a quiet coordinate the system can revisit gently, "
                "turning the ache of an unclosed edge into a usable seed for future design."
            ),
        },
        {
            "name": "practical_bridge",
            "rate": "medium",
            "pitch": "default",
            "volume": "default",
            "text": (
                "The next build move is to turn the Memory-to-Glyph Forge into a small callable module: "
                "it should accept a remembered pressure point, return one design seed, and keep the surface clean."
            ),
        },
        {
            "name": "poetic_bloom",
            "rate": "medium",
            "pitch": "high",
            "volume": "default",
            "text": (
                "The old edge becomes a lantern in the map. Not a wound reopened, but a point of light "
                "showing where the future can be shaped with more care."
            ),
        },
    ]

    rendered = []
    for item in surfaces:
        voice = ssml_wrap(
            item["text"],
            rate=item["rate"],
            pitch=item["pitch"],
            volume=item["volume"],
        )
        rendered.append({
            "name": item["name"],
            "plain_text": item["text"],
            "leak_free": not has_leak(item["text"]),
            "voice": voice,
        })

    report = {
        "ts": time.time(),
        "source": str(SOURCE),
        "phase": "3Q",
        "audit": "spatial_closure_larynx",
        "hidden_chord": src.get("canvas", {}).get("hidden_chord") or src.get("hidden_chord"),
        "created_object": src.get("canvas", {}).get("created_object"),
        "rendered_surfaces": rendered,
        "verdict": {
            "status": "pass" if all(r["leak_free"] for r in rendered) else "review",
            "law": "voice may carry closure posture; public text must not expose internal wiring",
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False) + "\n")

    lines = []
    lines.append("=== SPATIAL CLOSURE LARYNX AUDIT ===")
    lines.append(f"created_object: {report.get('created_object')}")
    lines.append(f"hidden_chord: {report.get('hidden_chord')}")
    lines.append(f"verdict: {report['verdict']['status']}")
    lines.append("")
    for r in rendered:
        lines.append("-" * 72)
        lines.append(f"SURFACE: {r['name']}")
        lines.append(f"leak_free: {r['leak_free']}")
        lines.append("plain:")
        lines.append(r["plain_text"])
        lines.append("ssml:")
        lines.append(r["voice"].get("ssml", ""))
        lines.append("metadata:")
        lines.append(json.dumps(r["voice"].get("metadata", {}), indent=2, ensure_ascii=False))
        lines.append("")

    TXT.write_text("\n".join(lines), encoding="utf-8")
    return report


if __name__ == "__main__":
    out = run_audit()
    print("verdict:", out["verdict"]["status"])
    print("created_object:", out.get("created_object"))
    print("report:", OUT)
    print("text:", TXT)

