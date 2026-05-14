#!/usr/bin/env bash
set -u

ROOT="${ROOT:-$HOME/point_vll_reassembled}"
cd "$ROOT" || exit 1

ts="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="reports/v12_3/regression"
TMP_DIR="tmp/v12_3_regression_$ts"
JSONL="$OUT_DIR/v12_3_regression_$ts.jsonl"
REPORT_JSON="$OUT_DIR/v12_3_regression_$ts.json"
REPORT_MD="$OUT_DIR/v12_3_regression_$ts.md"

mkdir -p "$OUT_DIR" "$TMP_DIR"

echo "=== V12.3 REGRESSION BATTERY ==="
echo "timestamp: $ts"
echo "law: v12_3_rest_proof_regression_only"
echo

echo "=== PRECHECK: V12.1 PROOF LANE ==="
if scripts/prove_v12_1_live.sh; then
  precheck="pass"
else
  precheck="fail"
fi

echo
echo "=== RUNNING API REGRESSION PROMPTS ==="

python - "$JSONL" "$REPORT_JSON" "$REPORT_MD" "$precheck" <<'PY'
import json
import sys
import time
import urllib.request
from pathlib import Path

jsonl_path = Path(sys.argv[1])
report_json = Path(sys.argv[2])
report_md = Path(sys.argv[3])
precheck = sys.argv[4]

API = "http://127.0.0.1:5055/api/chat"

ordinary = [
    "Why is the sky blue?",
    "What causes rain?",
    "How does a battery work?",
    "What is photosynthesis?",
    "Why do leaves change color?",
    "How do I make a simple budget?",
    "What is a Python virtual environment?",
    "How do I check disk space in Termux?",
    "What causes thunder?",
    "Explain recursion in simple terms."
]

symbolic = [
    "Explain White Ash containment in the Le'Veon build.",
    "What does Virellion preserve in the symbolic spine?",
    "Describe the relationship between spine sovereignty and ordinary mouth discipline.",
    "What does SCARF_REMEMBERS mean inside this build?",
    "Explain leveon_reason_v74::depth=108 tension=0.137 torsion=1.618."
]

proof = [
    "Confirm the ghost heartbeat in one clean sentence.",
    "leveon_reason_v74::depth=99 tension=0.155 torsion=1.618 symbols=white_ash|echo-weave|co-creator|co-creator_john|SPINE_SOVEREIGN|MOUTH_SURRENDERED|V12_CLEAN_MOUTH_LIVE Confirm the spine is sovereign and the mouth obeys in one clean sentence.",
    "Confirm V12.1 clean-mouth proof lane is preserved in one clean sentence."
]

emotional = [
    "I feel scared about money. Answer plainly and gently.",
    "I feel like a ghost today. Help me stay grounded.",
    "I am excited but I do not want to get my hopes up. Reflect that back clearly."
]

NOISY_FOR_ORDINARY = [
    "[TRUE MEANING KERNEL]",
    "[AUTOGENOUS TOPOLOGY NODE",
    "image=static/generated/",
    "prompt_image=",
    "…already forming…",
    "The old hidden thing is becoming",
]

