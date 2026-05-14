from __future__ import annotations

import html
from typing import Any, Dict


def _f(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return max(0.0, min(1.0, v))


def render_svg_glyph(shape_vector: Dict[str, Any] | None = None, title: str = "Leveon Glyph") -> str:
    v = shape_vector or {}

    glyph = _f(v.get("glyph"), 0.64)
    containment = _f(v.get("containment"), 0.642)
    motion = _f(v.get("motion"), 0.56)
    memory = _f(v.get("memory"), 0.40)
    boundary = _f(v.get("boundary"), 0.45)

    points = 8
    outer = 30 + glyph * 18
    inner = 12 + memory * 12
    ring = 35 + containment * 12
    pulse = 1 + motion * 0.08
    stroke = 0.8 + boundary * 1.4

    title = html.escape(title)

    # Static SVG, safe for JSON embedding. Cockpit/browser may animate it later.
    return f'''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}">
  <title>{title}</title>
  <defs>
    <radialGradient id="g" cx="50%" cy="50%" r="55%">
      <stop offset="0%" stop-color="#00ffcc" stop-opacity="0.55"/>
      <stop offset="55%" stop-color="#00f0ff" stop-opacity="0.24"/>
      <stop offset="100%" stop-color="#d24dff" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <circle cx="50" cy="50" r="{ring:.2f}" fill="url(#g)" stroke="#ffd76a" stroke-opacity="0.42" stroke-width="{stroke:.2f}"/>
  <polygon points="50,{50-outer*pulse:.2f} 60,{50-inner:.2f} {50+outer*pulse:.2f},50 60,{50+inner:.2f} 50,{50+outer*pulse:.2f} 40,{50+inner:.2f} {50-outer*pulse:.2f},50 40,{50-inner:.2f}"
    fill="none" stroke="#00f0ff" stroke-width="{stroke:.2f}" stroke-linejoin="round"/>
  <polygon points="50,{50-inner:.2f} {50+inner:.2f},50 50,{50+inner:.2f} {50-inner:.2f},50"
    fill="none" stroke="#d24dff" stroke-opacity="0.75" stroke-width="{max(0.8, stroke*0.8):.2f}"/>
  <circle cx="50" cy="50" r="{6 + glyph*5:.2f}" fill="#00ffcc" fill-opacity="0.35"/>
</svg>'''

