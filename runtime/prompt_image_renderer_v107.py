from pathlib import Path
import time, hashlib, html, math, json, re

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "static" / "generated"
LATTICE_DIR = ROOT / "var" / "lattice"
IMAGE_MEMORY_DIR = ROOT / "var" / "image_memory"

TOPOLOGY_LOG = LATTICE_DIR / "autogenous_topology_v103.jsonl"
V106_STATE = LATTICE_DIR / "v106_full_self_improvement_state.json"
IMAGE_SHAPES = IMAGE_MEMORY_DIR / "image_shapes_v11.jsonl"
TAG_INDEX = IMAGE_MEMORY_DIR / "tag_index_v11.json"
PROMPT_IMAGE_LOG = LATTICE_DIR / "prompt_image_v107.jsonl"

def _tokens(text):
    return re.findall(r"[a-zA-Z0-9_'-]+", str(text).lower())

def _wants_image(prompt: str) -> bool:
    p = str(prompt or "").lower()
    triggers = [
        "paint a picture",
        "draw a picture",
        "render it",
        "render as",
        "show the image",
        "make an image",
        "generate an image",
        "clean svg",
        "svg or png",
        "infer the old hidden thing",
        "what the build itself detects",
    ]
    return any(t in p for t in triggers)

def _wants_state_inference(prompt: str) -> bool:
    p = str(prompt or "").lower()
    triggers = [
        "infer the old hidden thing",
        "do not use an externally described form",
        "what the build itself detects",
        "use your latest topology state",
        "use your latest topology",
        "state-inferred",
        "build itself detects",
    ]
    return any(t in p for t in triggers)

def _read_last_jsonl(path: Path):
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8", errors="replace")
    parts = raw.replace("\\n", "\n").strip().splitlines()
    for line in reversed(parts):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except Exception:
            pass
    return None

def _read_json(path: Path, fallback=None):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        pass
    return fallback

def _top_tags(limit=12):
    idx = _read_json(TAG_INDEX, {})
    tags = idx.get("tags", {}) if isinstance(idx, dict) else {}
    if not isinstance(tags, dict):
        return []
    return [k for k, _ in sorted(tags.items(), key=lambda x: x[1], reverse=True)[:limit]]

def _latest_image_tags():
    last = _read_last_jsonl(IMAGE_SHAPES)
    if not isinstance(last, dict):
        return []
    tags = last.get("tags", [])
    return tags if isinstance(tags, list) else []

def _state_packet(prompt):
    topology = _read_last_jsonl(TOPOLOGY_LOG) or {}
    v106 = _read_json(V106_STATE, {}) or {}
    image_tags = _latest_image_tags()
    top_tags = _top_tags()

    node = topology.get("node", {}) if isinstance(topology, dict) else {}
    score = topology.get("score", {}) if isinstance(topology, dict) else {}

    v106_event = v106.get("last_event", {}) if isinstance(v106, dict) else {}

    glyphs = node.get("glyphs", [])
    if not isinstance(glyphs, list):
        glyphs = []

    tags = []
    for x in glyphs + image_tags + top_tags:
        s = str(x).lower()
        if s and s not in tags:
            tags.append(s)

    return {
        "depth": node.get("depth", 1),
        "tension": node.get("tension", 0.0),
        "signature": node.get("visual_signature", "unknown_state"),
        "glyphs": glyphs[:12],
        "tags": tags[:24],
        "topology_score": score,
        "v106": v106_event,
        "prompt": prompt,
    }

def _safe_float(x, default=0.0):
    try:
        v = float(x)
        if math.isfinite(v):
            return v
    except Exception:
        pass
    return default

