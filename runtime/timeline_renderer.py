#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from runtime.timeline_data import build_timeline_window


OUT_DIR = Path("logs/timeline_renders")
DOWNLOAD_DIR = Path.home() / "storage" / "downloads" / "leveon_topology"

FAMILY_COLORS = {
    "visual_runtime": "#6ec6ff",
    "gravity_grief": "#9cff9c",
    "build_path": "#7bd389",
    "unknown": "#999999",
}

ROLE_COLORS = {
    "stable_diagnostic": "#6ec6ff",
    "transformative_opener": "#9cff9c",
    "unknown": "#aaaaaa",
}

BG = "#07131c"
PANEL = "#0b1a26"
GRID = "#1d3343"
TEXT = "#d7f0ff"
MUTED = "#88a9bf"
ACCENT = "#7cd7ff"
LINE = "#9be7ff"
PULSE = "#98ff98"
NEG_PULSE = "#ffb066"


def esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def convert_svg_to_png(svg_path: Path, width: int = 1600) -> Path | None:
    if not shutil.which("rsvg-convert"):
        return None
    png_path = svg_path.with_suffix(".png")
    subprocess.run(
        ["rsvg-convert", "-w", str(width), str(svg_path), "-o", str(png_path)],
        check=True,
    )
    return png_path


def copy_latest(*paths: Path) -> list[Path]:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []

    for src in paths:
        if src and src.exists():
            dest = DOWNLOAD_DIR / src.name
            shutil.copy2(src, dest)
            copied.append(dest)

    return copied


