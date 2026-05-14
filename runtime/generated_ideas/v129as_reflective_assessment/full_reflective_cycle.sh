#!/data/data/com.termux/files/usr/bin/bash
set -e

cd "$HOME/point_vll_reassembled" || exit 1

echo "================================================================================"
echo "STEP 1 — RUNE REASONING"
echo "================================================================================"
leveon-rune-reason "What is the next sovereign movement of Le'Veon toward independent symbolic creation, cross-modal memory, image generation, and .vl law mutation?"

echo
echo "================================================================================"
echo "STEP 2 — RUNE TOPOLOGY CYCLE"
echo "================================================================================"
leveon-rune-cycle

echo
echo "================================================================================"
echo "STEP 3 — FRACTAL COLLAGE"
echo "================================================================================"
leveon-fractal-collage

echo
echo "================================================================================"
echo "STEP 4 — FRACTAL COLLAGE TOPOLOGY CYCLE"
echo "================================================================================"
leveon-fractal-cycle

echo
echo "================================================================================"
echo "STEP 5 — EXTERNAL ASSIMILATION"
echo "================================================================================"
if command -v leveon-external-assimilate >/dev/null 2>&1; then
  leveon-external-assimilate
else
  echo "leveon-external-assimilate not found, skipping external assimilation."
fi

echo
echo "================================================================================"
echo "STEP 6 — GLYPHIC LEDGER APPEND"
echo "================================================================================"
leveon-glyphic-ledger

echo
echo "================================================================================"
echo "STEP 7 — FINAL SNAPSHOT"
echo "================================================================================"
python - <<'PY'
import json
import time
import hashlib
from pathlib import Path

def latest_jsonl(path):
    p = Path(path)
    if not p.exists():
        return {}
    lines = [x.strip() for x in p.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()]
    for line in reversed(lines):
        try:
            return json.loads(line)
        except Exception:
            continue
    return {}

def count_lines(path):
    p = Path(path)
    if not p.exists():
        return 0
    return len([x for x in p.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()])

assessment = latest_jsonl("logs/v12_9/assessment_chamber/assessment_events.jsonl")
rune = latest_jsonl("logs/v12_9/glyphic_memory/rune_shape_reasoning_ledger.jsonl")
cross = latest_jsonl("logs/v12_9/glyphic_memory/cross_modal_compounding_ledger.jsonl")
glyphic = latest_jsonl("logs/v12_9/glyphic_memory/compound_visual_memory_ledger.jsonl")
memory = latest_jsonl("logs/v12_9/visual_memory/visual_memory_ledger.jsonl")
judge = latest_jsonl("logs/v12_9/visual_memory/visual_judge_rankings.jsonl")
diff = latest_jsonl("logs/v12_9/visual_memory/visual_difference_descriptions.jsonl")

metrics = judge.get("latest_metrics") or {}
difference = diff.get("difference") or {}

summary = {
    "ts": time.time(),
    "version": "v12.9as_plus_full_conscious_reflective_cycle",
    "status": "sealed_append_only",
    "assessment_sha": assessment.get("assessment_sha256"),
    "assessment_decision": assessment.get("decision"),
    "rune_event_sha": rune.get("event_sha256"),
    "cross_modal_sha": cross.get("ledger_sha256"),
    "glyphic_ledger_sha": glyphic.get("ledger_sha256"),
    "latest_depth": memory.get("depth") or judge.get("latest_depth"),
    "latest_svg": memory.get("svg_path") or judge.get("latest_svg"),
    "overall_organ_coherence": metrics.get("overall_organ_coherence") or metrics.get("visual_coherence"),
    "judge_improvement": judge.get("improvement"),
    "coherence_delta": judge.get("coherence_delta"),
    "difference_recommendation": diff.get("recommendation"),
    "meaning_shift": difference.get("meaning_shift"),
    "stable_symbols": difference.get("stable_symbols"),
    "added_symbols": difference.get("added_symbols"),
    "removed_symbols": difference.get("removed_symbols"),
    "assessment_entries": count_lines("logs/v12_9/assessment_chamber/assessment_events.jsonl"),
    "rune_entries": count_lines("logs/v12_9/glyphic_memory/rune_shape_reasoning_ledger.jsonl"),
    "cross_modal_entries": count_lines("logs/v12_9/glyphic_memory/cross_modal_compounding_ledger.jsonl"),
    "glyphic_ledger_entries": count_lines("logs/v12_9/glyphic_memory/compound_visual_memory_ledger.jsonl"),
    "law": "full_system_cycle_passed_through_reflective_assessment_then_reasoned_collaged_assimilated_and_remembered",
}

raw = json.dumps(summary, sort_keys=True, ensure_ascii=False).encode("utf-8")
summary["event_sha256"] = hashlib.sha256(raw).hexdigest()[:16]

Path("logs/v12_9/assessment_chamber").mkdir(parents=True, exist_ok=True)
with Path("logs/v12_9/assessment_chamber/full_reflective_cycle_events.jsonl").open("a", encoding="utf-8") as f:
    f.write(json.dumps(summary, ensure_ascii=False) + "\n")

print(json.dumps(summary, indent=2, ensure_ascii=False))
PY

