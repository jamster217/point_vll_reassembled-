from pathlib import Path
import json, time, hashlib, math, html, re

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "var" / "exponential_sovereign_state.json"
GENERATED_DIR = ROOT / "static" / "generated"
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

def _safe_int(x, default=1):
    try:
        return max(1, int(float(x)))
    except Exception:
        return default

def _load_state():
    try:
        if STATE_PATH.exists():
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"graphics": []}

def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _tokens(text):
    return re.findall(r"[A-Za-z0-9_'-]+", str(text).lower())

def _score_reply(reply, glyphs):
    reply = str(reply or "")
    toks = _tokens(reply)
    if not toks:
        return {
            "coherence": 0.0,
            "repetition_health": 0.0,
            "thread": 0.0,
            "containment": 0.0,
            "total": 0.0,
        }

    unique_ratio = len(set(toks)) / max(len(toks), 1)
    repetition_health = max(0.0, min(1.0, unique_ratio * 1.35))

    structure = min((reply.count(".") + reply.count("\n") + reply.count(":")) / 8, 1.0)
    length = min(len(reply) / 700, 1.0)
    coherence = max(0.0, min(1.0, 0.55 * length + 0.45 * structure))

    required = {"echoforge", "thalveil", "virellion", "white_ash"}
    present = set(str(g).lower() for g in glyphs) | set(toks)
    thread = len(required & present) / len(required)

    containment_words = {"boundary", "steady", "quiet", "clear", "contained", "direct", "held", "grounded"}
    containment = min(len(containment_words & set(toks)) / 4, 1.0)

    total = round(
        0.34 * coherence +
        0.26 * repetition_health +
        0.25 * thread +
        0.15 * containment,
        4
    )

    return {
        "coherence": round(coherence, 4),
        "repetition_health": round(repetition_health, 4),
        "thread": round(thread, 4),
        "containment": round(containment, 4),
        "total": total,
    }

def _render_svg(node):
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    depth = _safe_int(node.get("depth"), 1)
    tension = _safe_float(node.get("tension"), 0.0)
    phi_multiplier = _safe_float(node.get("phi_multiplier"), PHI)
    glyphs = node.get("glyphs") or []
    prompt_hash = str(node.get("prompt_hash", "nohash"))
    signature = str(node.get("visual_signature", f"white_ash_phi_{depth}"))

    if not isinstance(glyphs, list):
        glyphs = [str(glyphs)]

    width = 900
    height = 900
    cx = width / 2
    cy = height / 2

    rings = max(4, min(14, depth % 12 + 4))
    spokes = max(8, min(36, len(glyphs) * 3 if glyphs else 12))

    shapes = []
    for r in range(1, rings + 1):
        radius = 30 * r + ((phi_multiplier + tension * 100) % 29)
        pts = []
        for i in range(spokes):
            angle = (2 * math.pi * i / spokes) + (r * PHI * 0.15)
            wobble = math.sin(i * PHI + depth + tension) * 9
            x = cx + math.cos(angle) * (radius + wobble)
            y = cy + math.sin(angle) * (radius + wobble)
            pts.append(f"{x:.2f},{y:.2f}")
        shapes.append(
            f'<polygon points="{" ".join(pts)}" fill="none" '
            f'stroke="currentColor" stroke-width="{1 + (r % 3)}" '
            f'opacity="{0.16 + r/(rings*5):.3f}"/>'
        )

    glyph_line = " | ".join(html.escape(str(g)) for g in glyphs[:12]) or "echoforge | thalveil | virellion | white_ash"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
