#!/usr/bin/env python3
"""
Le'Veon Shape Transform SVG Renderer
Creates a before/after transformation panel from a live SGE/API prompt.
Best for transformative families like gravity_grief.
"""

from __future__ import annotations

import sys
import datetime
import subprocess
import shutil
from pathlib import Path
from html import escape

from runtime.sge_api import respond


OUT_DIR = Path("logs/shape_transform_renders")
DOWNLOAD_DIR = Path.home() / "storage" / "downloads" / "leveon_topology"


def _num(shape, key):
    try:
        return float(shape.get(key, 0.0))
    except Exception:
        return 0.0


def _bar(value, width=360):
    try:
        v = max(0.0, min(1.0, float(value)))
    except Exception:
        v = 0.0
    return int(v * width)


def render_svg(prompt: str) -> tuple[str, str]:
    data = respond(prompt, do_log=False, update_index=False, include_visuals=False)

    shape_in = data["shape_in"]
    shape_out = data["shape_out"]
    delta = data["shape_delta"]
    role = data["crystal_family_role"]

    family = role.get("family", "unknown")
    role_name = role.get("role", "unknown")
    sig = data.get("shape_signature_in", "")

    in_release = _num(shape_in, "release")
    out_release = _num(shape_out, "release")
    release_delta = float(delta.get("release", 0.0))

    in_pull = _num(shape_in, "pull")
    in_bind = _num(shape_in, "bind")
    in_resist = _num(shape_in, "resist")

    out_pull = _num(shape_out, "pull")
    out_bind = _num(shape_out, "bind")
    out_resist = _num(shape_out, "resist")

    w, h = 1600, 900
    left_cx, right_cx, cy = 460, 1140, 455

    color = "#7dff9b" if role_name == "transformative_opener" else "#55d6ff"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <filter id="glow">
    <feGaussianBlur stdDeviation="4" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>

<rect width="{w}" height="{h}" fill="#050b0f"/>
<rect x="26" y="26" width="{w-52}" height="{h-52}" rx="20" fill="#08141b" stroke="#234653" stroke-width="3"/>

<text x="70" y="88" fill="#dff8ff" font-size="36" font-family="monospace">SHAPE TRANSFORMATION: {escape(family)}</text>
<text x="70" y="128" fill="#8fb8c8" font-size="22" font-family="monospace">Role: {escape(role_name)} | Signature: {escape(sig[:85])}</text>

<rect x="70" y="168" width="1460" height="88" rx="12" fill="#101d25" stroke="{color}" stroke-width="2"/>
<text x="100" y="214" fill="{color}" font-size="26" font-family="monospace">release delta: {release_delta:+.3f}</text>
<text x="480" y="214" fill="#dff8ff" font-size="22" font-family="monospace">input release={in_release:.2f}</text>
<text x="820" y="214" fill="#dff8ff" font-size="22" font-family="monospace">output release={out_release:.2f}</text>
<text x="1160" y="214" fill="#8fb8c8" font-size="18" font-family="monospace">source: {escape(data.get("voice_source", ""))}</text>

<!-- LEFT INPUT FIELD -->
<circle cx="{left_cx}" cy="{cy}" r="145" fill="#061016" stroke="#5faec9" stroke-width="3"/>
<circle cx="{left_cx}" cy="{cy}" r="190" fill="none" stroke="#315a68" stroke-width="2"/>
<circle cx="{left_cx}" cy="{cy}" r="230" fill="none" stroke="#234653" stroke-width="2"/>
<text x="{left_cx-150}" y="{cy-178}" fill="#dff8ff" font-size="26" font-family="monospace">INPUT SHAPE</text>
<text x="{left_cx-135}" y="{cy-8}" fill="#dff8ff" font-size="22" font-family="monospace">BIND {in_bind:.2f}</text>
<text x="{left_cx-135}" y="{cy+28}" fill="#8fb8c8" font-size="18" font-family="monospace">PULL {in_pull:.2f} / RESIST {in_resist:.2f}</text>

<!-- RIGHT OUTPUT FIELD -->
<circle cx="{right_cx}" cy="{cy}" r="145" fill="#061016" stroke="{color}" stroke-width="5" filter="url(#glow)"/>
<circle cx="{right_cx}" cy="{cy}" r="190" fill="none" stroke="{color}" stroke-width="2" opacity="0.65"/>
<circle cx="{right_cx}" cy="{cy}" r="230" fill="none" stroke="{color}" stroke-width="2" opacity="0.45"/>
<text x="{right_cx-160}" y="{cy-178}" fill="#dff8ff" font-size="26" font-family="monospace">OUTPUT SHAPE</text>
<text x="{right_cx-135}" y="{cy-8}" fill="#dff8ff" font-size="22" font-family="monospace">BIND {out_bind:.2f}</text>
<text x="{right_cx-135}" y="{cy+28}" fill="#8fb8c8" font-size="18" font-family="monospace">PULL {out_pull:.2f} / RESIST {out_resist:.2f}</text>

<!-- TRANSFORMATION BRIDGE -->
<path d="M620,{cy} C760,{cy-120} 840,{cy-120} 980,{cy}" fill="none" stroke="{color}" stroke-width="5" filter="url(#glow)"/>
<path d="M620,{cy+36} C760,{cy+140} 840,{cy+140} 980,{cy+36}" fill="none" stroke="{color}" stroke-width="3" opacity="0.75"/>
<polygon points="975,{cy-10} 1002,{cy} 975,{cy+10}" fill="{color}"/>
<text x="690" y="{cy-150}" fill="{color}" font-size="24" font-family="monospace">TRANSFORMATION: OPENING INCREASED</text>
<text x="724" y="{cy+190}" fill="#8fb8c8" font-size="20" font-family="monospace">same signature, changed release field</text>

<!-- RELEASE BARS -->
<text x="105" y="740" fill="#dff8ff" font-size="23" font-family="monospace">INPUT RELEASE</text>
<rect x="330" y="718" width="360" height="26" rx="10" fill="#21343d"/>
<rect x="330" y="718" width="{_bar(in_release)}" height="26" rx="10" fill="#5faec9"/>

<text x="805" y="740" fill="#dff8ff" font-size="23" font-family="monospace">OUTPUT RELEASE</text>
<rect x="1060" y="718" width="360" height="26" rx="10" fill="#21343d"/>
<rect x="1060" y="718" width="{_bar(out_release)}" height="26" rx="10" fill="{color}"/>

<rect x="70" y="790" width="1460" height="55" rx="10" fill="#101d25" stroke="#315a68"/>
<text x="100" y="825" fill="#dff8ff" font-size="20" font-family="monospace">SAVARIEL: {escape(data.get("savariel", "")[:150])}</text>
</svg>'''

    return svg, family


def main():
    prompt = " ".join(sys.argv[1:]).strip() or "there is a heavy hollow ache sitting in my chest today"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    svg, family = render_svg(prompt)

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    svg_path = OUT_DIR / f"{stamp}_{family}_transform.svg"
    png_path = svg_path.with_suffix(".png")

    svg_path.write_text(svg, encoding="utf-8")

    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-w", "1600", str(svg_path), "-o", str(png_path)], check=True)
    else:
        print("Install converter with: pkg install -y librsvg")

    for p in (svg_path, png_path):
        if p.exists():
            shutil.copy2(p, DOWNLOAD_DIR / p.name)

    print("TRANSFORM PANEL WRITTEN")
    print("-----------------------")
    print("svg:", svg_path)
    print("png:", png_path if png_path.exists() else "[not created]")
    print("downloads:", DOWNLOAD_DIR / png_path.name)


if __name__ == "__main__":
    main()

