#!/usr/bin/env python3
"""
Le'Veon Topology SVG Renderer
Turns latest topology spec JSON into a deterministic local SVG map.

Input:
  logs/topology_specs/*.json

Output:
  logs/topology_renders/*.svg
"""

from __future__ import annotations

import json
import math
import sys
import datetime
from pathlib import Path
from html import escape


SPEC_DIR = Path("logs/topology_specs")
OUT_DIR = Path("logs/topology_renders")


def latest_spec_path() -> Path:
    specs = sorted(SPEC_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not specs:
        raise FileNotFoundError("No topology specs found in logs/topology_specs")
    return specs[0]


def load_spec(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def metric(spec: dict, name: str) -> dict:
    return spec.get("metrics", {}).get(name, {})


def line_path(x1, y1, x2, y2, curve=0):
    cx1 = x1 + (x2 - x1) * 0.42
    cx2 = x1 + (x2 - x1) * 0.58
    return f"M{x1},{y1} C{cx1},{y1+curve} {cx2},{y2-curve} {x2},{y2}"


def render_svg(spec: dict) -> str:
    width = 1600
    height = 900

    family = spec.get("active_family", "unknown")
    role = spec.get("active_role", "unknown")
    title = spec.get("title", "CORE FUNCTIONAL TOPOLOGY")
    subtitle = spec.get("subtitle", "")
    signature = spec.get("signature", "")
    stability = spec.get("signature_stability", 0.0)
    summary = spec.get("summary", "")

    pull = metric(spec, "pull")
    bind = metric(spec, "bind")
    resist = metric(spec, "resist")
    release = metric(spec, "release")

    pull_v = float(pull.get("value", 0.0))
    bind_v = float(bind.get("value", 0.0))
    resist_v = float(resist.get("value", 0.0))
    release_v = float(release.get("value", 0.0))

    cx = 800
    cy = 455
    core_r = 112 + int(bind_v * 42)

    left_x = 90
    core_left = cx - core_r
    core_right = cx + core_r
    right_x = 1510

    flow_lines = max(6, int(8 + pull_v * 10))
    release_lines = max(6, int(8 + release_v * 10))
    resist_lines = max(2, int(2 + resist_v * 14))

    parts = []

    def add(s):
        parts.append(s)

    add(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs>
  <radialGradient id="coreGlow" cx="50%" cy="50%" r="60%">
    <stop offset="0%" stop-color="#8fdcff" stop-opacity="0.35"/>
    <stop offset="55%" stop-color="#2b8fc0" stop-opacity="0.18"/>
    <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
  </radialGradient>
  <filter id="softGlow">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>

<rect x="0" y="0" width="{width}" height="{height}" fill="#071014"/>
<rect x="24" y="24" width="{width-48}" height="{height-48}" rx="18" fill="#0b161d" stroke="#28404d" stroke-width="2"/>
<rect x="48" y="48" width="{width-96}" height="{height-96}" rx="10" fill="none" stroke="#1b3440" stroke-width="1"/>

<text x="70" y="82" fill="#cfefff" font-size="34" font-family="monospace">{escape(title)}</text>
<text x="70" y="118" fill="#8eb3c4" font-size="22" font-family="monospace">{escape(subtitle)}</text>

<rect x="1060" y="54" width="470" height="126" rx="8" fill="#101b23" stroke="#5b7b8b"/>
<text x="1080" y="86" fill="#bfeaff" font-size="20" font-family="monospace">ACTIVE FAMILY: {escape(str(family))}</text>
<text x="1080" y="116" fill="#bfeaff" font-size="20" font-family="monospace">ACTIVE ROLE: {escape(str(role))}</text>
<text x="1080" y="146" fill="#92b4c0" font-size="14" font-family="monospace">SIGNATURE: {escape(str(signature))}</text>

<rect x="70" y="150" width="430" height="102" rx="8" fill="#101b23" stroke="#5b7b8b"/>
<line x1="86" y1="170" x2="86" y2="232" stroke="#36ff8f" stroke-width="6"/>
<text x="108" y="190" fill="#e6f7ff" font-size="23" font-family="monospace">SIGNATURE STABILITY: {stability}</text>
<text x="108" y="224" fill="#e6f7ff" font-size="23" font-family="monospace">SYSTEM STATE: {escape(str(role).replace("_", " ").title())}</text>

<rect x="1120" y="205" width="390" height="118" rx="8" fill="#101b23" stroke="#5b7b8b"/>
<text x="1140" y="238" fill="#e6f7ff" font-size="25" font-family="monospace">SIGNATURE STABILITY: {stability}</text>
<text x="1140" y="272" fill="#a9c7d5" font-size="16" font-family="monospace">SUMMARY:</text>
<text x="1140" y="298" fill="#a9c7d5" font-size="14" font-family="monospace">{escape(str(summary)[:52])}</text>
''')

    # core glow and rings
    add(f'<circle cx="{cx}" cy="{cy}" r="{core_r+82}" fill="url(#coreGlow)"/>')
    for i in range(5):
        r = core_r + i * 20
        opacity = 0.65 - i * 0.09
        add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#7bd8ff" stroke-width="2" opacity="{opacity:.2f}"/>')

    add(f'<circle cx="{cx}" cy="{cy}" r="{core_r}" fill="#081219" stroke="#8ee7ff" stroke-width="4" filter="url(#softGlow)"/>')
    add(f'<text x="{cx-150}" y="{cy-8}" fill="#dff8ff" font-size="21" font-family="monospace">CORE FIELD / BIND</text>')
    add(f'<text x="{cx-118}" y="{cy+24}" fill="#aac6d2" font-size="16" font-family="monospace">value={bind_v:.2f}, band={escape(str(bind.get("band")))}</text>')

    # incoming pull lines
    for i in range(flow_lines):
        offset = (i - flow_lines / 2) * 15
        y1 = cy + offset * 1.45
        y2 = cy + offset * 0.55
        curve = math.sin(i) * 18
        add(f'<path d="{line_path(left_x, y1, core_left, y2, curve)}" fill="none" stroke="#74d7ff" stroke-width="2" opacity="0.72"/>')
        add(f'<polygon points="{core_left-4},{y2-4} {core_left+8},{y2} {core_left-4},{y2+4}" fill="#74d7ff" opacity="0.8"/>')

    # release output lines
    for i in range(release_lines):
        offset = (i - release_lines / 2) * 15
        y1 = cy + offset * 0.55
        y2 = cy + offset * 1.45
        curve = math.cos(i) * 18
        add(f'<path d="{line_path(core_right, y1, right_x, y2, curve)}" fill="none" stroke="#74d7ff" stroke-width="2" opacity="0.76"/>')
        add(f'<polygon points="{right_x-10},{y2-4} {right_x+4},{y2} {right_x-10},{y2+4}" fill="#74d7ff" opacity="0.85"/>')

    # resist crossing currents
    for i in range(resist_lines):
        yoff = (i - resist_lines / 2) * 34
        add(f'<path d="M{cx-330},{cy-210+yoff} C{cx-150},{cy-20-yoff} {cx+150},{cy+20+yoff} {cx+330},{cy+210-yoff}" fill="none" stroke="#ffad4d" stroke-width="2" opacity="0.55"/>')
        add(f'<path d="M{cx-330},{cy+210-yoff} C{cx-150},{cy+20+yoff} {cx+150},{cy-20-yoff} {cx+330},{cy-210+yoff}" fill="none" stroke="#ffad4d" stroke-width="2" opacity="0.55"/>')

    # labels
    add(f'<text x="74" y="{cy+8}" fill="#a9c7d5" font-size="23" font-family="monospace">Past-&gt;Present</text>')
    add(f'<text x="288" y="{cy+8}" fill="#dff8ff" font-size="19" font-family="monospace">PULL / FLOW value={pull_v:.2f}, band={escape(str(pull.get("band")))}</text>')
    add(f'<text x="{core_right+34}" y="{cy+8}" fill="#dff8ff" font-size="19" font-family="monospace">RELEASE / OPENING value={release_v:.2f}, band={escape(str(release.get("band")))}</text>')
    add(f'<text x="1350" y="{cy+8}" fill="#a9c7d5" font-size="23" font-family="monospace">Present-&gt;Near_Future</text>')
    add(f'<text x="{cx+190}" y="{cy+178}" fill="#ffbd73" font-size="18" font-family="monospace">RESIST / FRICTION value={resist_v:.2f}, band={escape(str(resist.get("band")))}</text>')

    # time axis
    add(f'<line x1="360" y1="790" x2="1220" y2="790" stroke="#9fdfff" stroke-width="2"/>')
    add(f'<text x="370" y="824" fill="#cfefff" font-size="22" font-family="monospace">TIME AXIS: left=past   center=present   right=near_future</text>')
    add(f'<text x="620" y="856" fill="#8eb3c4" font-size="18" font-family="monospace">raw={escape(str(spec.get("time_axis", {}).get("raw")))}</text>')

    # diagram key
    add('<rect x="1170" y="655" width="340" height="170" rx="8" fill="#101b23" stroke="#5b7b8b"/>')
    add('<text x="1192" y="690" fill="#e6f7ff" font-size="22" font-family="monospace">DIAGRAM KEY</text>')

    y = 724
    colors = ["#2ccc7a", "#6a8cff", "#ffb84d", "#c77dff", "#ff6a8a"]
    for idx, item in enumerate(spec.get("diagram_key", [])[:5], start=1):
        color = colors[(idx - 1) % len(colors)]
        fam = str(item.get("family"))
        role_i = str(item.get("role"))
        turns = item.get("turns")
        stab = item.get("stability")
        add(f'<rect x="1190" y="{y-20}" width="24" height="24" fill="{color}" opacity="0.85"/>')
        add(f'<text x="1197" y="{y-2}" fill="#ffffff" font-size="15" font-family="monospace">{idx}</text>')
        add(f'<text x="1224" y="{y-2}" fill="#e6f7ff" font-size="15" font-family="monospace">{escape(fam)} role={escape(role_i)}</text>')
        add(f'<text x="1224" y="{y+18}" fill="#9eb7c2" font-size="13" font-family="monospace">turns={turns}, stability={stab}</text>')
        y += 42

    add('</svg>')
    return "\n".join(parts)


def write_svg(spec_path: Path) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    spec = load_spec(spec_path)

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    family = str(spec.get("active_family", "unknown")).replace("/", "_")
    out = OUT_DIR / f"{stamp}_{family}.svg"

    out.write_text(render_svg(spec), encoding="utf-8")
    return out


def main() -> None:
    arg = " ".join(sys.argv[1:]).strip()
    spec_path = Path(arg) if arg else latest_spec_path()

    out = write_svg(spec_path)

    print("TOPOLOGY SVG WRITTEN")
    print("--------------------")
    print(out)


if __name__ == "__main__":
    main()

