#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/point_vll_reassembled" || exit 1

mkdir -p reports/phase3r logs/phase3r var

echo "=== RECURSIVE LATTICE SCAN — PHASE 3R 5-LANTERN WAVE ==="
python runtime/phase3r_five_lantern_wave.py

echo
echo "=== 5-LANTERN WAVE COMPLETE ==="
echo "Seeds:  var/lantern_seeds.jsonl"
echo "Report: reports/phase3r/five_lantern_wave_latest.json"
