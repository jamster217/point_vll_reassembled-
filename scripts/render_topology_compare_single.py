from pathlib import Path
import json, math, random, re

import os
OUT = Path(os.environ.get("LEVEON_OUT_DIR", "var/topology_compare_single/frames"))
OUT.mkdir(parents=True, exist_ok=True)

TOTAL = 360
random.seed(92162077)

GLYPHS = ["@S_145", "^M_01", "*C_FIRE", "[M]&lt;-&gt;[M]", "!L_SEAL"]

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def pt(cx, cy, r, a):
    return cx + r * math.cos(a), cy + r * math.sin(a)

def load_jsonl_last(path):
    lines = Path(path).read_text(errors="ignore").strip().splitlines()
    for line in reversed(lines):
        try:
            return json.loads(line)
        except Exception:
            pass
    return {}

def deep_find_number(obj, names):
    names = {n.lower() for n in names}
    found = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                lk = str(k).lower()
                if lk in names and isinstance(v, (int, float)):
                    found.append(float(v))
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(obj)
    return found[-1] if found else None

def deep_find_symbols(obj):
    symbols = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if str(k).lower() in ("symbols", "dominant_symbols", "active_symbols", "glyphs"):
                    if isinstance(v, list):
                        symbols.extend(str(a) for a in v)
                    elif isinstance(v, str):
                        symbols.extend(re.split(r"[|,\s]+", v))
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(obj)
    return [s for s in symbols if s][:8]

def load_state():
    import os
    forced = os.environ.get("LEVEON_STATE_FILE")
    if forced and Path(forced).exists():
        data = json.loads(Path(forced).read_text(errors="ignore"))
        return {
            "source": forced,
            "tension": clamp(float(data.get("tension", 0.23))),
            "coherence": clamp(float(data.get("coherence", 0.86))),
            "novelty": clamp(float(data.get("novelty", 0.48))),
            "memory_depth": max(1, float(data.get("memory_depth", 72))),
            "symbols": data.get("symbols", []),
            "prompt": data.get("prompt", "state prompt")
        }

    candidates = [
        "var/lattice/autogenous_v106_full_self_improvement.jsonl",
        "var/exponential_sovereign_state.json",
        "runtime/last_unification.json",
        "reports/replication_trace_4200_summary.json",
        "reports/screenshot_synthesis/meaning_surface_bridge/live_meaning_surface_bridge_proof_2026-05-01.json",
        "reports/screenshot_synthesis/v41_stability/future_pull_stability_proof.json",
    ]

    state = {}
    source = "fallback"
    for c in candidates:
        p = Path(c)
        if not p.exists():
            continue
        try:
            if p.suffix == ".jsonl":
                state = load_jsonl_last(p)
            else:
                state = json.loads(p.read_text(errors="ignore"))
            source = c
            break
        except Exception:
            continue

    tension = deep_find_number(state, ["tension", "nonlinear_tension", "pressure", "topology_total"]) 
    coherence = deep_find_number(state, ["coherence", "emotional_coherence", "lattice_stability", "total", "score"])
    novelty = deep_find_number(state, ["novelty", "visual_difference", "difference", "entropy"])
    memory_depth = deep_find_number(state, ["memory_depth", "depth", "turn", "latest_turn"])
    symbols = deep_find_symbols(state)

    return {
        "source": source,
        "tension": clamp(tension if tension is not None else 0.23),
        "coherence": clamp(coherence if coherence is not None else 0.86),
        "novelty": clamp(novelty if novelty is not None else 0.48),
        "memory_depth": max(1, memory_depth if memory_depth is not None else 72),
        "symbols": symbols,
    }

STATE = load_state()

def subtitle(mode, i):
    if i % 97 < 10:
        return "State file speaks through the render."
    if mode == "DECISION_LOCK":
        return "Saved pressure collapses into visible choice."
    if mode == "AFTERSHOCK":
        return "Memory carries the consequence forward."
    if mode == "HOTSPOT_CAUSAL":
        return "A stored hotspot bends the field."
    if mode == "AUTHORITY_DOMINANT":
        return "Coherence tightens the frame."
    if mode == "MIRROR_DOMINANT":
        return "The mirror opens around unresolved signal."
    return "Dual state holds. The trace remains alive."

