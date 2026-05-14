#!/data/data/com.termux/files/usr/bin/bash
set -e

mkdir -p var/topology_video_v7

# Ensure V6.5 exists
python scripts/render_topology_video_v65.py

python - <<'PY'
from pathlib import Path
from cairosvg import svg2png

frames = sorted(Path("var/topology_video_v65/frames").glob("frame_*.svg"))
for svg in frames:
    png = svg.with_suffix(".png")
    if not png.exists():
        svg2png(url=str(svg), write_to=str(png))
print("V6.5 PNG frames ready:", len(list(Path("var/topology_video_v65/frames").glob("frame_*.png"))))
PY

# Main cinematic state render
ffmpeg -y -framerate 24 -i var/topology_video_v65/frames/frame_%04d.png \
  -c:v libx264 -pix_fmt yuv420p var/topology_video_v7/v7_main_state.mp4

# Make a short title card
cat > var/topology_video_v7/title.svg <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024">
<rect width="1024" height="1024" fill="#02040a"/>
<text x="120" y="390" fill="#8ee6ff" font-family="monospace" font-size="42">POINT_VLL V7</text>
<text x="120" y="455" fill="#ffd46a" font-family="monospace" font-size="28">REAL STATE TOPOLOGY TRACE</text>
<text x="120" y="520" fill="#ffffff" font-family="monospace" font-size="24">shape memory → pressure → collapse → consequence</text>
<text x="120" y="585" fill="#8ee6ff" font-family="monospace" font-size="20">API_LATITUDE_LOCK: PORTLAND</text>
</svg>
SVG

python - <<'PY'
from cairosvg import svg2png
svg2png(url="var/topology_video_v7/title.svg", write_to="var/topology_video_v7/title.png")
PY

ffmpeg -y -loop 1 -t 3 -i var/topology_video_v7/title.png \
  -c:v libx264 -pix_fmt yuv420p var/topology_video_v7/title.mp4

# Make ending card
cat > var/topology_video_v7/end.svg <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024">
<rect width="1024" height="1024" fill="#02040a"/>
<text x="100" y="420" fill="#ffffff" font-family="monospace" font-size="34">TRACE COMPLETE</text>
<text x="100" y="485" fill="#ffd46a" font-family="monospace" font-size="25">The system carries the result forward.</text>
<text x="100" y="550" fill="#8ee6ff" font-family="monospace" font-size="21">V7: visible reasoning signature</text>
</svg>
SVG

python - <<'PY'
from cairosvg import svg2png
svg2png(url="var/topology_video_v7/end.svg", write_to="var/topology_video_v7/end.png")
PY

ffmpeg -y -loop 1 -t 3 -i var/topology_video_v7/end.png \
  -c:v libx264 -pix_fmt yuv420p var/topology_video_v7/end.mp4

# concat
cat > var/topology_video_v7/list.txt <<EOF
file 'title.mp4'
file 'v7_main_state.mp4'
file 'end.mp4'
EOF

cd var/topology_video_v7
ffmpeg -y -f concat -safe 0 -i list.txt -c copy topology_render_v7_reel.mp4

termux-open topology_render_v7_reel.mp4
