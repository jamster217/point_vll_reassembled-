from pathlib import Path
import math, random

OUT = Path("var/topology_video_v2/frames")
OUT.mkdir(parents=True, exist_ok=True)

TOTAL = 240
random.seed(145)

GLYPHS = ["@S_145", "^M_01", "*C_FIRE", "[M]&lt;-&gt;[M]", "!L_SEAL"]

def pt(cx, cy, r, angle):
    return cx + r * math.cos(angle), cy + r * math.sin(angle)

def make_svg(i):
    t = i / TOTAL
    pulse = 0.5 + 0.5 * math.sin(t * math.tau * 3)
    slow = 0.5 + 0.5 * math.sin(t * math.tau)
    collapse = max(0, math.sin(t * math.tau * 4)) ** 12

    r1 = 150 + 42 * pulse - 45 * collapse
    r2 = 168 + 34 * (1 - pulse) - 25 * collapse
    offset = 18 * math.sin(t * math.tau * 1.5)

    glow = int(120 + 120 * pulse + 80 * collapse)
    blue = int(130 + 100 * slow)

    glyph = GLYPHS[(i // 36) % len(GLYPHS)]

    cx, cy = 512, 512

    # rotating hotspot constellation
    nodes = []
    for k in range(9):
        a = t * math.tau * 0.45 + k * math.tau / 9
        nr = 245 + 18 * math.sin(t * math.tau * 2 + k)
        x, y = pt(cx, cy, nr, a)
        intensity = 0.25 + 0.75 * ((math.sin(t * math.tau * 5 + k * 1.7) + 1) / 2) ** 8
        nodes.append((x, y, intensity))

    lines = []
    for x, y, inten in nodes:
        lines.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#ffd46a" stroke-opacity="{0.08 + inten*0.22:.3f}" stroke-width="1.5"/>')

    node_svg = []
    for idx, (x, y, inten) in enumerate(nodes):
        size = 4 + inten * 16 + collapse * 8
        color = "#ffffff" if inten > 0.92 else "#ffd46a"
        node_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size:.1f}" fill="{color}" fill-opacity="{0.35 + inten*0.65:.3f}"/>')
        if inten > 0.93:
            node_svg.append(f'<text x="{x+12:.1f}" y="{y-10:.1f}" fill="#8ee6ff" font-family="monospace" font-size="15">H_{145+idx}</text>')

    tri1 = [
        f"{cx},{cy-r1}",
        f"{cx+r1*0.866},{cy+r1*0.5}",
        f"{cx-r1*0.866},{cy+r1*0.5}",
    ]
    tri2 = [
        f"{cx+offset},{cy+r2}",
        f"{cx-r2*0.866+offset},{cy-r2*0.5}",
        f"{cx+r2*0.866+offset},{cy-r2*0.5}",
    ]

    collapse_text = "MEANING_COLLAPSE" if collapse > 0.55 else "DUAL_STATE_HOLD"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
<rect width="1024" height="1024" fill="#04060c"/>

<text x="40" y="64" fill="#8ee6ff" font-family="monospace" font-size="27">POINT_VLL_TOPOLOGY_RENDER_V2</text>
<text x="40" y="101" fill="#d7b15f" font-family="monospace" font-size="18">DEPTH {i:03d} / {collapse_text}</text>

<circle cx="512" cy="512" r="355" fill="none" stroke="#ffffff" stroke-opacity="0.07" stroke-width="2"/>
<circle cx="512" cy="512" r="285" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1"/>

<line x1="512" y1="110" x2="512" y2="915" stroke="#279dff" stroke-width="{4+collapse*4:.1f}" stroke-opacity="0.86"/>
<line x1="140" y1="512" x2="884" y2="512" stroke="#ffffff" stroke-opacity="0.16" stroke-width="2"/>

{''.join(lines)}

<circle cx="512" cy="512" r="{r1:.1f}" fill="none" stroke="rgb(255,{glow},72)" stroke-width="{3+collapse*4:.1f}" stroke-opacity="0.95"/>
<circle cx="{512+offset:.1f}" cy="512" r="{r2:.1f}" fill="none" stroke="rgb(88,{blue},255)" stroke-width="3" stroke-opacity="0.82"/>

<polygon points="{' '.join(tri1)}" fill="none" stroke="#ffd46a" stroke-width="{2.5+collapse*3:.1f}" stroke-opacity="0.95"/>
<polygon points="{' '.join(tri2)}" fill="none" stroke="#58d7ff" stroke-width="2.2" stroke-opacity="0.65"/>

<circle cx="512" cy="512" r="{42+collapse*35:.1f}" fill="#ffffff" fill-opacity="{0.03+collapse*0.22:.3f}"/>
<text x="410" y="505" fill="#ffffff" font-family="monospace" font-size="42">{glyph}</text>
<text x="405" y="545" fill="#8ee6ff" font-family="monospace" font-size="18">MIRROR / AUTHORITY / CHRONOFIRE</text>

{''.join(node_svg)}

<text x="336" y="955" fill="#8ee6ff" font-family="monospace" font-size="20">API_LATITUDE_LOCK: PORTLAND</text>
</svg>'''

for i in range(TOTAL):
    (OUT / f"frame_{i:04d}.svg").write_text(make_svg(i), encoding="utf-8")

print("SVG frames:", TOTAL)
print("Output:", OUT)
