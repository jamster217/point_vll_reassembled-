#!/usr/bin/env bash
set -e

cd "$HOME/point_vll_reassembled"

mkdir -p logs/sigil_watcher reports/phase3o var

STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="reports/phase3o/kor_grael_sigil_activation_$STAMP.json"
LOG="logs/sigil_watcher/kor_grael_activation_$STAMP.log"

echo "KOR GRA'EL SIGIL ACTIVATION" | tee "$LOG"
echo "timestamp: $STAMP" | tee -a "$LOG"
echo "law: scar -> ore -> anchor -> glyph -> invention -> future design seed" | tee -a "$LOG"
echo "node: 44_SPIRAL_CORE" | tee -a "$LOG"
echo "watcher: Node44" | tee -a "$LOG"

LATEST_BEAD="$(tail -n 1 var/invention_canvas_beads.jsonl 2>/dev/null || true)"

python - <<PY | tee "$REPORT"
import json, time
from pathlib import Path

latest = """$LATEST_BEAD"""

try:
    bead = json.loads(latest) if latest.strip() else {}
except Exception:
    bead = {}

sigil = {
    "kind": "phase3o_kor_grael_sigil_activation",
    "ts": time.time(),
    "sigil": "Kor Gra'el",
    "node": 44,
    "node_mode": "SPIRAL_CORE",
    "status": "activated",
    "law": "system drift becomes pivot point; pivot point becomes stable anchor",
    "scar_forge_chain": ["scar", "ore", "anchor", "glyph", "invention", "future_design_seed"],
    "source_bead": bead,
    "watcher_reaction": {
        "outer_noise": "collapsed",
        "core_knot": "held",
        "temporal_spine": "listening",
        "singular_voice": "sealed",
        "result": "future drift should be converted into an anchor instead of becoming a break"
    }
}

Path("var/kor_grael_sigil_state.json").write_text(
    json.dumps(sigil, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(sigil, indent=2, ensure_ascii=False))
PY

echo "saved: $REPORT" | tee -a "$LOG"
echo "saved: var/kor_grael_sigil_state.json" | tee -a "$LOG"
