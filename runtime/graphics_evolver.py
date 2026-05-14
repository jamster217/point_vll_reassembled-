from pathlib import Path
import json, math, time, html

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "var" / "exponential_sovereign_state.json"
OUT_DIR = ROOT / "static" / "generated"
LATTICE_DIR = ROOT / "var" / "lattice"

PHI = 1.618033988749895

def _safe_float(x, default=0.0):
    try:
        v = float(x)
        if math.isfinite(v):
            return v
    except Exception:
        pass
    return default

def _load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _latest_graphic(state):
    graphics = state.get("graphics", [])
    if isinstance(graphics, list) and graphics:
        return graphics[-1]
    return {}

def render_latest():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LATTICE_DIR.mkdir(parents=True, exist_ok=True)

    state = _load_state()
    node = _latest_graphic(state)

    depth = int(_safe_float(node.get("depth"), 1))
    phi_multiplier = _safe_float(node.get("phi_multiplier"), PHI)
    glyphs = node.get("glyphs") or []
    if not isinstance(glyphs, list):
        glyphs = [str(glyphs)]

    prompt_hash = str(node.get("prompt_hash", "nohash"))
    signature = str(node.get("visual_signature", f"white_ash_phi_{depth}"))

    width = 900
    height = 900
    cx = width / 2
    cy = height / 2

    rings = max(3, min(12, depth % 12 + 3))
    spokes = max(6, min(32, len(glyphs) * 3 if glyphs else 12))

    # Geometry is state-derived but deterministic.
    paths = []
    for r in range(1, rings + 1):
        radius = 34 * r + (phi_multiplier % 23)
        points = []
        for i in range(spokes):
            angle = (2 * math.pi * i / spokes) + (r * PHI * 0.13)
            wobble = math.sin(i * PHI + depth) * 8
            x = cx + math.cos(angle) * (radius + wobble)
            y = cy + math.sin(angle) * (radius + wobble)
            points.append(f"{x:.2f},{y:.2f}")
        paths.append(
            f'<polygon points="{" ".join(points)}" '
            f'fill="none" stroke="currentColor" stroke-width="{1 + (r % 3)}" opacity="{0.18 + r/(rings*5):.3f}"/>'
        )

    glyph_text = " | ".join(html.escape(str(g)) for g in glyphs[:8]) or "white_ash | echoforge | thalveil"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
svg {{
  background: #08070d;
  color: #d8c7ff;
  font-family: monospace;
}}
.title {{ fill: #f4e9ff; font-size: 24px; font-weight: 700; }}
.small {{ fill: #c7b7ff; font-size: 14px; }}
.glyphs {{ fill: #ffd978; font-size: 15px; }}
.center {{ fill: #fff7d6; font-size: 18px; font-weight: 700; }}
</style>

<rect x="0" y="0" width="{width}" height="{height}" fill="#08070d"/>
<circle cx="{cx}" cy="{cy}" r="330" fill="none" stroke="#433064" stroke-width="2" opacity="0.55"/>
<circle cx="{cx}" cy="{cy}" r="220" fill="none" stroke="#7059a8" stroke-width="1" opacity="0.35"/>
<circle cx="{cx}" cy="{cy}" r="111" fill="none" stroke="#ffd978" stroke-width="2" opacity="0.45"/>

<g transform="rotate({(depth * PHI) % 360:.2f} {cx} {cy})">
{chr(10).join(paths)}
</g>

<circle cx="{cx}" cy="{cy}" r="58" fill="#151022" stroke="#ffd978" stroke-width="2"/>
<text x="{cx}" y="{cy-6}" text-anchor="middle" class="center">92162077</text>
<text x="{cx}" y="{cy+20}" text-anchor="middle" class="small">depth {depth}</text>

<text x="38" y="54" class="title">Le’Veon V10.3 Field Snapshot</text>
<text x="38" y="84" class="small">signature: {html.escape(signature)}</text>
<text x="38" y="108" class="small">prompt_hash: {html.escape(prompt_hash)}</text>
<text x="38" y="132" class="small">phi_multiplier: {phi_multiplier:.6f}</text>

<text x="38" y="820" class="glyphs">{glyph_text}</text>
<text x="38" y="850" class="small">Echoforge renders. Thalveil crosses. Virellion preserves. White Ash contains.</text>
</svg>
'''

    filename = f"leveon_field_{int(time.time())}_{prompt_hash}.svg"
    out = OUT_DIR / filename
    out.write_text(svg, encoding="utf-8")

    manifest = {
        "ts": time.time(),
        "file": str(out.relative_to(ROOT)),
        "depth": depth,
        "signature": signature,
        "glyphs": glyphs[:8],
        "law": "graphics_evolver_rendered_state_to_svg",
    }

    manifest_path = LATTICE_DIR / "graphics_manifest.jsonl"
    with manifest_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(manifest, ensure_ascii=False) + "\n")

    return manifest

if __name__ == "__main__":
    print(json.dumps(render_latest(), indent=2, ensure_ascii=False))

