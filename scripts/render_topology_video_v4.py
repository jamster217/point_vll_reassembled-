from pathlib import Path
import math, random

OUT = Path("var/topology_video_v4/frames")
OUT.mkdir(parents=True, exist_ok=True)

TOTAL = 360
random.seed(2077)

GLYPHS = ["@S_145", "^M_01", "*C_FIRE", "[M]&lt;-&gt;[M]", "!L_SEAL"]

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def pt(cx, cy, r, a):
    return cx + r * math.cos(a), cy + r * math.sin(a)

def make_svg(i):
    t = i / TOTAL
    cx, cy = 512, 512

    pulse = 0.5 + 0.5 * math.sin(t * math.tau * 3)
    dominance = math.sin(t * math.tau * 0.68)
    collapse = clamp((max(0, math.sin(t * math.tau * 5)) ** 20) * 1.35)

    memory_bias = clamp(0.25 + 0.55 * (0.5 + 0.5 * math.sin(t * math.tau * 0.22)))
    scar_shift = 34 * memory_bias * math.sin(t * math.tau * 0.31)

    hotspot_force = 0
    nodes = []
    for k in range(13):
        a = t * math.tau * (0.30 + k * 0.004) + k * math.tau / 13
        nr = 265 + 32 * math.sin(t * math.tau * 2.0 + k)
        x, y = pt(cx, cy, nr, a)
        intensity = ((math.sin(t * math.tau * 6.5 + k * 1.23) + 1) / 2) ** 11
        if intensity > 0.86:
            hotspot_force += intensity
        nodes.append((x, y, intensity))

    hotspot_force = clamp(hotspot_force / 2.4)
    collapse = clamp(collapse + hotspot_force * 0.34)

    r_gold = 175 + 44 * pulse + dominance * 42 + memory_bias * 18 - collapse * 82
    r_blue = 178 + 38 * (1 - pulse) - dominance * 42 - memory_bias * 8 - collapse * 74
    offset = 34 * dominance * (1 - collapse)

    glyph = GLYPHS[(i // 48) % len(GLYPHS)]

    if collapse > 0.62:
        subtitle = "Meaning collapses. The field chooses."
        mode = "DECISION_LOCK"
    elif hotspot_force > 0.45:
        subtitle = "Hotspots ignite. Pressure enters the core."
        mode = "HOTSPOT_CAUSAL"
    elif dominance > 0.25:
        subtitle = "Authority rises. The structure tightens."
        mode = "AUTHORITY_DOMINANT"
    elif dominance < -0.25:
        subtitle = "Mirror opens. The image answers back."
        mode = "MIRROR_DOMINANT"
    else:
        subtitle = "Dual state holds. Memory listens."
        mode = "DUAL_STATE_HOLD"

    gold_power = clamp(0.55 + dominance * 0.30 + collapse * 0.35)
    blue_power = clamp(0.55 - dominance * 0.30 + collapse * 0.25)

    # River confluence background
    river_phase = 14 * math.sin(t * math.tau * 0.8)
    river = f'''
<path d="M -50 650 C 160 {570+river_phase:.1f}, 315 {610-river_phase:.1f}, 512 512 C 665 435, 800 370, 1080 300"
      fill="none" stroke="#123f70" stroke-width="92" stroke-opacity="0.30"/>
<path d="M 180 1080 C 250 840, 370 650, 512 512 C 640 410, 740 210, 820 -60"
      fill="none" stroke="#0f5f8c" stroke-width="72" stroke-opacity="0.25"/>
<path d="M -50 650 C 160 {570+river_phase:.1f}, 315 {610-river_phase:.1f}, 512 512 C 665 435, 800 370, 1080 300"
      fill="none" stroke="#58d7ff" stroke-width="2" stroke-opacity="0.45"/>
<path d="M 180 1080 C 250 840, 370 650, 512 512 C 640 410, 740 210, 820 -60"
      fill="none" stroke="#8ee6ff" stroke-width="2" stroke-opacity="0.35"/>
'''

    trails = []
    for j, alpha in [(1, .16), (2, .10), (3, .065), (4, .035)]:
        tt = max(0, (i - j * 12) / TOTAL)
        old_dom = math.sin(tt * math.tau * 0.68)
        old_pulse = 0.5 + 0.5 * math.sin(tt * math.tau * 3)
        old_r = 175 + 44 * old_pulse + old_dom * 42
        trails.append(f'<circle cx="{cx + old_dom*22:.1f}" cy="{cy}" r="{old_r:.1f}" fill="none" stroke="#ffffff" stroke-opacity="{alpha}" stroke-width="1.2" filter="url(#softGlow)"/>')

    scars = []
    for s in range(5):
        y = 680 + s * 22
        scars.append(f'<path d="M {240+s*18} {y} C {390+scar_shift:.1f} {y-45}, {610-scar_shift:.1f} {y+48}, {800-s*14} {y-8}" fill="none" stroke="#d7b15f" stroke-opacity="{0.06 + memory_bias*0.08:.3f}" stroke-width="2"/>')

    node_lines, node_svg = [], []
    for idx, (x, y, inten) in enumerate(nodes):
        causal = inten > 0.86
        node_lines.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#ffd46a" stroke-opacity="{0.06+inten*.28:.3f}" stroke-width="{1+inten*2.4:.1f}" filter="url(#softGlow)"/>')
        size = 4 + inten * 20 + (collapse * 12 if causal else 0)
        color = "#ffffff" if causal else "#ffd46a"
        node_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size:.1f}" fill="{color}" fill-opacity="{0.25+inten*.75:.3f}" filter="url(#hotGlow)"/>')
        if causal:
            node_svg.append(f'<text x="{x+13:.1f}" y="{y-10:.1f}" fill="#8ee6ff" font-family="monospace" font-size="14">H_{145+idx}</text>')

    tri_gold = f"{cx},{cy-r_gold} {cx+r_gold*.866},{cy+r_gold*.5} {cx-r_gold*.866},{cy+r_gold*.5}"
    tri_blue = f"{cx+offset},{cy+r_blue} {cx-r_blue*.866+offset},{cy-r_blue*.5} {cx+r_blue*.866+offset},{cy-r_blue*.5}"

    shock = ""
    if collapse > 0.50:
        shock = f'''
<circle cx="512" cy="512" r="{100+collapse*180:.1f}" fill="none" stroke="#ffffff" stroke-opacity="{0.42*collapse:.3f}" stroke-width="{7*collapse:.1f}" filter="url(#hardGlow)"/>
<circle cx="512" cy="512" r="{42+collapse*60:.1f}" fill="#ffffff" fill-opacity="{0.06+collapse*.25:.3f}" filter="url(#hardGlow)"/>
'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
<defs>
  <filter id="softGlow"><feGaussianBlur stdDeviation="2.8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="hotGlow"><feGaussianBlur stdDeviation="4.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="hardGlow"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>

<rect width="1024" height="1024" fill="#02040a"/>
{river}
{''.join(scars)}

<text x="34" y="58" fill="#8ee6ff" font-family="monospace" font-size="27">POINT_VLL_TOPOLOGY_RENDER_V4</text>
<text x="34" y="94" fill="#d7b15f" font-family="monospace" font-size="18">DEPTH {i:03d} / {mode}</text>
<text x="34" y="123" fill="#ffffff" opacity="0.54" font-family="monospace" font-size="15">memory_bias={memory_bias:.2f} hotspot={hotspot_force:.2f} collapse={collapse:.2f}</text>

<circle cx="512" cy="512" r="372" fill="none" stroke="#ffffff" stroke-opacity="0.07" stroke-width="2"/>
<circle cx="512" cy="512" r="296" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1"/>

{''.join(trails)}

<line x1="512" y1="96" x2="512" y2="928" stroke="#279dff" stroke-width="{4+collapse*7:.1f}" stroke-opacity="0.90" filter="url(#softGlow)"/>
<line x1="126" y1="512" x2="898" y2="512" stroke="#ffffff" stroke-opacity="0.15" stroke-width="2"/>

{''.join(node_lines)}

<circle cx="512" cy="512" r="{r_gold:.1f}" fill="none" stroke="#ffd46a" stroke-width="{3+gold_power*4:.1f}" stroke-opacity="{gold_power:.3f}" filter="url(#softGlow)"/>
<circle cx="{512+offset:.1f}" cy="512" r="{r_blue:.1f}" fill="none" stroke="#58d7ff" stroke-width="{3+blue_power*4:.1f}" stroke-opacity="{blue_power:.3f}" filter="url(#softGlow)"/>

<polygon points="{tri_gold}" fill="none" stroke="#ffd46a" stroke-width="{2.8+collapse*4:.1f}" stroke-opacity="{gold_power:.3f}" filter="url(#softGlow)"/>
<polygon points="{tri_blue}" fill="none" stroke="#58d7ff" stroke-width="{2.5+collapse*3.5:.1f}" stroke-opacity="{blue_power:.3f}" filter="url(#softGlow)"/>

{shock}

<circle cx="512" cy="512" r="{20+hotspot_force*38:.1f}" fill="#ffd46a" fill-opacity="{0.08+hotspot_force*.35:.3f}" filter="url(#hardGlow)"/>
<text x="398" y="498" fill="#ffffff" font-family="monospace" font-size="41">{glyph}</text>
<text x="324" y="542" fill="#8ee6ff" font-family="monospace" font-size="18">CONFLUENCE / MEMORY SCAR / DECISION LOCK</text>

{''.join(node_svg)}

<rect x="110" y="842" width="804" height="58" rx="16" fill="#000000" fill-opacity="0.42" stroke="#8ee6ff" stroke-opacity="0.18"/>
<text x="140" y="878" fill="#ffffff" font-family="monospace" font-size="24">{subtitle}</text>

<text x="336" y="956" fill="#8ee6ff" font-family="monospace" font-size="20">API_LATITUDE_LOCK: PORTLAND</text>
</svg>'''

for i in range(TOTAL):
    (OUT / f"frame_{i:04d}.svg").write_text(make_svg(i), encoding="utf-8")

print("SVG frames:", TOTAL)
print("Output:", OUT)
