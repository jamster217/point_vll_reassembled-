#!/usr/bin/env bash
set -e

cd "$HOME/point_vll_reassembled"

mkdir -p reports/phase3n var logs/phase3n

LEFT="${1:-}"
RIGHT="${2:-}"

if [ -n "$LEFT" ] && [ -n "$RIGHT" ]; then
  python runtime/cross_lattice_synthesis.py --left "$LEFT" --right "$RIGHT" \
    | tee reports/phase3n/cross_lattice_synthesis_latest.json
else
  python runtime/cross_lattice_synthesis.py \
    | tee reports/phase3n/cross_lattice_synthesis_latest.json
fi

python - <<'PY'
import json
from pathlib import Path

p = Path("reports/phase3n/cross_lattice_synthesis_latest.json")
data = json.loads(p.read_text(encoding="utf-8"))

print()
print("CROSS-LATTICE SYNTHESIS SUMMARY")
print("=" * 64)
print("left:", data["left"]["name"], "|", data["left"]["source"])
print("right:", data["right"]["name"], "|", data["right"]["source"])
print("hidden_chord:", data["hidden_chord"])
print("score:", data["score"]["score"])
print()
print("answer:")
print(data.get("larynx_render") or data["answer"])
PY