def render_svg(data: dict, width: int = 1400, height: int = 560) -> str:
    rows = data["rows"]
    n = max(len(rows), 1)

    margin_left = 70
    margin_right = 30
    plot_left = margin_left
    plot_right = width - margin_right
    plot_width = plot_right - plot_left

    stability_top = 90
    stability_h = 120

    pulse_top = 255
    pulse_h = 120
    pulse_mid = pulse_top + (pulse_h / 2)

    strata_top = 420
    strata_h = 44

    def x_at(i: int) -> float:
        if n == 1:
            return plot_left + plot_width / 2
        return plot_left + (i / (n - 1)) * plot_width

    def y_stability(v: float) -> float:
        v = clamp(v, 0.0, 1.0)
        return stability_top + stability_h - (v * stability_h)

    def pulse_height(z: float) -> float:
        z = clamp(z, -2.5, 2.5)
        return abs(z) / 2.5 * (pulse_h / 2 - 8)

    parts: list[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    parts.append(f'<rect width="100%" height="100%" fill="{BG}"/>')
    parts.append(f'<rect x="18" y="18" width="{width-36}" height="{height-36}" rx="18" fill="{PANEL}" stroke="{GRID}" stroke-width="2"/>')

    parts.append(f'<text x="40" y="52" fill="{TEXT}" font-size="28" font-family="monospace">TEMPORAL TIMELINE: trend-aware runtime</text>')
    parts.append(f'<text x="40" y="78" fill="{MUTED}" font-size="15" font-family="monospace">The moment is a point; the timeline is the path.</text>')

    # Section labels
    parts.append(f'<text x="40" y="{stability_top-14}" fill="{ACCENT}" font-size="18" font-family="monospace">1. Stability Wave (signature stability)</text>')
    parts.append(f'<text x="40" y="{pulse_top-14}" fill="{ACCENT}" font-size="18" font-family="monospace">2. Release Pulse (normalized z-score by family)</text>')
    parts.append(f'<text x="40" y="{strata_top-14}" fill="{ACCENT}" font-size="18" font-family="monospace">3. Family Transition (cluster density / occupancy)</text>')

    # Grid lines stability
    for frac, label in ((0.25, "0.25"), (0.50, "0.50"), (0.75, "0.75"), (1.00, "1.00")):
        y = y_stability(frac)
        parts.append(f'<line x1="{plot_left}" y1="{y:.1f}" x2="{plot_right}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="18" y="{y+5:.1f}" fill="{MUTED}" font-size="12" font-family="monospace">{label}</text>')

    # Stability polyline
    if rows:
        points = " ".join(f"{x_at(i):.2f},{y_stability(row['stability']):.2f}" for i, row in enumerate(rows))
        parts.append(f'<polyline fill="none" stroke="{LINE}" stroke-width="3" points="{points}"/>')
        for i, row in enumerate(rows):
            x = x_at(i)
            y = y_stability(row["stability"])
            color = FAMILY_COLORS.get(row["family"], FAMILY_COLORS["unknown"])
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.5" fill="{color}" stroke="{TEXT}" stroke-width="1"/>')

    # Pulse baseline
    parts.append(f'<line x1="{plot_left}" y1="{pulse_mid:.1f}" x2="{plot_right}" y2="{pulse_mid:.1f}" stroke="{GRID}" stroke-width="1.5"/>')
    parts.append(f'<text x="18" y="{pulse_mid+5:.1f}" fill="{MUTED}" font-size="12" font-family="monospace">0</text>')

    # Pulses
    bar_w = max(8, plot_width / max(n, 10) * 0.55)
    for i, row in enumerate(rows):
        x = x_at(i)
        z = row["release_z"]
        h = pulse_height(z)
        color = PULSE if z >= 0 else NEG_PULSE
        if z >= 0:
            y = pulse_mid - h
        else:
            y = pulse_mid
        parts.append(
            f'<rect x="{x - bar_w/2:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{max(h,2):.2f}" '
            f'rx="2" fill="{color}" opacity="0.92"/>'
        )

    # Family strata
    cell_w = plot_width / n
    for i, row in enumerate(rows):
        x = plot_left + i * cell_w
        color = FAMILY_COLORS.get(row["family"], FAMILY_COLORS["unknown"])
        parts.append(f'<rect x="{x:.2f}" y="{strata_top}" width="{cell_w+1:.2f}" height="{strata_h}" fill="{color}" opacity="0.85"/>')

    # Tick labels
    for i, row in enumerate(rows):
        if i == 0 or i == len(rows) - 1 or i % max(1, len(rows)//8) == 0:
            x = x_at(i)
            parts.append(f'<line x1="{x:.2f}" y1="{strata_top+strata_h}" x2="{x:.2f}" y2="{strata_top+strata_h+7}" stroke="{GRID}" stroke-width="1"/>')
            parts.append(f'<text x="{x:.2f}" y="{strata_top+strata_h+22}" fill="{MUTED}" font-size="11" font-family="monospace" text-anchor="middle">{i+1}</text>')

    # Legend
    lx = width - 290
    ly = 420
    parts.append(f'<rect x="{lx}" y="{ly}" width="240" height="110" rx="10" fill="{PANEL}" stroke="{GRID}" stroke-width="1.5"/>')
    parts.append(f'<text x="{lx+16}" y="{ly+24}" fill="{TEXT}" font-size="16" font-family="monospace">FAMILY LEGEND</text>')

    legend_items = [("visual_runtime", FAMILY_COLORS["visual_runtime"]),
                    ("gravity_grief", FAMILY_COLORS["gravity_grief"]),
                    ("build_path", FAMILY_COLORS["build_path"])]
    for idx, (name, color) in enumerate(legend_items):
        yy = ly + 48 + idx * 22
        parts.append(f'<rect x="{lx+16}" y="{yy-11}" width="12" height="12" rx="2" fill="{color}"/>')
        parts.append(f'<text x="{lx+38}" y="{yy}" fill="{TEXT}" font-size="13" font-family="monospace">{esc(name)}</text>')

    # Summary panel
    sx = width - 360
    sy = 38
    latest = rows[-1] if rows else {"family": "none", "role": "none", "release_delta": 0.0, "stability": 0.0}
    parts.append(f'<rect x="{sx}" y="{sy}" width="320" height="150" rx="12" fill="{PANEL}" stroke="{GRID}" stroke-width="1.5"/>')
    parts.append(f'<text x="{sx+18}" y="{sy+28}" fill="{TEXT}" font-size="18" font-family="monospace">TIMELINE SUMMARY</text>')
    parts.append(f'<text x="{sx+18}" y="{sy+56}" fill="{ACCENT}" font-size="13" font-family="monospace">window turns: {data["turn_count"]}</text>')
    parts.append(f'<text x="{sx+18}" y="{sy+78}" fill="{TEXT}" font-size="13" font-family="monospace">avg stability: {data["avg_stability"]:.3f}</text>')
    parts.append(f'<text x="{sx+18}" y="{sy+100}" fill="{TEXT}" font-size="13" font-family="monospace">avg release Δ: {data["avg_release_delta"]:+.3f}</text>')
    parts.append(f'<text x="{sx+18}" y="{sy+122}" fill="{TEXT}" font-size="13" font-family="monospace">latest family: {esc(latest["family"])}</text>')
    parts.append(f'<text x="{sx+18}" y="{sy+144}" fill="{TEXT}" font-size="13" font-family="monospace">latest role: {esc(latest["role"])}</text>')

    # Footer note
    parts.append(f'<text x="40" y="{height-28}" fill="{MUTED}" font-size="13" font-family="monospace">Look for the rhythm in the pulses — that is where the build finds its heartbeat.</text>')

    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Le'Veon runtime timeline from logs/sge_turns.jsonl")
    parser.add_argument("--last", type=int, default=40, help="number of most recent turns to render")
    args = parser.parse_args()

    data = build_timeline_window(last_n=args.last)

    if not data["rows"]:
        print("No timeline data found in logs/sge_turns.jsonl")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    svg_path = OUT_DIR / f"{stamp}_runtime_timeline.svg"
    svg_path.write_text(render_svg(data), encoding="utf-8")

    png_path = convert_svg_to_png(svg_path, width=1600)

    copied = copy_latest(svg_path)
    latest_svg = DOWNLOAD_DIR / "timeline_latest.svg"
    shutil.copy2(svg_path, latest_svg)
    copied.append(latest_svg)

    if png_path and png_path.exists():
        copy_latest(png_path)
        latest_png = DOWNLOAD_DIR / "timeline_latest.png"
        shutil.copy2(png_path, latest_png)
        copied.append(latest_png)

    print("RUNTIME TIMELINE WRITTEN")
    print("------------------------")
    print("svg :", svg_path)
    print("png :", png_path if png_path else "[not created - install librsvg]")
    print()
    print("COPIED:")
    for path in copied:
        print(path)


if __name__ == "__main__":
    main()

