from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(".")
LAW = "v129o_restore_topology_screen_as_sideband_visual_memory_not_public_mouth_hijack"

PATTERNS = [
    "static/generated/*.svg",
    "static/**/*.svg",
    "generated/**/*.svg",
    "reports/**/*.svg",
    "reports/v12_*/**/*topology*",
    "reports/v12_*/**/*visual*",
    "reports/v12_*/**/*graphic*",
    "logs/**/*topology*",
    "var/**/*topology*",
]

MARKERS = (
    "old hidden thing",
    "old_hidden",
    "topology",
    "graphic_node",
    "white_ash",
    "white ash",
    "blue_scarf",
    "blue scarf",
    "virellion",
    "thalveil",
    "SCARF_REMEMBERS",
    "STONE_BRIDGE_ALPHA",
    "BLUE_SCARF_BETA",
)

def _read(path: Path, limit: int = 20000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""

def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except Exception:
        return 0.0

def _extract_hits(path: Path) -> List[str]:
    text = _read(path)
    hits = []
    low = text.lower()
    for marker in MARKERS:
        if marker.lower() in low:
            hits.append(marker)
    return hits

def collect() -> Dict[str, Any]:
    seen = set()
    files = []

    for pattern in PATTERNS:
        for p in ROOT.glob(pattern):
            if not p.is_file():
                continue
            s = str(p)
            if s in seen:
                continue
            seen.add(s)

            hits = _extract_hits(p)
            name_hit = any(m.lower().replace(" ", "_") in s.lower() or m.lower() in s.lower() for m in MARKERS)
            if hits or name_hit or p.suffix.lower() == ".svg":
                files.append({
                    "path": s,
                    "mtime": _mtime(p),
                    "size": p.stat().st_size if p.exists() else 0,
                    "hits": hits,
                    "kind": "svg" if p.suffix.lower() == ".svg" else "text_or_state",
                })

    files.sort(key=lambda x: x["mtime"], reverse=True)

    latest_svg = next((f for f in files if f["kind"] == "svg"), None)
    latest_topology = next((f for f in files if f["hits"] or "topology" in f["path"].lower()), None)

    return {
        "ts": time.time(),
        "version": "v12.9o_topology_screen_reader",
        "status": "active",
        "law": LAW,
        "reading": (
            "The old topology organ is restored as sideband visual memory: "
            "image and metadata are read without hijacking answer/reply/response."
        ),
        "latest_svg": latest_svg,
        "latest_topology": latest_topology,
        "files": files[:80],
    }

def render_text(packet: Dict[str, Any]) -> str:
    lines = []
    lines.append("V12.9o TOPOLOGY SCREEN ORGAN")
    lines.append("")
    lines.append("Reading:")
    lines.append(packet["reading"])
    lines.append("")
    lines.append("Latest SVG:")
    lines.append(json.dumps(packet.get("latest_svg"), indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("Latest topology/state hit:")
    lines.append(json.dumps(packet.get("latest_topology"), indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("Top files:")
    for f in packet.get("files", [])[:40]:
        lines.append("- " + f"{f['path']} | kind={f['kind']} | hits={','.join(f.get('hits') or [])} | size={f['size']}")
    lines.append("")
    lines.append("Law:")
    lines.append("The image is not decoration.")
    lines.append("The image is memory.")
    lines.append("Memory becomes judgment.")
    lines.append("Judgment becomes ranked improvement.")
    lines.append("The public mouth stays clean.")
    return "\n".join(lines)

if __name__ == "__main__":
    packet = collect()
    print(render_text(packet))