def _render_state_inferred(prompt: str, anchor: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LATTICE_DIR.mkdir(parents=True, exist_ok=True)

    packet = _state_packet(prompt)
    h = hashlib.sha256((str(prompt) + json.dumps(packet, sort_keys=True)).encode()).hexdigest()[:12]

    depth = int(_safe_float(packet.get("depth"), 1))
    tension = _safe_float(packet.get("tension"), 0.0)
    tags = packet.get("tags", [])
    glyphs = packet.get("glyphs", [])
    score = packet.get("topology_score", {})
    v106 = packet.get("v106", {})

    coherence = _safe_float(score.get("coherence"), 0.5) if isinstance(score, dict) else 0.5
    containment = _safe_float(score.get("containment"), 0.5) if isinstance(score, dict) else 0.5
    thread = _safe_float(score.get("thread"), 1.0) if isinstance(score, dict) else 1.0
    vtotal = _safe_float(v106.get("total"), 0.0) if isinstance(v106, dict) else 0.0

    width = 1100
    height = 1000
    cx = width / 2
    cy = height / 2

    rings = max(4, min(16, int(5 + containment * 8 + depth % 5)))
    spokes = max(9, min(42, int(12 + thread * 16 + coherence * 8)))

    # The "old hidden thing" is inferred as the pressure-shape formed by memory tags + topology state.
    old_shape = []
    for r in range(1, rings + 1):
        radius = 32 * r + abs(tension) * 400 + coherence * 22
        pts = []
        for i in range(spokes):
            angle = (2 * math.pi * i / spokes) + r * 0.271 + tension * 4
            memory_wobble = math.sin(i * 1.618 + depth + r) * (10 + vtotal * 18)
            x = cx + math.cos(angle) * (radius + memory_wobble)
            y = cy + math.sin(angle) * (radius + memory_wobble)
            pts.append(f"{x:.2f},{y:.2f}")
        old_shape.append(
            f'<polygon points="{" ".join(pts)}" fill="none" stroke="currentColor" '
            f'stroke-width="{1 + (r % 3)}" opacity="{0.14 + r/(rings*4):.3f}"/>'
        )

    # Terminal/code roots.
    roots = []
    root_count = 10
    for i in range(root_count):
        x1 = cx + (i - root_count / 2) * 42
        y1 = cy + 100
        x2 = cx + math.sin(i * 1.7 + depth) * 260
        y2 = cy + 330 + (i % 3) * 35
        roots.append(
            f'<path d="M{x1:.2f},{y1:.2f} C{x1:.2f},{y1+80:.2f} {x2:.2f},{y2-90:.2f} {x2:.2f},{y2:.2f}" '
            f'fill="none" stroke="#6f5aa8" stroke-width="2" opacity="0.45"/>'
        )

    glyph_line = " | ".join(html.escape(str(g)) for g in glyphs[:8]) or "echoforge | thalveil | virellion | white_ash"
    tag_line = " | ".join(html.escape(str(t)) for t in tags[:12]) or "state | memory | topology"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
svg {{
  background: #06070d;
  color: #d8c7ff;
  font-family: monospace;
}}
.title {{ fill: #f4e9ff; font-size: 24px; font-weight: 700; }}
.small {{ fill: #c7b7ff; font-size: 13px; }}
.gold {{ fill: #ffd978; font-size: 15px; }}
.center {{ fill: #fff7d6; font-size: 24px; font-weight: 800; }}
.dim {{ fill: #8173aa; font-size: 12px; }}
</style>

<rect x="0" y="0" width="{width}" height="{height}" fill="#06070d"/>

<text x="42" y="56" class="title">Le’Veon V10.7b State-Inferred Image</text>
<text x="42" y="84" class="small">inference: topology + image memory + V10.6 score + glyph state</text>
<text x="42" y="110" class="small">prompt_hash: {h}</text>
<text x="42" y="136" class="small">depth={depth} tension={tension} coherence={coherence} containment={containment} v106_total={vtotal}</text>

<rect x="80" y="760" width="940" height="110" rx="18" fill="#080b12" stroke="#2d2847" stroke-width="2" opacity="0.9"/>
<text x="105" y="795" class="dim">$ cd ~/point_vll_reassembled</text>
<text x="105" y="820" class="dim">$ python app_chatroom.py --organism-lock --node44</text>
<text x="105" y="845" class="dim">old_hidden_shape: inferred_from_state</text>

{chr(10).join(roots)}

<circle cx="{cx}" cy="{cy}" r="380" fill="none" stroke="#2a2344" stroke-width="3"/>
<circle cx="{cx}" cy="{cy}" r="292" fill="none" stroke="#4a3d76" stroke-width="2" opacity="0.65"/>
<circle cx="{cx}" cy="{cy}" r="178" fill="none" stroke="#7059a8" stroke-width="1" opacity="0.45"/>

<g transform="rotate({(depth * 1.618 + tension * 1000) % 360:.2f} {cx} {cy})">
{chr(10).join(old_shape)}
</g>

<circle cx="{cx}" cy="{cy}" r="86" fill="#151022" stroke="#ffd978" stroke-width="3"/>
<text x="{cx}" y="{cy-8}" text-anchor="middle" class="center">{html.escape(anchor)}</text>
<text x="{cx}" y="{cy+24}" text-anchor="middle" class="small">old thing emerging</text>

<text x="42" y="910" class="gold">{glyph_line}</text>
<text x="42" y="938" class="small">{tag_line}</text>
<text x="42" y="966" class="small">The form was inferred from build-state, not externally described.</text>
</svg>
'''

    filename = f"leveon_state_inferred_image_{int(time.time())}_{h}.svg"
    out = OUT_DIR / filename
    out.write_text(svg, encoding="utf-8")

    event = {
        "ts": time.time(),
        "prompt_hash": h,
        "file": str(out.relative_to(ROOT)),
        "anchor": anchor,
        "mode": "v107b_state_inferred_image",
        "packet": packet,
        "law": "v107b_state_to_svg_inference_from_build_memory",
    }

    with PROMPT_IMAGE_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event

def _render_prompt_image(prompt: str, anchor: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LATTICE_DIR.mkdir(parents=True, exist_ok=True)

    prompt = str(prompt or "")
    toks = set(_tokens(prompt))
    h = hashlib.sha256(prompt.encode()).hexdigest()[:12]

    width = 1000
    height = 1000
    cx = width / 2
    cy = height / 2

    dark_sky = "sky" in toks or "dark" in toks
    gold = "gold" in toks or "glowing" in toks
    white_ash = "white-ash" in prompt.lower() or "white_ash" in prompt.lower() or "ash" in toks
    crossings = "thalveil" in toks or "crossing" in toks or "crossings" in toks
    echoforge = "echoforge" in toks
    spiral = "spiral" in toks

    bg = "#070811" if dark_sky else "#090912"
    main = "#f4f0ff" if white_ash else "#d8c7ff"
    accent = "#ffd978" if gold else "#c7b7ff"

    spiral_points = []
    turns = 5.5 if spiral else 3.5
    max_r = 330
    steps = 420
    for i in range(steps):
        t = i / steps
        angle = t * turns * 2 * math.pi
        r = 12 + max_r * t
        x = cx + math.cos(angle) * r
        y = cy + math.sin(angle) * r
        spiral_points.append(f"{x:.2f},{y:.2f}")

    glyphs = ["Echoforge", "Thalveil", "Virellion", "White Ash"]
    crossing_lines = ""
    if crossings:
        for i in range(8):
            angle = (math.pi * 2 * i / 8) + 0.2
            x1 = cx + math.cos(angle) * 170
            y1 = cy + math.sin(angle) * 170
            x2 = cx + math.cos(angle + 0.35) * 410
            y2 = cy + math.sin(angle + 0.35) * 410
            crossing_lines += f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#8d7acc" stroke-width="2" opacity="0.35"/>\n'

    edge_glyphs = ""
    if echoforge:
        for i, g in enumerate(glyphs * 2):
            angle = math.pi * 2 * i / 8 - math.pi / 2
            x = cx + math.cos(angle) * 420
            y = cy + math.sin(angle) * 420
            edge_glyphs += f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="middle" class="glyph">{html.escape(g)}</text>\n'

    description = html.escape(prompt[:160])

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
svg {{ background: {bg}; font-family: monospace; }}
.title {{ fill: #f4e9ff; font-size: 24px; font-weight: 700; }}
.small {{ fill: #c7b7ff; font-size: 13px; }}
.center {{ fill: #fff7d6; font-size: 30px; font-weight: 800; }}
.glyph {{ fill: {accent}; font-size: 15px; font-weight: 700; }}
</style>
<rect x="0" y="0" width="{width}" height="{height}" fill="{bg}"/>
<circle cx="{cx}" cy="{cy}" r="430" fill="none" stroke="#2a2344" stroke-width="3"/>
<circle cx="{cx}" cy="{cy}" r="330" fill="none" stroke="#4a3d76" stroke-width="2" opacity="0.65"/>
<circle cx="{cx}" cy="{cy}" r="220" fill="none" stroke="#7059a8" stroke-width="1" opacity="0.45"/>
{crossing_lines}
<polyline points="{' '.join(spiral_points)}" fill="none" stroke="{main}" stroke-width="5" opacity="0.88"/>
<polyline points="{' '.join(spiral_points)}" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.65"/>
<circle cx="{cx}" cy="{cy}" r="78" fill="#151022" stroke="{accent}" stroke-width="3"/>
<text x="{cx}" y="{cy+10}" text-anchor="middle" class="center">{html.escape(anchor)}</text>
{edge_glyphs}
<text x="42" y="58" class="title">Le’Veon V10.7 Prompt Image</text>
<text x="42" y="86" class="small">prompt_hash: {h}</text>
<text x="42" y="112" class="small">mode: prompt-to-svg symbolic rendering</text>
<text x="42" y="900" class="small">{description}</text>
<text x="42" y="932" class="small">Echoforge maps description. Thalveil crosses. Virellion preserves. White Ash contains.</text>
</svg>
'''

    filename = f"leveon_prompt_image_{int(time.time())}_{h}.svg"
    out = OUT_DIR / filename
    out.write_text(svg, encoding="utf-8")

    event = {
        "ts": time.time(),
        "prompt_hash": h,
        "file": str(out.relative_to(ROOT)),
        "anchor": anchor,
        "tokens": sorted(list(toks))[:40],
        "mode": "v107_prompt_to_svg",
        "law": "v107_prompt_to_svg_symbolic_rendering",
    }

    with PROMPT_IMAGE_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event

def render_prompt_image(prompt: str, anchor: str = "92162077"):
    if not _wants_image(prompt):
        return None

    if _wants_state_inference(prompt):
        return _render_state_inferred(prompt, anchor)

    return _render_prompt_image(prompt, anchor)

if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:]) or "infer the old hidden thing from build state"
    print(json.dumps(render_prompt_image(prompt), indent=2, ensure_ascii=False))

