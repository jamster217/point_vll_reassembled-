#!/usr/bin/env python3
"""
Le'Veon Crystal Index SVG Renderer
Creates a local dashboard image from logs/crystal_family_index.json.
"""

from __future__ import annotations

import json
import datetime
from pathlib import Path
from html import escape


INDEX_PATH = Path("logs/crystal_family_index.json")
OUT_DIR = Path("logs/crystal_index_renders")


def load_index() -> dict:
    if not INDEX_PATH.exists():
        raise FileNotFoundError("Missing logs/crystal_family_index.json. Run: python runtime/crystal_index.py")
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def role_color(role: str) -> str:
    return {
        "stable_diagnostic": "#55d6ff",
        "transformative_opener": "#7dff9b",
        "seed_pattern": "#ffcc66",
        "emerging_pattern": "#c48cff",
        "containment_tightener": "#ff7b7b",
        "friction_reducer": "#ffaa55",
        "structure_builder": "#a6b6ff",
    }.get(role, "#8aa0aa")


def bar(x: float, width: int = 220) -> int:
    try:
        return max(0, min(width, int(float(x) * width)))
    except Exception:
        return 0


def render_svg(data: dict) -> str:
    families = data.get("families", [])
    w, h = 1600, 900

    parts = []
    a = parts.append

    a(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <filter id="glow">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>

<rect width="{w}" height="{h}" fill="#050b0f"/>
<rect x="24" y="24" width="{w-48}" height="{h-48}" rx="18" fill="#0a151b" stroke="#24404d" stroke-width="2"/>
<rect x="50" y="50" width="{w-100}" height="{h-100}" rx="10" fill="none" stroke="#1f3540"/>

<text x="70" y="92" fill="#d8f4ff" font-size="36" font-family="monospace">CRYSTAL LIBRARY CONTROL PANEL</text>
<text x="70" y="130" fill="#8fb8c8" font-size="21" font-family="monospace">Family Index / Pattern Roles / Stability / Delta</text>

<rect x="1070" y="64" width="430" height="105" rx="8" fill="#101b23" stroke="#5b7b8b"/>
<text x="1090" y="100" fill="#d8f4ff" font-size="22" font-family="monospace">GENERATED: {escape(str(data.get("generated_at", "?")))}</text>
<text x="1090" y="136" fill="#d8f4ff" font-size="22" font-family="monospace">FAMILY COUNT: {data.get("family_count", len(families))}</text>
''')

    # central library core
    cx, cy = 800, 430
    a(f'<circle cx="{cx}" cy="{cy}" r="135" fill="#061016" stroke="#8feaff" stroke-width="4" filter="url(#glow)"/>')
    for r in (170, 205, 240):
        a(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#315a68" stroke-width="2" opacity="0.75"/>')
    a(f'<text x="{cx-165}" y="{cy-10}" fill="#e5fbff" font-size="23" font-family="monospace">CRYSTAL FAMILY INDEX</text>')
    a(f'<text x="{cx-118}" y="{cy+26}" fill="#9fc2cf" font-size="17" font-family="monospace">roles mapped from logs</text>')

    # family cards
    card_w = 455
    card_h = 170
    positions = [
        (80, 225),
        (1065, 225),
        (80, 475),
        (1065, 475),
        (570, 650),
    ]

    for i, fam in enumerate(families[:5]):
        x, y = positions[i] if i < len(positions) else (80, 225 + i * 190)
        name = str(fam.get("family", "unknown"))
        role = str(fam.get("role", "unknown"))
        color = role_color(role)
        turns = fam.get("turns", 0)
        stability = float(fam.get("stability", 0.0) or 0.0)
        delta = fam.get("avg_delta", {})
        release = float(delta.get("release", 0.0) or 0.0)
        summary = str(fam.get("summary", ""))[:70]
        sig = str(fam.get("top_signature", ""))[:62]

        a(f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="12" fill="#101b23" stroke="{color}" stroke-width="2"/>')
        a(f'<rect x="{x+16}" y="{y+20}" width="14" height="54" fill="{color}" filter="url(#glow)"/>')
        a(f'<text x="{x+46}" y="{y+42}" fill="#eaffff" font-size="24" font-family="monospace">{escape(name)}</text>')
        a(f'<text x="{x+46}" y="{y+72}" fill="{color}" font-size="18" font-family="monospace">role: {escape(role)}</text>')
        a(f'<text x="{x+46}" y="{y+100}" fill="#bdd6df" font-size="16" font-family="monospace">turns={turns} stability={stability:.3f} release_delta={release:+.3f}</text>')
        a(f'<rect x="{x+46}" y="{y+114}" width="220" height="12" fill="#22343c"/>')
        a(f'<rect x="{x+46}" y="{y+114}" width="{bar(stability)}" height="12" fill="{color}"/>')
        a(f'<text x="{x+46}" y="{y+146}" fill="#8fb8c8" font-size="13" font-family="monospace">{escape(sig)}</text>')
        a(f'<text x="{x+46}" y="{y+164}" fill="#8fb8c8" font-size="12" font-family="monospace">{escape(summary)}</text>')

        # connector line to core
        start_x = x + card_w if x < cx else x
        start_y = y + card_h / 2
        a(f'<path d="M{start_x},{start_y} C{(start_x+cx)/2},{start_y} {(start_x+cx)/2},{cy} {cx},{cy}" fill="none" stroke="{color}" stroke-width="2" opacity="0.45"/>')

    # bottom meaning row
    a(f'<rect x="260" y="785" width="1080" height="55" rx="8" fill="#101b23" stroke="#315a68"/>')
    a(f'<text x="285" y="820" fill="#d8f4ff" font-size="20" font-family="monospace">RUNTIME MEANING: known families become instruments; repeated shapes become navigable controls.</text>')

    a('</svg>')
    return "\\n".join(parts)


def write_svg() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = load_index()
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUT_DIR / f"{stamp}_crystal_family_index.svg"
    path.write_text(render_svg(data), encoding="utf-8")
    return path


def main():
    path = write_svg()
    print("CRYSTAL INDEX SVG WRITTEN")
    print("-------------------------")
    print(path)


if __name__ == "__main__":
    main()