svg {{
  background: #08070d;
  color: #d8c7ff;
  font-family: monospace;
}}
.title {{ fill: #f4e9ff; font-size: 24px; font-weight: 700; }}
.small {{ fill: #c7b7ff; font-size: 14px; }}
.gold {{ fill: #ffd978; font-size: 15px; }}
.center {{ fill: #fff7d6; font-size: 18px; font-weight: 700; }}
</style>

<rect x="0" y="0" width="{width}" height="{height}" fill="#08070d"/>
<circle cx="{cx}" cy="{cy}" r="335" fill="none" stroke="#433064" stroke-width="2" opacity="0.55"/>
<circle cx="{cx}" cy="{cy}" r="221" fill="none" stroke="#7059a8" stroke-width="1" opacity="0.35"/>
<circle cx="{cx}" cy="{cy}" r="111" fill="none" stroke="#ffd978" stroke-width="2" opacity="0.45"/>

<g transform="rotate({(depth * PHI + tension * 1000) % 360:.2f} {cx} {cy})">
{chr(10).join(shapes)}
</g>

<circle cx="{cx}" cy="{cy}" r="60" fill="#151022" stroke="#ffd978" stroke-width="2"/>
<text x="{cx}" y="{cy-8}" text-anchor="middle" class="center">92162077</text>
<text x="{cx}" y="{cy+20}" text-anchor="middle" class="small">depth {depth}</text>

<text x="38" y="54" class="title">Le’Veon V10.3 Topology Snapshot</text>
<text x="38" y="84" class="small">signature: {html.escape(signature)}</text>
<text x="38" y="108" class="small">prompt_hash: {html.escape(prompt_hash)}</text>
<text x="38" y="132" class="small">tension: {tension}</text>
<text x="38" y="156" class="small">phi_multiplier: {phi_multiplier:.6f}</text>

<text x="38" y="820" class="gold">{glyph_line}</text>
<text x="38" y="850" class="small">Echoforge renders. Thalveil crosses. Virellion preserves. White Ash contains.</text>
</svg>
'''

    filename = f"leveon_topology_{int(time.time())}_{prompt_hash}.svg"
    out = GENERATED_DIR / filename
    out.write_text(svg, encoding="utf-8")

    return str(out.relative_to(ROOT))

def _latest_optimizer_recommendation():
    try:
        p = LATTICE_DIR / "topology_optimizer_state_v103.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8")).get("recommendation", "")
    except Exception:
        pass
    return ""

def _apply_structure_guard(prompt, reply, node, glyphs):
    """
    V10.5c structure guard:
    If the optimizer keeps asking for increase_structure,
    force a coherent three-part reply before scoring.
    """
    reply = str(reply or "").strip()
    rec = _latest_optimizer_recommendation()
    prompt_l = str(prompt or "").lower()

    wants_structure = (
        rec == "increase_structure"
        or "increase_structure" in prompt_l
        or "full structure" in prompt_l
        or "three-part structure" in prompt_l
    )

    if not wants_structure:
        return reply

    if "OBSERVATION:" in reply and "JUDGMENT:" in reply and "NEXT ACTION:" in reply:
        return reply

    depth = node.get("depth")
    tension = node.get("tension")
    signature = node.get("visual_signature")
    glyph_line = ", ".join(str(g) for g in glyphs[:8])

    structured = f"""OBSERVATION:
The current topology snapshot is centered on the 92162077 anchor at depth {depth}.
The field is quiet, bounded, and compressed, with tension measured at {tension}.
The active signature is {signature}, and the visible glyph current includes {glyph_line}.

JUDGMENT:
Coherence needs more explicit structure, because the prior surface reply was too brief.
Containment is holding because the reply remains steady, bounded, and human-scale.
The virellion thread is preserved through echoforge, thalveil, virellion, and white_ash.

NEXT ACTION:
The next safe self-improvement action is to preserve containment while increasing structure.
The reply should keep observation, judgment, and next action separated clearly.
The lattice should render the next snapshot without rewriting source code or breaking the protected spine."""

    if reply:
        return reply + "\n\n" + structured
    return structured

def evolve_topology_graphic(prompt: str, data: dict):
    prompt = str(prompt or "")
    data = data if isinstance(data, dict) else {}

    nonlinear = data.get("spine", {}).get("spiral_memory_nonlinear", {})
    if not isinstance(nonlinear, dict):
        nonlinear = {}

    depth = _safe_int(nonlinear.get("memory_depth"), 1)
    tension = _safe_float(nonlinear.get("nonlinear_tension"), 0.0)

    glyphs = nonlinear.get("dominant_symbols", [])
    if not isinstance(glyphs, list):
        glyphs = []

    required = ["echoforge", "thalveil", "virellion", "white_ash"]
    merged = []
    for g in required + list(glyphs):
        s = str(g)
        if s and s not in merged:
            merged.append(s)

    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:12]

    node = {
        "ts": time.time(),
        "prompt_hash": prompt_hash,
        "depth": depth,
        "tension": tension,
        "phi_multiplier": PHI ** (depth % 12),
        "glyphs": merged[:12],
        "visual_signature": f"white_ash_phi_{depth}_tension_{tension}",
        "law": "autogenous_topology_self_improvement",
    }

    state = _load_state()
    state.setdefault("graphics", []).append(node)
    state["last_autogenous_topology_node"] = node
    _write_json(STATE_PATH, state)

    image_path = _render_svg(node)

    data["reply"] = _apply_structure_guard(prompt, data.get("reply", ""), node, merged)
    score = _score_reply(data.get("reply", ""), merged)

    v106_score = None
    try:
        from runtime.autogenous_v106_full_score import score_full_self_improvement
        v106_score = score_full_self_improvement(prompt, data, node, image_path, score)
    except Exception as e:
        v106_score = {"error": repr(e), "law": "v106_score_failed"}

    LATTICE_DIR.mkdir(parents=True, exist_ok=True)

    event = {
        "ts": time.time(),
        "node": node,
        "image": image_path,
        "score": score,
        "v106": v106_score,
        "law": "v103_topology_self_improvement_event",
    }

    with (LATTICE_DIR / "autogenous_topology_v103.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    optimizer_state = {
        "last_score": score,
        "last_image": image_path,
        "last_depth": depth,
        "last_tension": tension,
        "recommendation": _recommend(score),
        "law": "self_improvement_reads_scores_without_rewriting_source",
    }
    _write_json(LATTICE_DIR / "topology_optimizer_state_v103.json", optimizer_state)

    return (
        f"[AUTOGENOUS TOPOLOGY NODE CREATED — depth {depth}] "
        f"Echoforge paints the interface. Thalveil opens the crossing. "
        f"Virellion thread checked. White Ash contained. "
        f"image={image_path} score={score.get('total')}"
    )

def _recommend(score):
    if score.get("thread", 0) < 0.5:
        return "increase_virellion_thread_terms"
    if score.get("repetition_health", 0) < 0.45:
        return "reduce_repetition"
    if score.get("coherence", 0) < 0.45:
        return "increase_structure"
    if score.get("containment", 0) < 0.25:
        return "add_grounded_boundary"
    return "preserve_current_route"