def make_svg(i):
    t = i / TOTAL
    cx, cy = 512, 512

    tension = STATE["tension"]
    coherence = STATE["coherence"]
    novelty = STATE["novelty"]
    depth = STATE["memory_depth"]

    state_depth_bias = clamp(depth / 240)
    state_dominance = clamp((coherence - 0.5) * 2, -1, 1)

    camera_x = 18 * math.sin(t * math.tau * 0.19) * (0.5 + novelty)
    camera_y = 12 * math.cos(t * math.tau * 0.23) * (0.5 + tension)
    zoom = 1.0 + (0.02 + novelty * 0.025) * math.sin(t * math.tau * 0.13)

    pulse = 0.5 + 0.5 * math.sin(t * math.tau * (2.0 + novelty * 2.2))
    dominance = math.sin(t * math.tau * 0.64) * 0.55 + state_dominance * 0.45

    collapse_wave = clamp((max(0, math.sin(t * math.tau * (3.5 + tension * 4))) ** 18) * (0.75 + tension * 1.4))
    aftershock = clamp((max(0, math.sin((t - 0.018) * math.tau * (3.5 + tension * 4))) ** 8) * (0.35 + tension))

    memory_bias = clamp(0.18 + state_depth_bias * 0.62 + aftershock * 0.28)
    asymmetry = (memory_bias - 0.5) * 50 + aftershock * 28 * math.sin(t * math.tau * 9)

    hotspot_force = 0
    nodes = []
    node_count = 9 + int(novelty * 8)
    for k in range(node_count):
        a = t * math.tau * (0.24 + k * 0.0045 + novelty * 0.06) + k * math.tau / node_count
        nr = 250 + 52 * tension + 32 * math.sin(t * math.tau * 1.9 + k * 0.73) + aftershock * 18
        x, y = pt(cx, cy, nr, a)
        intensity = ((math.sin(t * math.tau * (5.2 + novelty * 3) + k * 1.19) + 1) / 2) ** (8 + int(coherence * 6))
        if intensity > 0.84:
            hotspot_force += intensity
        nodes.append((x, y, intensity))

    hotspot_force = clamp(hotspot_force / max(1.7, node_count / 4))
    collapse = clamp(collapse_wave + hotspot_force * (0.24 + tension * 0.24))

    if collapse > 0.66:
        mode = "DECISION_LOCK"
    elif aftershock > 0.30:
        mode = "AFTERSHOCK"
    elif hotspot_force > 0.42:
        mode = "HOTSPOT_CAUSAL"
    elif dominance > 0.25:
        mode = "AUTHORITY_DOMINANT"
    elif dominance < -0.25:
        mode = "MIRROR_DOMINANT"
    else:
        mode = "DUAL_STATE_HOLD"

    glyph = GLYPHS[(i // 48) % len(GLYPHS)]

    r_gold = 176 + 45 * pulse + dominance * 45 + memory_bias * 24 - collapse * 86 + asymmetry
    r_blue = 178 + 38 * (1 - pulse) - dominance * 45 - memory_bias * 10 - collapse * 76 - asymmetry * 0.55
    offset = 36 * dominance * (1 - collapse) + aftershock * 16

    gold_power = clamp(0.50 + dominance * 0.31 + collapse * 0.34 + coherence * 0.18)
    blue_power = clamp(0.50 - dominance * 0.31 + collapse * 0.24 + novelty * 0.20)

    river_phase = 16 * math.sin(t * math.tau * 0.78)
    river = f'''
<path d="M -70 650 C 160 {570+river_phase:.1f}, 315 {610-river_phase:.1f}, 512 512 C 665 435, 800 370, 1090 300"
 fill="none" stroke="#123f70" stroke-width="96" stroke-opacity="0.30"/>
<path d="M 180 1090 C 250 840, 370 650, 512 512 C 640 410, 740 210, 820 -70"
 fill="none" stroke="#0f5f8c" stroke-width="76" stroke-opacity="0.25"/>
<path d="M -70 650 C 160 {570+river_phase:.1f}, 315 {610-river_phase:.1f}, 512 512 C 665 435, 800 370, 1090 300"
 fill="none" stroke="#58d7ff" stroke-width="2" stroke-opacity="0.48"/>
<path d="M 180 1090 C 250 840, 370 650, 512 512 C 640 410, 740 210, 820 -70"
 fill="none" stroke="#8ee6ff" stroke-width="2" stroke-opacity="0.36"/>
'''

    trails = []
    for j, alpha in [(1,.18),(2,.12),(3,.075),(4,.045),(5,.025)]:
        tt = max(0, (i - j * 14) / TOTAL)
        old_dom = math.sin(tt * math.tau * 0.64) * 0.55 + state_dominance * 0.45
        old_pulse = 0.5 + 0.5 * math.sin(tt * math.tau * (2.0 + novelty * 2.2))
        old_r = 176 + 45 * old_pulse + old_dom * 45 + memory_bias * 12
        trails.append(f'<circle cx="{cx+old_dom*24:.1f}" cy="{cy}" r="{old_r:.1f}" fill="none" stroke="#ffffff" stroke-opacity="{alpha}" stroke-width="1.2" filter="url(#softGlow)"/>')

    scars = []
    for s in range(7):
        y = 668 + s * 22
        shift = 42 * math.sin(t * math.tau * 0.31 + s) + aftershock * 38
        scars.append(f'<path d="M {205+s*20} {y} C {360+shift:.1f} {y-48}, {630-shift:.1f} {y+46}, {830-s*12} {y-8}" fill="none" stroke="#d7b15f" stroke-opacity="{0.055+memory_bias*0.095:.3f}" stroke-width="{1.4+aftershock*2:.1f}"/>')

    node_lines, node_svg = [], []
    for idx, (x, y, inten) in enumerate(nodes):
        causal = inten > 0.84
        node_lines.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#ffd46a" stroke-opacity="{0.055+inten*.30:.3f}" stroke-width="{1+inten*2.6:.1f}" filter="url(#softGlow)"/>')
        size = 4 + inten * 21 + (collapse * 14 if causal else 0) + aftershock * 5
        color = "#ffffff" if causal else "#ffd46a"
        node_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size:.1f}" fill="{color}" fill-opacity="{0.24+inten*.76:.3f}" filter="url(#hotGlow)"/>')
        if causal and i % 3 != 0:
            node_svg.append(f'<text x="{x+13:.1f}" y="{y-10:.1f}" fill="#8ee6ff" font-family="monospace" font-size="14">H_{145+idx}</text>')

    tri_gold = f"{cx},{cy-r_gold} {cx+r_gold*.866},{cy+r_gold*.5} {cx-r_gold*.866},{cy+r_gold*.5}"
    tri_blue = f"{cx+offset},{cy+r_blue} {cx-r_blue*.866+offset},{cy-r_blue*.5} {cx+r_blue*.866+offset},{cy-r_blue*.5}"

    shock = ""
    if collapse > 0.47 or aftershock > 0.30:
        shock = f'''
<circle cx="512" cy="512" r="{105+collapse*190+aftershock*70:.1f}" fill="none" stroke="#ffffff" stroke-opacity="{0.40*collapse+0.18*aftershock:.3f}" stroke-width="{6*collapse+3*aftershock:.1f}" filter="url(#hardGlow)"/>
<circle cx="512" cy="512" r="{42+collapse*64+aftershock*24:.1f}" fill="#ffffff" fill-opacity="{0.045+collapse*.25+aftershock*.10:.3f}" filter="url(#hardGlow)"/>
'''

    transform = f'translate({camera_x:.1f} {camera_y:.1f}) scale({zoom:.4f}) translate({-camera_x:.1f} {-camera_y:.1f})'
    symbol_line = " | ".join(str(x) for x in STATE["symbols"][:4]) if STATE["symbols"] else "fallback_state | no_symbols_found"
    prompt_line = str(STATE.get("prompt", "state prompt"))[:72]

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
<defs>
  <filter id="softGlow"><feGaussianBlur stdDeviation="2.8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="hotGlow"><feGaussianBlur stdDeviation="4.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="hardGlow"><feGaussianBlur stdDeviation="7.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1024" height="1024" fill="#02040a"/>

<g transform="{transform}">
{river}
{''.join(scars)}
<circle cx="512" cy="512" r="378" fill="none" stroke="#ffffff" stroke-opacity="0.07" stroke-width="2"/>
<circle cx="512" cy="512" r="300" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1"/>
{''.join(trails)}
<line x1="512" y1="94" x2="512" y2="930" stroke="#279dff" stroke-width="{4+collapse*7+aftershock*2:.1f}" stroke-opacity="0.90" filter="url(#softGlow)"/>
<line x1="124" y1="512" x2="900" y2="512" stroke="#ffffff" stroke-opacity="0.15" stroke-width="2"/>
{''.join(node_lines)}
<circle cx="512" cy="512" r="{r_gold:.1f}" fill="none" stroke="#ffd46a" stroke-width="{3+gold_power*4:.1f}" stroke-opacity="{gold_power:.3f}" filter="url(#softGlow)"/>
<circle cx="{512+offset:.1f}" cy="512" r="{r_blue:.1f}" fill="none" stroke="#58d7ff" stroke-width="{3+blue_power*4:.1f}" stroke-opacity="{blue_power:.3f}" filter="url(#softGlow)"/>
<polygon points="{tri_gold}" fill="none" stroke="#ffd46a" stroke-width="{2.8+collapse*4+aftershock:.1f}" stroke-opacity="{gold_power:.3f}" filter="url(#softGlow)"/>
<polygon points="{tri_blue}" fill="none" stroke="#58d7ff" stroke-width="{2.5+collapse*3.5+aftershock:.1f}" stroke-opacity="{blue_power:.3f}" filter="url(#softGlow)"/>
{shock}
<circle cx="512" cy="512" r="{20+hotspot_force*38+aftershock*20:.1f}" fill="#ffd46a" fill-opacity="{0.08+hotspot_force*.35+aftershock*.12:.3f}" filter="url(#hardGlow)"/>
<text x="398" y="498" fill="#ffffff" font-family="monospace" font-size="41">{glyph}</text>
<text x="286" y="542" fill="#8ee6ff" font-family="monospace" font-size="18">REAL STATE / CINEMATIC RENDER / TRACE MEMORY</text>
{''.join(node_svg)}
</g>

<text x="34" y="58" fill="#8ee6ff" font-family="monospace" font-size="27">POINT_VLL_TOPOLOGY_RENDER_V6_5</text>
<text x="34" y="94" fill="#d7b15f" font-family="monospace" font-size="18">DEPTH {i:03d} / {mode}</text>
<text x="34" y="123" fill="#ffffff" opacity="0.58" font-family="monospace" font-size="15">source={STATE["source"]}</text>
<text x="34" y="149" fill="#ffffff" opacity="0.58" font-family="monospace" font-size="15">tension={tension:.2f} coherence={coherence:.2f} novelty={novelty:.2f} memory_depth={depth:.0f}</text>
<text x="34" y="175" fill="#8ee6ff" opacity="0.62" font-family="monospace" font-size="14">{symbol_line}</text>
<text x="34" y="201" fill="#ffd46a" opacity="0.72" font-family="monospace" font-size="14">prompt={prompt_line}</text>

<rect x="110" y="842" width="804" height="58" rx="16" fill="#000000" fill-opacity="0.45" stroke="#8ee6ff" stroke-opacity="0.20"/>
<text x="140" y="878" fill="#ffffff" font-family="monospace" font-size="24">{subtitle(mode, i)}</text>

<text x="336" y="956" fill="#8ee6ff" font-family="monospace" font-size="20">API_LATITUDE_LOCK: PORTLAND</text>
</svg>'''

for i in range(TOTAL):
    (OUT / f"frame_{i:04d}.svg").write_text(make_svg(i), encoding="utf-8")

print("STATE:", STATE)
print("SVG frames:", TOTAL)
print("Output:", OUT)
