#!/usr/bin/env python3
"""
Le'Veon Visual Turn Runner

One command:
  python runtime/leveon_visual_turn.py "prompt here"

Does:
1. run SGE/API response
2. log turn
3. update Crystal Index
4. write topology spec
5. render topology SVG/PNG
6. render mobile Crystal dashboard SVG/PNG
7. copy PNG/SVG files to Android Downloads
8. print final paths
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import datetime
from pathlib import Path

from runtime.sge_api import respond
from runtime.topology_spec import write_topology_spec
from runtime.topology_svg_renderer import write_svg as write_topology_svg
from runtime.crystal_index import write_index
from runtime.crystal_index_mobile_svg_renderer import load_index, render_svg as render_mobile_index_svg
from runtime.shape_transform_svg_renderer import render_svg as render_transform_svg, OUT_DIR as TRANSFORM_RENDER_DIR


DOWNLOAD_DIR = Path.home() / "storage" / "downloads" / "leveon_topology"
MOBILE_RENDER_DIR = Path("logs/crystal_index_mobile_renders")


def convert_svg_to_png(svg_path: Path, width: int) -> Path | None:
    png_path = svg_path.with_suffix(".png")

    if not shutil.which("rsvg-convert"):
        print("[WARN] rsvg-convert not found. Install with: pkg install -y librsvg")
        return None

    subprocess.run(
        ["rsvg-convert", "-w", str(width), str(svg_path), "-o", str(png_path)],
        check=True,
    )
    return png_path


def copy_to_downloads(*paths: Path) -> list[Path]:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    copied = []

    for p in paths:
        if p and p.exists():
            dest = DOWNLOAD_DIR / p.name
            shutil.copy2(p, dest)
            copied.append(dest)

    return copied


def write_mobile_dashboard_svg() -> Path:
    MOBILE_RENDER_DIR.mkdir(parents=True, exist_ok=True)
    data = load_index()

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = MOBILE_RENDER_DIR / f"{stamp}_crystal_library_mobile.svg"
    out.write_text(render_mobile_index_svg(data), encoding="utf-8")
    return out


def main() -> None:
    prompt = " ".join(sys.argv[1:]).strip()
    if not prompt:
        prompt = "visual image helps improve the build"

    print("LE'VEON VISUAL TURN")
    print("-------------------")
    print("PROMPT:", prompt)
    print()

    # 1. API response, log turn, update index
    result = respond(prompt, do_log=True, update_index=True, include_visuals=False)

    print("VOICE SOURCE:", result.get("voice_source"))
    print("FAMILY      :", result.get("crystal_family_role", {}).get("family"))
    print("ROLE        :", result.get("crystal_family_role", {}).get("role"))
    print("SIGNATURE   :", result.get("shape_signature_in"))
    print("NEXT ACTION :", result.get("john_next_action"))
    print()

    print("SAVARIEL:")
    print(result.get("savariel", ""))
    print()

    # 2. Ensure Crystal Index is current
    index = write_index()
    print("CRYSTAL INDEX UPDATED:")
    print("logs/crystal_family_index.json | families=", index.get("family_count"))
    print()

    # 3. Topology spec + topology render
    topology_spec_path = write_topology_spec(prompt)
    topology_svg = write_topology_svg(topology_spec_path)
    topology_png = convert_svg_to_png(topology_svg, width=1600)

    # 4. Mobile Crystal dashboard render
    mobile_svg = write_mobile_dashboard_svg()
    mobile_png = convert_svg_to_png(mobile_svg, width=1080)

    # 5. Optional transform panel for transformative opener families
    transform_svg = None
    transform_png = None
    active_role = result.get("crystal_family_role", {}).get("role")

    if active_role == "transformative_opener":
        TRANSFORM_RENDER_DIR.mkdir(parents=True, exist_ok=True)
        transform_svg_text, transform_family = render_transform_svg(prompt)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        transform_svg = TRANSFORM_RENDER_DIR / f"{stamp}_{transform_family}_transform.svg"
        transform_svg.write_text(transform_svg_text, encoding="utf-8")
        transform_png = convert_svg_to_png(transform_svg, width=1600)

    # 6. Copy outputs
    copied = copy_to_downloads(
        topology_spec_path,
        topology_svg,
        topology_png,
        mobile_svg,
        mobile_png,
        transform_svg,
        transform_png,
    )

    print("GENERATED:")
    print("topology_spec :", topology_spec_path)
    print("topology_svg  :", topology_svg)
    print("topology_png  :", topology_png if topology_png else "[not created]")
    print("mobile_svg    :", mobile_svg)
    print("mobile_png    :", mobile_png if mobile_png else "[not created]")
    print("transform_svg :", transform_svg if transform_svg else "[not needed]")
    print("transform_png :", transform_png if transform_png else "[not needed]")
    print()

    print("COPIED TO ANDROID DOWNLOADS:")
    for p in copied:
        print(p)

    print()
    print("DONE.")


if __name__ == "__main__":
    main()

