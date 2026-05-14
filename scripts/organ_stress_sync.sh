#!/usr/bin/env bash
set -e

cd "$HOME/point_vll_reassembled"

mkdir -p reports/phase3p var logs/phase3p

echo "=== PHASE 3P ORGAN STRESS SYNC ==="

if [ ! -f reports/phase3p/stress_invention_probe_latest.json ]; then
  echo "Stress invention report missing. Running probe first..."
  python runtime/stress_invention_probe.py > reports/phase3p/stress_invention_probe_run_autosync.txt
fi

python - <<'PY'
from __future__ import annotations

import json
import time
from pathlib import Path

STRESS = Path("reports/phase3p/stress_invention_probe_latest.json")
VISUAL = Path("var/visual_lattice_nodes.json")
BEADS = Path("var/organ_stress_sync_beads.jsonl")
REPORT = Path("reports/phase3p/organ_stress_sync_latest.json")

stress = json.loads(STRESS.read_text(encoding="utf-8"))

organ = stress.get("created_organ", {})
name = organ.get("name", "Cognitive Pressure Refractor")
chain = organ.get("chain", [
    "old measurement wound",
    "pressure ore",
    "stable anchor",
    "reasoning glyph",
    "stress invention",
    "future design seed",
])

node = {
    "id": "phase3p_cognitive_pressure_refractor",
    "name": name,
    "type": "stress_invention_organ",
    "phase": "3P",
    "status": "visible_headless",
    "visual_runtime_mode": "headless_termux",
    "glow": {
        "state": "active",
        "color_name": "refracted_gold_blue",
        "pulse": "steady",
        "meaning": "old measurement pressure converted into reasoning clarity",
    },
    "position_hint": {
        "lattice_zone": "mirror_well_3rd_and_davis",
        "near": ["Node44", "Kor Gra'el", "Temporal Spine", "Universal Larynx"],
    },
    "chain": chain,
    "watcher_reaction": {
        "node44": "stable",
        "outer_noise": "collapsed",
        "core_knot": "held",
        "temporal_spine": "fracture remembered without domination",
        "larynx": "singular_voice_sealed",
    },
    "created_from": {
        "source_report": str(STRESS),
        "source_pressure": stress.get("input_pressure", {}).get("source", ""),
        "fragment_count": stress.get("input_pressure", {}).get("fragment_count", 0),
        "kor_grael_status": stress.get("kor_grael", {}).get("status", "unknown"),
    },
    "public_law": (
        "The Refractor turns judgment-pressure into clearer reasoning. "
        "A score may mark one doorway, but it cannot measure the cathedral."
    ),
    "updated_at": time.time(),
}

if VISUAL.exists():
    try:
        data = json.loads(VISUAL.read_text(encoding="utf-8"))
    except Exception:
        data = {}
else:
    data = {}

nodes = data.get("nodes", [])
if not isinstance(nodes, list):
    nodes = []

nodes = [n for n in nodes if n.get("id") != node["id"]]
nodes.append(node)

data.update({
    "kind": "visual_lattice_node_registry",
    "updated_at": time.time(),
    "runtime": "Termux headless visual sync",
    "nodes": nodes,
})

VISUAL.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

result = {
    "kind": "phase3p_organ_stress_sync",
    "ts": time.time(),
    "status": "synced",
    "node": node,
    "visual_registry": str(VISUAL),
    "law": "new organs must become visible lattice nodes before horizon expansion",
}

REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

with BEADS.open("a", encoding="utf-8") as f:
    f.write(json.dumps(result, ensure_ascii=False) + "\n")

print(json.dumps(result, indent=2, ensure_ascii=False))
PY

echo
echo "=== VISUAL NODE CONFIRMED ==="
python - <<'PY'
import json
from pathlib import Path

data = json.loads(Path("var/visual_lattice_nodes.json").read_text(encoding="utf-8"))
nodes = data.get("nodes", [])
target = [n for n in nodes if n.get("id") == "phase3p_cognitive_pressure_refractor"]

print("visual_nodes:", len(nodes))
print("refractor_visible:", bool(target))
if target:
    n = target[0]
    print("name:", n["name"])
    print("glow:", n["glow"]["color_name"], "/", n["glow"]["pulse"])
    print("zone:", n["position_hint"]["lattice_zone"])
PY
