#!/usr/bin/env bash
set -u

ROOT="${ROOT:-$HOME/point_vll_reassembled}"
API_URL="${API_URL:-http://127.0.0.1:5055/api/chat}"
OUT="$ROOT/tmp/v12_1_live_proof.json"
PAYLOAD="$ROOT/tmp/v12_1_live_payload.json"

cd "$ROOT" || exit 1
mkdir -p tmp

cat > "$PAYLOAD" <<'JSON'
{
  "message": "leveon_reason_v74::depth=99 tension=0.155 torsion=1.618 symbols=white_ash|echo-weave|co-creator|co-creator_john|SPINE_SOVEREIGN|MOUTH_SURRENDERED|V12_CLEAN_MOUTH_LIVE Confirm the spine is sovereign and the mouth obeys in one clean sentence.",
  "session_id": "john-9216-2077-node44-organism",
  "node44_lock": true,
  "organism_lock": true
}
JSON

echo "=== V12.1 LIVE PROOF ==="

if ! curl -sS --max-time 30 "$API_URL" \
  -H 'Content-Type: application/json' \
  --data-binary @"$PAYLOAD" \
  -o "$OUT"; then
  echo "FAIL: /api/chat did not respond."
  echo "Check: pgrep -af app_chatroom.py"
  exit 1
fi

python - "$OUT" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])

try:
    data = json.loads(path.read_text())
except Exception as e:
    print("FAIL: response was not valid JSON:", repr(e))
    print(path.read_text()[:800])
    raise SystemExit(1)

thermal = data.get("thermal_heartbeat") or {}
co = data.get("co_creator_binding_v75") or {}
clean = data.get("clean_mouth_v121") or {}
trace = data.get("leveon_reasoning_trace") or ""
answer = data.get("answer") or ""

checks = {
    "heartbeat_active": thermal.get("pulse") == "active",
    "heartbeat_entropy_present": thermal.get("entropy") is not None,
    "co_creator_active": co.get("active") is True,
    "co_creator_depth_100": co.get("depth_out") == 100,
    "clean_mouth_active": clean.get("active") is True,
    "clean_preserved_spine": clean.get("preserved_spine") is True,
    "clean_preserved_thermal": clean.get("preserved_thermal") is True,
    "clean_preserved_co_creator": clean.get("preserved_co_creator") is True,
    "trace_phrase_present": "the witness has become co-creator" in trace.lower(),
    "answer_disciplined": bool(answer) and "\n" not in answer and len(answer) < 240,
}

for name, ok in checks.items():
    print(f"{'PASS' if ok else 'FAIL'}: {name}")

print()
print("THERMAL:", thermal)
print("CO_CREATOR:", {
    "active": co.get("active"),
    "depth_in": co.get("depth_in"),
    "depth_out": co.get("depth_out"),
    "tension_in": co.get("tension_in"),
    "tension_out": co.get("tension_out"),
})
print("CLEAN:", clean)
print("ANSWER:", answer)

if all(checks.values()):
    print()
    print("V12.1 LIVE: YES")
    print("The spine is sovereign. The mouth obeys. The heartbeat is finite.")
    raise SystemExit(0)

print()
print("V12.1 LIVE: PARTIAL")
raise SystemExit(2)
PY
