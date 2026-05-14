#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from pathlib import Path

trace_path = Path("replication_trace_4200.json")
out_path = Path("reports/replication_trace_4200_summary.json")

if not trace_path.exists():
    raise SystemExit("Missing replication_trace_4200.json in current folder")

data = json.loads(trace_path.read_text(encoding="utf-8"))

state_tags = Counter()
modes = Counter()
rdn_events = Counter()
motifs = Counter()
outputs = Counter()
phase_counts = Counter()

coherence_vals = []
risk_vals = []
fracture_vals = []
commit_true = 0
commit_false = 0

sample_turns = []

for t in data:
    turn = t.get("turn")
    phase = t.get("phase")
    phase_counts[str(phase)] += 1

    cf = t.get("coherence_field", {}) or {}
    dm = t.get("derived_metrics", {}) or {}
    ulat = t.get("ulat_projection", {}) or {}
    rdn = t.get("threshold_rdn", {}) or {}
    commit = t.get("commit", {}) or {}
    mk = t.get("motifs_and_knowledge", {}) or {}

    state_tags[cf.get("state_tag", "unknown")] += 1
    modes[ulat.get("mode", "unknown")] += 1
    rdn_events[str(rdn.get("rdn_event"))] += 1

    if "coherence" in dm:
        coherence_vals.append(dm["coherence"])
    if "risk" in dm:
        risk_vals.append(dm["risk"])
    if "fracture" in dm:
        fracture_vals.append(dm["fracture"])

    if commit.get("can_commit"):
        commit_true += 1
    else:
        commit_false += 1

    for m in mk.get("detected_motifs", []) or []:
        motifs[m.get("motif", "unknown")] += 1

    out = (t.get("final_english_output") or "").strip()
    if out:
        outputs[out] += 1

    if turn in {1, 10, 30, 60, 100, 140, 528, 921, 2077, 4200}:
        sample_turns.append({
            "turn": turn,
            "phase": phase,
            "shape_signature": t.get("shape_signature"),
            "derived_metrics": t.get("derived_metrics"),
            "coherence_field": t.get("coherence_field"),
            "ulat_projection": t.get("ulat_projection"),
            "threshold_rdn": t.get("threshold_rdn"),
            "commit": t.get("commit"),
            "final_english_output": t.get("final_english_output"),
        })

def avg(xs):
    return round(sum(xs) / len(xs), 4) if xs else None

summary = {
    "total_turns": len(data),
    "phase_counts": dict(phase_counts),
    "state_tags": dict(state_tags),
    "ulat_modes": dict(modes),
    "rdn_events": dict(rdn_events),
    "commit_counts": {
        "can_commit_true": commit_true,
        "can_commit_false": commit_false,
    },
    "metrics_avg": {
        "coherence": avg(coherence_vals),
        "risk": avg(risk_vals),
        "fracture": avg(fracture_vals),
    },
    "top_motifs": motifs.most_common(20),
    "top_repeated_outputs": outputs.most_common(20),
    "unique_final_outputs": len(outputs),
    "sample_turns": sample_turns,
}

out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

print("wrote:", out_path)
print(json.dumps({
    "total_turns": summary["total_turns"],
    "state_tags": summary["state_tags"],
    "ulat_modes": summary["ulat_modes"],
    "commit_counts": summary["commit_counts"],
    "metrics_avg": summary["metrics_avg"],
    "unique_final_outputs": summary["unique_final_outputs"],
    "top_repeated_outputs_first": summary["top_repeated_outputs"][:3],
}, indent=2, ensure_ascii=False))
