from pathlib import Path
from PIL import Image, ImageDraw
import math

ROOT = Path.home() / "point_vll_reassembled"
OUT = ROOT / "reports/governance/conflict_maps/v572_conflict_map.png"

W,H = 1280,720
img = Image.new("RGB",(W,H),(8,10,18))
d = ImageDraw.Draw(img)

d.text((40,25),"V5.7.2 CONFLICT MAP - AUTHORITY x MOTION",(230,220,255))

d.rectangle((0,520,W,H),(18,22,32))
for x in range(0,W,80): d.line((x,520,x,720),(35,40,55),1)
for y in range(540,720,40): d.line((0,y,W,y),(35,40,55),1)

west=(390,330); east=(890,330); mid=(640,350)

d.ellipse((300,240,480,420),outline=(180,130,255),width=4)
d.text((270,205),"WEST HILLS 0.12\nAUTHORITY BRACE",(220,210,255))

d.ellipse((820,260,960,400),outline=(100,255,180),width=4)
d.text((780,220),"EASTBANK 0.08\nKINETIC PIVOT",(200,255,220))

d.ellipse((390,230,890,470),outline=(255,215,100),width=3)
d.text((490,495),"ELLIPTICAL ATTRACTOR: negotiated_survivability",(255,230,160))

for i in range(18):
    t=i/17
    x=int(west[0]*(1-t)+east[0]*t)
    y=int(330+35*math.sin(t*math.pi*6))
    d.line((west[0],west[1],x,y),fill=(160,90,220),width=1)
    d.line((east[0],east[1],x,y),fill=(80,220,170),width=1)

d.ellipse((595,305,685,395),outline=(255,90,140),width=4)
d.text((560,270),"VARIANCE 0.04",(255,180,190))

for n,line in enumerate([
"STATE: DUAL_ANCHOR_TENSIONING_ACTIVE",
"RESOLUTION: negotiated_survivability",
"CONFIDENCE: 0.84",
"LAW: authority_and_motion_must_reconcile_under_survivability_pressure"
]):
    d.text((45,560+n*28),line,(235,235,235))

OUT.parent.mkdir(parents=True,exist_ok=True)
img.save(OUT)
print(OUT)

