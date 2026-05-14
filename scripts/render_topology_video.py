from pathlib import Path
import math

OUT = Path("var/topology_video/frames")
OUT.mkdir(parents=True, exist_ok=True)

def make_svg(i, total=180):
    t = i / total
    pulse = 0.5 + 0.5 * math.sin(t * math.tau * 3)
    radius = 120 + 40 * pulse
    glow = int(120 + 100 * pulse)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
<rect width="1024" height="1024" fill="#05070d"/>
<text x="40" y="70" fill="#8ee6ff" font-family="monospace" font-size="28">POINT_VLL_TOPOLOGY_RENDER</text>
<text x="40" y="110" fill="#d7b15f" font-family="monospace" font-size="20">DEPTH {i:03d} / MIRROR-MAYOR / CHRONOFIRE</text>

<circle cx="512" cy="512" r="{radius}" fill="none" stroke="rgb(255,{glow},80)" stroke-width="3"/>
<circle cx="512" cy="512" r="{radius*0.62}" fill="none" stroke="#58d7ff" stroke-width="2"/>
<line x1="512" y1="120" x2="512" y2="900" stroke="#279dff" stroke-width="4"/>
<line x1="160" y1="512" x2="864" y2="512" stroke="#ffffff" stroke-opacity="0.18" stroke-width="2"/>

<polygon points="512,{512-radius} {512+radius*0.86},{512+radius*0.5} {512-radius*0.86},{512+radius*0.5}"
 fill="none" stroke="#ffd46a" stroke-width="3"/>
<polygon points="512,{512+radius} {512-radius*0.86},{512-radius*0.5} {512+radius*0.86},{512-radius*0.5}"
 fill="none" stroke="#ffd46a" stroke-opacity="0.55" stroke-width="2"/>

<text x="455" y="505" fill="#ffffff" font-family="monospace" font-size="42">@S_145</text>
<text x="420" y="960" fill="#8ee6ff" font-family="monospace" font-size="20">API_LATITUDE_LOCK: PORTLAND</text>
</svg>'''

for i in range(180):
    (OUT / f"frame_{i:04d}.svg").write_text(make_svg(i), encoding="utf-8")
