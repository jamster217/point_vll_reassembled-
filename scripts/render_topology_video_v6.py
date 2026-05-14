from pathlib import Path
import math
from state_loader_v6 import load_latest_shape, extract_variables

OUT = Path("var/topology_video_v6/frames")
OUT.mkdir(parents=True, exist_ok=True)

TOTAL = 240

state = load_latest_shape()
vars = extract_variables(state)

tension = vars["tension"]
coherence = vars["coherence"]
novelty = vars["novelty"]
memory_depth = vars["memory_depth"]

def make_svg(i):
    t = i / TOTAL
    cx, cy = 512, 512

    # REAL state influences
    collapse = min(1.0, tension * (0.5 + 0.5 * math.sin(t * math.tau * 3)))
    dominance = (coherence - 0.5) * 2
    memory_bias = min(1.0, memory_depth / 100)

    r1 = 180 + dominance * 60 - collapse * 90
    r2 = 180 - dominance * 60 - collapse * 80

    color_shift = int(120 + novelty * 120)

    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024">
<rect width="1024" height="1024" fill="#03050b"/>

<circle cx="{cx}" cy="{cy}" r="{r1}" fill="none"
 stroke="rgb(255,{color_shift},80)" stroke-width="4"/>

<circle cx="{cx}" cy="{cy}" r="{r2}" fill="none"
 stroke="rgb(80,{color_shift},255)" stroke-width="3"/>

<text x="400" y="520" fill="white" font-size="28">
STATE DRIVEN
</text>

<text x="300" y="580" fill="#8ee6ff" font-size="18">
tension={tension:.2f} coherence={coherence:.2f}
</text>

</svg>
'''

for i in range(TOTAL):
    (OUT / f"frame_{i:04d}.svg").write_text(make_svg(i))

print("V6 frames generated")
