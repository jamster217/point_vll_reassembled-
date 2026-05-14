#!/usr/bin/env python3
"""
Le'Veon Crystal Index Mobile SVG Renderer
Phone-readable Crystal Library dashboard.
"""

from __future__ import annotations

import json
import datetime
import textwrap
from pathlib import Path
from html import escape


INDEX_PATH = Path("logs/crystal_family_index.json")
OUT_DIR = Path("logs/crystal_index_mobile_renders")


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
    }.get(role, "#9fb3bd")


def wrap_lines(text: str, width: int = 42, max_lines: int = 3):
    lines = textwrap.wrap(str(text), width=width)
    return lines[:max_lines]


def render_svg(data: dict) -> str:
    families = data.get("families", [])
    w = 1080
    h = max(1850, 520 + len(families) * 325)

    stable = sum(1 for f in families if f.get("role") == "stable_diagnostic")
    transformative = sum(1 for f in families if f.get("role") == "transformative_opener")

    parts = []
    a = parts.append

    a(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <filter id="glow">
    <feGaussianBlur stdDeviation="4" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>

<rect width="{w}" height="{h}" fill="#03080c"/>
<rect x="28" y="28" width="{w-56}" height="{h-56}" rx="28" fill="#08141b" stroke="#234653" stroke-width="3"/>

<text x="62" y="92" fill="#dff8ff" font-size="42" font-family="monospace">CRYSTAL LIBRARY</text>
<text x="62" y="136" fill="#8fb8c8" font-size="24" font-family="monospace">Mobile Control Panel</text>

<rect x="62" y="170" width="956" height="150" rx="18" fill="#101d25" stroke="#395f70" stroke-width="2"/>
<text x="92" y="218" fill="#eaffff" font-size="28" font-family="monospace">Families tracked: {len(families)}</text>
<text x="92" y="260" fill="#55d6ff" font-size="26" font-family="monospace">Stable diagnostic: {stable}</text>
<text x="92" y="300" fill="#7dff9b" font-size="26" font-family="monospace">Transformative opener: {transformative}</text>

<circle cx="540" cy="395" r="52" fill="#061016" stroke="#8feaff" stroke-width="4" filter="url(#glow)"/>
<text x="360" y="350" fill="#dff8ff" font-size="24" font-family="monospace">FAMILY INDEX CORE</text>
''')

    y = 540
    for i, fam in enumerate(families, start=1):
        name = str(fam.get("family", "unknown"))
        role = str(fam.get("role", "unknown"))
        color = role_color(role)
        turns = fam.get("turns", 0)
        stability = float(fam.get("stability", 0.0) or 0.0)
        release = float((fam.get("avg_delta") or {}).get("release", 0.0) or 0.0)
        summary = str(fam.get("summary", ""))

        card_h = 275
        a(f'<rect x="62" y="{y}" width="956" height="{card_h}" rx="22" fill="#101d25" stroke="{color}" stroke-width="3"/>')
        a(f'<rect x="88" y="{y+26}" width="22" height="82" rx="4" fill="{color}" filter="url(#glow)"/>')
        a(f'<text x="132" y="{y+60}" fill="#eaffff" font-size="34" font-family="monospace">{i}. {escape(name)}</text>')
        a(f'<text x="132" y="{y+105}" fill="{color}" font-size="27" font-family="monospace">role: {escape(role)}</text>')

        a(f'<text x="132" y="{y+150}" fill="#cfe8f0" font-size="24" font-family="monospace">turns: {turns}</text>')
        a(f'<text x="390" y="{y+150}" fill="#cfe8f0" font-size="24" font-family="monospace">stability: {stability:.3f}</text>')
        a(f'<text x="132" y="{y+188}" fill="#cfe8f0" font-size="24" font-family="monospace">release delta: {release:+.3f}</text>')

        bar_w = int(420 * max(0.0, min(1.0, stability)))
        a(f'<rect x="560" y="{y+171}" width="420" height="20" rx="8" fill="#21343d"/>')
        a(f'<rect x="560" y="{y+171}" width="{bar_w}" height="20" rx="8" fill="{color}"/>')

        sy = y + 226
        for line in wrap_lines(summary, width=58, max_lines=2):
            a(f'<text x="132" y="{sy}" fill="#8fb8c8" font-size="18" font-family="monospace">{escape(line)}</text>')
            sy += 24

        y += card_h + 42

    a(f'''
<rect x="62" y="{h-145}" width="956" height="82" rx="18" fill="#101d25" stroke="#395f70" stroke-width="2"/>
<text x="92" y="{h-96}" fill="#dff8ff" font-size="23" font-family="monospace">Known families become instruments.</text>
<text x="92" y="{h-62}" fill="#8fb8c8" font-size="21" font-family="monospace">Repeated shapes become navigable controls.</text>

<text x="62" y="{h-25}" fill="#527987" font-size="16" font-family="monospace">Generated: {escape(str(data.get("generated_at", "?")))}</text>
</svg>''')

    return "\n".join(parts)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = load_index()
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = OUT_DIR / f"{stamp}_crystal_library_mobile.svg"
    out.write_text(render_svg(data), encoding="utf-8")

    print("MOBILE CRYSTAL INDEX SVG WRITTEN")
    print(out)


if __name__ == "__main__":
    main()

