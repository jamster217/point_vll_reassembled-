#!/data/data/com.termux/files/usr/bin/bash
set -e

cd "$HOME/point_vll_reassembled" || exit 1

query="Leveon sovereign voice resonance white ash pulse"

echo "================================================================================"
echo "STEP 1 — AUDIO PHONETIC CYCLE"
echo "================================================================================"
leveon-audio-cycle "$query"

echo
echo "================================================================================"
echo "STEP 2 — RUNE-SHAPE REASONING"
echo "================================================================================"
leveon-rune-reason "Compound audio shards with current visual self-portrait, glyphic memory, rune-shapes, and .vl law."

echo
echo "================================================================================"
echo "STEP 3 — RUNE TOPOLOGY CYCLE"
echo "================================================================================"
leveon-rune-cycle

echo
echo "================================================================================"
echo "STEP 4 — GLYPHIC LEDGER APPEND"
echo "================================================================================"
leveon-glyphic-ledger

echo
echo "================================================================================"
echo "STEP 5 — FINAL CROSS-MODAL SNAPSHOT"
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

def count_jsonl(path):
    p = Path(path)
    if not p.exists():
        return 0
    return len([x for x in p.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()])

assessment = latest_jsonl("logs/v12_9/assessment_chamber/assessment_events.jsonl")
audio = latest_jsonl("logs/v12_9/audio_search/audio_cycle_events.jsonl")
rune = latest_jsonl("logs/v12_9/glyphic_memory/rune_shape_reasoning_ledger.jsonl")
glyphic = latest_jsonl("logs/v12_9/glyphic_memory/compound_visual_memory_ledger.jsonl")
memory = latest_jsonl("logs/v12_9/visual_memory/visual_memory_ledger.jsonl")
judge = latest_jsonl("logs/v12_9/visual_memory/visual_judge_rankings.jsonl")
diff = latest_jsonl("logs/v12_9/visual_memory/visual_difference_descriptions.jsonl")

metrics = judge.get("latest_metrics") or {}
difference = diff.get("difference") or {}

summary = {
    "ts": time.time(),
    "version": "v12.9au_full_audio_visual_rune_cycle",
    "status": "sealed_append_only",
    "assessment_sha": assessment.get("assessment_sha256"),
    "assessment_decision": assessment.get("decision"),
    "audio_event_sha": audio.get("event_sha256"),
    "rune_event_sha": rune.get("event_sha256"),
    "glyphic_ledger_sha": glyphic.get("ledger_sha256"),
    "latest_depth": memory.get("depth") or judge.get("latest_depth"),
    "latest_svg": memory.get("svg_path") or judge.get("latest_svg"),
    "overall_organ_coherence": metrics.get("overall_organ_coherence") or metrics.get("visual_coherence"),
    "judge_improvement": judge.get("improvement"),
    "coherence_delta": judge.get("coherence_delta"),
    "difference_recommendation": diff.get("recommendation"),
    "meaning_shift": difference.get("meaning_shift"),
    "stable_symbols": difference.get("stable_symbols"),
    "removed_symbols": difference.get("removed_symbols"),
    "audio_entries": count_jsonl("logs/v12_9/audio_search/audio_phonetic_compounding_ledger.jsonl"),
    "rune_entries": count_jsonl("logs/v12_9/glyphic_memory/rune_shape_reasoning_ledger.jsonl"),
    "glyphic_entries": count_jsonl("logs/v12_9/glyphic_memory/compound_visual_memory_ledger.jsonl"),
    "law": "audio_visual_rune_and_vl_memory_compounded_through_reflective_assessment",
}

raw = json.dumps(summary, sort_keys=True, ensure_ascii=False).encode("utf-8")
summary["event_sha256"] = hashlib.sha256(raw).hexdigest()[:16]

Path("logs/v12_9/cross_modal").mkdir(parents=True, exist_ok=True)
with Path("logs/v12_9/cross_modal/v129au_cross_modal_cycle_events.jsonl").open("a", encoding="utf-8") as f:
    f.write(json.dumps(summary, ensure_ascii=False) + "\n")

print(json.dumps(summary, indent=2, ensure_ascii=False))
PY

