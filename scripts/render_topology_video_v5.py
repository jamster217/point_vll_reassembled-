from pathlib import Path
import math, random

OUT = Path("var/topology_video_v5/frames")
OUT.mkdir(parents=True, exist_ok=True)

TOTAL = 420
random.seed(92162077)

GLYPHS = ["@S_145", "^M_01", "*C_FIRE", "[M]&lt;-&gt;[M]", "!L_SEAL"]
SHORT_LINES = [
    "Hold.",
    "Pressure enters.",
    "Mirror opens.",
    "Authority answers.",
    "The field remembers.",
    "Collapse.",
    "Not lost. Carried.",
    "Signal survives.",
]

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def pt(cx, cy, r, a):
    return cx + r * math.cos(a), cy + r * math.sin(a)

def line_for(mode, i):
    if i % 89 < 9:
        return SHORT_LINES[(i // 89) % len(SHORT_LINES)]
    if mode == "DECISION_LOCK":
        return "Decision locks. The scar remains."
    if mode == "AFTERSHOCK":
        return "The system absorbs what it chose."
    if mode == "HOTSPOT_CAUSAL":
        return "Hotspots ignite and bend the field."
    if mode == "AUTHORITY_DOMINANT":
        return "Authority tightens the living frame."
    if mode == "MIRROR_DOMINANT":
        return "The mirror returns the hidden shape."
    return "Dual state holds. Memory listens."

def make_svg(i):
    t = i / TOTAL
    cx, cy = 512, 512

    camera_x = 18 * math.sin(t * math.tau * 0.19)
    camera_y = 12 * math.cos(t * math.tau * 0.23)
    zoom = 1.0 + 0.035 * math.sin(t * math.tau * 0.13)

    pulse = 0.5 + 0.5 * math.sin(t * math.tau * 3)
    dominance = math.sin(t * math.tau * 0.64)

    collapse_wave = clamp((max(0, math.sin(t * math.tau * 5)) ** 22) * 1.5)

    # aftershock lingers after collapse peaks
    aftershock = clamp((max(0, math.sin((t - 0.018) * math.tau * 5)) ** 8) * 0.55)

    memory_bias = clamp(0.28 + 0.50 * (0.5 + 0.5 * math.sin(t * math.tau * 0.19)) + aftershock * 0.32)
    asymmetry = (memory_bias - 0.5) * 42 + aftershock * 28 * math.sin(t * math.tau * 9)

    hotspot_force = 0
    nodes = []
    for k in range(15):
        a = t * math.tau * (0.28 + k * 0.0035) + k * math.tau / 15
        nr = 265 + 38 * math.sin(t * math.tau * 1.9 + k * 0.73) + aftershock * 18
        x, y = pt(cx, cy, nr, a)
        intensity = ((math.sin(t * math.tau * 6.8 + k * 1.19) + 1) / 2) ** 12
        if intensity > 0.855:
            hotspot_force += intensity
        nodes.append((x, y, intensity))

    hotspot_force = clamp(hotspot_force / 2.8)
    collapse = clamp(collapse_wave + hotspot_force * 0.30)

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

    subtitle = line_for(mode, i)
    glyph = GLYPHS[(i // 54) % len(GLYPHS)]

    r_gold = 176 + 45 * pulse + dominance * 45 + memory_bias * 22 - collapse * 86 + asymmetry
    r_blue = 178 + 38 * (1 - pulse) - dominance * 45 - memory_bias * 10 - collapse * 76 - asymmetry * 0.55
    offset = 36 * dominance * (1 - collapse) + aftershock * 16

    gold_power = clamp(0.55 + dominance * 0.31 + collapse * 0.34 + aftershock * 0.12)
    blue_power = clamp(0.55 - dominance * 0.31 + collapse * 0.24 + aftershock * 0.18)

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
    for j, alpha in [(1, .18), (2, .12), (3, .075), (4, .045), (5, .025)]:
        tt = max(0, (i - j * 14) / TOTAL)
        old_dom = math.sin(tt * math.tau * 0.64)
        old_pulse = 0.5 + 0.5 * math.sin(tt * math.tau * 3)
        old_r = 176 + 45 * old_pulse + old_dom * 45 + memory_bias * 12
        trails.append(f'<circle cx="{cx + old_dom*24:.1f}" cy="{cy}" r="{old_r:.1f}" fill="none" stroke="#ffffff" stroke-opacity="{alpha}" stroke-width="1.2" filter="url(#softGlow)"/>')

    scars = []
    for s in range(7):
        y = 668 + s * 22
        shift = 42 * math.sin(t * math.tau * 0.31 + s) + aftershock * 38
        scars.append(f'<path d="M {205+s*20} {y} C {360+shift:.1f} {y-48}, {630-shift:.1f} {y+46}, {830-s*12} {y-8}" fill="none" stroke="#d7b15f" stroke-opacity="{0.055 + memory_bias*0.095:.3f}" stroke-width="{1.4+aftershock*2:.1f}"/>')

    node_lines, node_svg = [], []
    for idx, (x, y, inten) in enumerate(nodes):
        causal = inten > 0.855
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
<circle cx="512" cy="512" r="{105+collapse*190+aftershock*70:.1f}" fill="none" stroke="#ffffff" stroke-opacity="{0.40*collapse + 0.18*aftershock:.3f}" stroke-width="{6*collapse+3*aftershock:.1f}" filter="url(#hardGlow)"/>
<circle cx="512" cy="512" r="{42+collapse*64+aftershock*24:.1f}" fill="#ffffff" fill-opacity="{0.045+collapse*.25+aftershock*.10:.3f}" filter="url(#hardGlow)"/>
'''

    # whole-scene transform: slow drift/zoom camera
    transform = f'translate({camera_x:.1f} {camera_y:.1f}) scale({zoom:.4f}) translate({-camera_x:.1f} {-camera_y:.1f})'

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
<text x="300" y="542" fill="#8ee6ff" font-family="monospace" font-size="18">PRESENCE / AFTERSHOCK / MEMORY CONSEQUENCE</text>

{''.join(node_svg)}
</g>

<text x="34" y="58" fill="#8ee6ff" font-family="monospace" font-size="27">POINT_VLL_TOPOLOGY_RENDER_V5</text>
<text x="34" y="94" fill="#d7b15f" font-family="monospace" font-size="18">DEPTH {i:03d} / {mode}</text>
<text x="34" y="123" fill="#ffffff" opacity="0.54" font-family="monospace" font-size="15">memory={memory_bias:.2f} hotspot={hotspot_force:.2f} collapse={collapse:.2f} aftershock={aftershock:.2f}</text>

<rect x="110" y="842" width="804" height="58" rx="16" fill="#000000" fill-opacity="0.45" stroke="#8ee6ff" stroke-opacity="0.20"/>
<text x="140" y="878" fill="#ffffff" font-family="monospace" font-size="24">{subtitle}</text>

<text x="336" y="956" fill="#8ee6ff" font-family="monospace" font-size="20">API_LATITUDE_LOCK: PORTLAND</text>
</svg>'''

for i in range(TOTAL):
    (OUT / f"frame_{i:04d}.svg").write_text(make_svg(i), encoding="utf-8")

print("SVG frames:", TOTAL)
print("Output:", OUT)