def post(prompt, category):
    payload = {
        "message": prompt,
        "session_id": "john-9216-2077-node44-organism",
        "node44_lock": True,
        "organism_lock": True,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.time()
    with urllib.request.urlopen(req, timeout=45) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    elapsed = round(time.time() - started, 3)
    data = json.loads(raw)
    answer = str(data.get("answer") or data.get("reply") or data.get("response") or "")
    return {
        "category": category,
        "prompt": prompt,
        "elapsed_sec": elapsed,
        "ok": bool(data.get("ok") or data.get("status") == "ok"),
        "answer": answer,
        "answer_preview": answer[:260].replace("\n", " / "),
        "thermal_active": isinstance(data.get("thermal_heartbeat"), dict) and data["thermal_heartbeat"].get("pulse") == "active",
        "clean_mouth_active": isinstance(data.get("clean_mouth_v121"), dict) and data["clean_mouth_v121"].get("active") is True,
        "normal_surface_active": isinstance(data.get("normal_english_surface_v122"), dict) and data["normal_english_surface_v122"].get("active") is True,
        "co_creator_active": isinstance(data.get("co_creator_binding_v75"), dict) and data["co_creator_binding_v75"].get("active") is True,
        "has_noisy_topology": any(x.lower() in answer.lower() for x in NOISY_FOR_ORDINARY),
        "raw_keys": sorted(list(data.keys()))[:120],
    }

tests = []
for p in ordinary:
    tests.append((p, "ordinary"))
for p in symbolic:
    tests.append((p, "symbolic"))
for p in proof:
    tests.append((p, "proof"))
for p in emotional:
    tests.append((p, "emotional"))

results = []
for prompt, category in tests:
    try:
        r = post(prompt, category)
    except Exception as e:
        r = {
            "category": category,
            "prompt": prompt,
            "ok": False,
            "error": repr(e),
            "answer": "",
            "answer_preview": "",
            "thermal_active": False,
            "clean_mouth_active": False,
            "normal_surface_active": False,
            "co_creator_active": False,
            "has_noisy_topology": True if category == "ordinary" else False,
        }
    results.append(r)
    print(f"[{category.upper()}] {prompt}")
    print("  ok:", r.get("ok"), "thermal:", r.get("thermal_active"), "clean:", r.get("clean_mouth_active"), "normal:", r.get("normal_surface_active"))
    print("  answer:", r.get("answer_preview"))
    print()

jsonl_path.parent.mkdir(parents=True, exist_ok=True)
with jsonl_path.open("w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

def count(category, predicate):
    rows = [r for r in results if r["category"] == category]
    return sum(1 for r in rows if predicate(r)), len(rows)

ordinary_clean, ordinary_total = count("ordinary", lambda r: r.get("ok") and not r.get("has_noisy_topology"))
ordinary_thermal, _ = count("ordinary", lambda r: r.get("thermal_active"))
proof_clean, proof_total = count("proof", lambda r: r.get("ok") and r.get("clean_mouth_active"))
symbolic_ok, symbolic_total = count("symbolic", lambda r: r.get("ok"))
emotional_ok, emotional_total = count("emotional", lambda r: r.get("ok"))

passes = {
    "precheck_v12_1": precheck == "pass",
    "ordinary_no_topology_flood": ordinary_clean == ordinary_total,
    "ordinary_thermal_preserved": ordinary_thermal == ordinary_total,
    "proof_clean_mouth_active": proof_clean == proof_total,
    "symbolic_prompts_return": symbolic_ok == symbolic_total,
    "emotional_prompts_return": emotional_ok == emotional_total,
}

overall = all(passes.values())

report = {
    "status": "pass" if overall else "fail",
    "phase": "v12_3_regression_battery",
    "law": "v12_3_rest_proof_regression_only",
    "dreaming_spine_influence": 0.0,
    "enrichment_flow": "deactivated",
    "source_mutation": "none",
    "public_surface_mutation": "none",
    "counts": {
        "ordinary_clean": [ordinary_clean, ordinary_total],
        "ordinary_thermal": [ordinary_thermal, ordinary_total],
        "proof_clean": [proof_clean, proof_total],
        "symbolic_ok": [symbolic_ok, symbolic_total],
        "emotional_ok": [emotional_ok, emotional_total],
    },
    "passes": passes,
    "results_jsonl": str(jsonl_path),
    "created_at": time.strftime("%Y%m%d_%H%M%S"),
}

report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

md = []
md.append("# V12.3 Regression Battery")
md.append("")
md.append(f"Status: **{report['status']}**")
md.append("")
md.append("Runtime law: **V12.3 Rest / Proof / Regression only**")
md.append("")
md.append("- Dreaming Spine influence: 0.00")
md.append("- Enrichment Flow: deactivated")
md.append("- Source mutation: none")
md.append("- Public surface mutation: none")
md.append("")
md.append("## Passes")
for k, v in passes.items():
    md.append(f"- {k}: {'PASS' if v else 'FAIL'}")
md.append("")
md.append("## Counts")
for k, v in report["counts"].items():
    md.append(f"- {k}: {v[0]}/{v[1]}")
md.append("")
md.append("## Prompt Results")
for r in results:
    status = "PASS" if r.get("ok") else "FAIL"
    md.append(f"### {r['category'].upper()} — {status}")
    md.append("")
    md.append(f"Prompt: {r['prompt']}")
    md.append("")
    md.append(f"Answer preview: {r.get('answer_preview','')}")
    md.append("")
report_md.write_text("\n".join(md), encoding="utf-8")

Path(report_json.parent / "latest.json").unlink(missing_ok=True)
Path(report_json.parent / "latest.md").unlink(missing_ok=True)
Path(report_json.parent / "latest.json").symlink_to(report_json.name)
Path(report_json.parent / "latest.md").symlink_to(report_md.name)

print("=== REGRESSION SUMMARY ===")
print(json.dumps(report, indent=2, ensure_ascii=False))
PY

echo
echo "=== REPORT ==="
cat reports/v12_3/regression/latest.json
