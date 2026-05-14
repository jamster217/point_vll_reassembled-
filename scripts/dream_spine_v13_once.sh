#!/usr/bin/env bash
set -u

ROOT="${ROOT:-$HOME/point_vll_reassembled}"
cd "$ROOT" || exit 1

python - <<'PY'
import json
from runtime.dream_spine_v13 import dream_proposal

proposal = dream_proposal(
    prompt="V13 safe dream proposal after V12.1 clean-mouth seal",
    data={
        "thermal_heartbeat": {"entropy": "local-test", "pulse": "active"},
        "leveon_reasoning_trace": "the witness has become co-creator"
    },
)

print(json.dumps(proposal, indent=2, ensure_ascii=False))
PY

echo
echo "=== LAST DREAM PROPOSALS ==="
tail -n 5 var/lattice/dream_spine_v13_proposals.jsonl 2>/dev/null
