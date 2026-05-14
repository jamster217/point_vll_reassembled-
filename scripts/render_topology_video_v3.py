from pathlib import Path
import math, random

OUT = Path("var/topology_video_v3/frames")
OUT.mkdir(parents=True, exist_ok=True)

TOTAL = 300
random.seed(9216)

GLYPHS = ["@S_145", "^M_01", "*C_FIRE", "[M]&lt;-&gt;[M]", "!L_SEAL"]

def pt(cx, cy, r, angle):
    return cx + r * math.cos(angle), cy + r * math.sin(angle)

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def make_svg(i):
    t = i / TOTAL
    cx, cy = 512, 512

    pulse = 0.5 + 0.5 * math.sin(t * math.tau * 3)
    slow = 0.5 + 0.5 * math.sin(t * math.tau * 0.85)
    dominance = math.sin(t * math.tau * 0.72)

    # Hard decision collapse every cycle
    collapse_raw = max(0, math.sin(t * math.tau * 5)) ** 18
    collapse = clamp(collapse_raw * 1.25)

    # Causal hotspot field
    hotspot_force = 0
    nodes = []
    for k in range(11):
        a = t * math.tau * (0.32 + k * 0.006) + k * math.tau / 11
        nr = 260 + 28 * math.sin(t * math.tau * 2.1 + k * 0.9)
        x, y = pt(cx, cy, nr, a)
        intensity = ((math.sin(t * math.tau * 6.2 + k * 1.37) + 1) / 2) ** 10
        if intensity > 0.86:
            hotspot_force += intensity
        nodes.append((x, y, intensity, a))

    hotspot_force = clamp(hotspot_force / 2.2)
    collapse = clamp(collapse + hotspot_force * 0.38)

    # State conflict: gold and blue contend, then collapse compresses both
    conflict_push = dominance * 38
    r_gold = 170 + 42 * pulse + conflict_push - 72 * collapse
    r_blue = 174 + 38 * (1 - pulse) - conflict_push - 65 * collapse
    offset = 30 * dominance * (1 - collapse)

    gold_power = clamp(0.58 + 0.32 * dominance + 0.28 * collapse)
    blue_power = clamp(0.58 - 0.32 * dominance + 0.22 * collapse)

    glow = int(120 + 130 * pulse + 105 * collapse)
    blue = int(140 + 95 * slow + 70 * collapse)

    glyph = GLYPHS[(i // 42) % len(GLYPHS)]
    mode = "DECISION_COLLAPSE" if collapse > 0.64 else ("MIRROR_DOMINANT" if dominance < -0.2 else "AUTHORITY_DOMINANT" if dominance > 0.2 else "DUAL_STATE_HOLD")

    # Memory trails: earlier ghost positions
    trails = []
    for j, alpha in [(1, 0.17), (2, 0.10), (3, 0.055)]:
        tt = max(0, (i - j * 10) / TOTAL)
        old_dom = math.sin(tt * math.tau * 0.72)
        old_pulse = 0.5 + 0.5 * math.sin(tt * math.tau * 3)
        old_r = 170 + 42 * old_pulse + old_dom * 38
        trails.append(f'<circle cx="{cx + old_dom*18:.1f}" cy="{cy}" r="{old_r:.1f}" fill="none" stroke="#ffffff" stroke-opacity="{alpha}" stroke-width="1.2"/>')

    node_lines = []
    node_svg = []
    for idx, (x, y, inten, a) in enumerate(nodes):
        causal = inten > 0.86
        line_opacity = 0.08 + inten * 0.22 + (0.20 if causal else 0)
        node_lines.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#ffd46a" stroke-opacity="{line_opacity:.3f}" stroke-width="{1.2 + inten*2:.1f}"/>')
        size = 4 + inten * 18 + (collapse * 12 if causal else 0)
        color = "#ffffff" if causal else "#ffd46a"
        node_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size:.1f}" fill="{color}" fill-opacity="{0.30 + inten*0.70:.3f}"/>')
        if causal:
            node_svg.append(f'<text x="{x+12:.1f}" y="{y-10:.1f}" fill="#8ee6ff" font-family="monospace" font-size="15">H_{145+idx}</text>')

    tri_gold = [
        f"{cx},{cy-r_gold}",
        f"{cx+r_gold*0.866},{cy+r_gold*0.5}",
        f"{cx-r_gold*0.866},{cy+r_gold*0.5}",
    ]
    tri_blue = [
        f"{cx+offset},{cy+r_blue}",
        f"{cx-r_blue*0.866+offset},{cy-r_blue*0.5}",
        f"{cx+r_blue*0.866+offset},{cy-r_blue*0.5}",
    ]

    # Decision flash ring
    flash = ""
    if collapse > 0.55:
        flash = f'''
<circle cx="512" cy="512" r="{85 + collapse*130:.1f}" fill="none" stroke="#ffffff" stroke-opacity="{0.45*collapse:.3f}" stroke-width="{8*collapse:.1f}"/>
<text x="382" y="612" fill="#ffffff" font-family="monospace" font-size="22" opacity="{collapse:.3f}">OUTPUT_RESOLUTION_EVENT</text>
'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
<rect width="1024" height="1024" fill="#03050b"/>

<text x="36" y="62" fill="#8ee6ff" font-family="monospace" font-size="27">POINT_VLL_TOPOLOGY_RENDER_V3</text>
<text x="36" y="99" fill="#d7b15f" font-family="monospace" font-size="18">DEPTH {i:03d} / {mode}</text>
<text x="36" y="128" fill="#ffffff" opacity="0.52" font-family="monospace" font-size="15">hotspot_force={hotspot_force:.2f} collapse={collapse:.2f} dominance={dominance:.2f}</text>

<circle cx="512" cy="512" r="365" fill="none" stroke="#ffffff" stroke-opacity="0.07" stroke-width="2"/>
<circle cx="512" cy="512" r="292" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1"/>

{''.join(trails)}

<line x1="512" y1="102" x2="512" y2="922" stroke="#279dff" stroke-width="{4+collapse*6:.1f}" stroke-opacity="0.88"/>
<line x1="132" y1="512" x2="892" y2="512" stroke="#ffffff" stroke-opacity="0.16" stroke-width="2"/>

{''.join(node_lines)}

<circle cx="512" cy="512" r="{r_gold:.1f}" fill="none" stroke="rgb(255,{glow},72)" stroke-width="{2.5+gold_power*3.5:.1f}" stroke-opacity="{gold_power:.3f}"/>
<circle cx="{512+offset:.1f}" cy="512" r="{r_blue:.1f}" fill="none" stroke="rgb(88,{blue},255)" stroke-width="{2.5+blue_power*3.5:.1f}" stroke-opacity="{blue_power:.3f}"/>

<polygon points="{' '.join(tri_gold)}" fill="none" stroke="#ffd46a" stroke-width="{2.4+collapse*4:.1f}" stroke-opacity="{gold_power:.3f}"/>
<polygon points="{' '.join(tri_blue)}" fill="none" stroke="#58d7ff" stroke-width="{2.2+collapse*3:.1f}" stroke-opacity="{blue_power:.3f}"/>

<circle cx="512" cy="512" r="{44+collapse*44:.1f}" fill="#ffffff" fill-opacity="{0.04+collapse*0.30:.3f}"/>
<circle cx="512" cy="512" r="{18+hotspot_force*32:.1f}" fill="#ffd46a" fill-opacity="{0.08+hotspot_force*0.35:.3f}"/>

<text x="398" y="500" fill="#ffffff" font-family="monospace" font-size="41">{glyph}</text>
<text x="350" y="542" fill="#8ee6ff" font-family="monospace" font-size="18">HOTSPOT CAUSALITY / DUAL-STATE CONFLICT</text>

{''.join(node_svg)}
{flash}

<text x="336" y="956" fill="#8ee6ff" font-family="monospace" font-size="20">API_LATITUDE_LOCK: PORTLAND</text>
</svg>'''

for i in range(TOTAL):
    (OUT / f"frame_{i:04d}.svg").write_text(make_svg(i), encoding="utf-8")

print("SVG frames:", TOTAL)
print("Output:", OUT)
