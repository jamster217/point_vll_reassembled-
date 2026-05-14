#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from pathlib import Path

trace = json.loads(Path("replication_trace_4200.json").read_text(encoding="utf-8"))

state_modes = Counter()
motifs = Counter()
mode_by_state = defaultdict(Counter)
commit_by_state = defaultdict(Counter)

for t in trace:
    state = (t.get("coherence_field") or {}).get("state_tag", "unknown")
    mode = (t.get("ulat_projection") or {}).get("mode", "unknown")
    commit = bool((t.get("commit") or {}).get("can_commit"))
    state_modes[(state, mode)] += 1
    mode_by_state[state][mode] += 1
    commit_by_state[state]["commit" if commit else "block"] += 1

    for m in (t.get("motifs_and_knowledge") or {}).get("top_motifs", []):
        motifs[m.get("motif", "unknown")] += int(m.get("weight", 1) or 1)

law_bank = {
    "source": "replication_trace_4200.json",
    "total_turns": len(trace),
    "state_laws": {
        "fragile": {
            "surface_rule": "observe before expansion",
            "voice_rule": "short, grounded, low abstraction",
            "risk_rule": "do not amplify novelty",
        },
        "adaptive": {
            "surface_rule": "stabilize then open one layer",
            "voice_rule": "surface + deeper layer + structural read",
            "risk_rule": "allow novelty only after boundary holds",
        },
        "stable": {
            "surface_rule": "expand with controlled density",
            "voice_rule": "living language allowed, but no scaffold leak",
            "risk_rule": "preserve shape while increasing richness",
        },
    },
    "mode_laws": {
        "observe": "name what is present without forcing transformation",
        "stabilize": "hold the shape until the relation is clear",
        "expand": "render the formed shape into richer language",
    },
    "motif_bias": motifs.most_common(20),
    "mode_by_state": {k: dict(v) for k, v in mode_by_state.items()},
    "commit_by_state": {k: dict(v) for k, v in commit_by_state.items()},
    "renderer_warning": {
        "unique_outputs_problem": "trace has rich state but collapsed final English diversity",
        "law": "do not copy trace final_english_output directly; use trace only for state laws",
    },
}

Path("runtime/generated/trace_law_bank.json").write_text(
    json.dumps(law_bank, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("wrote runtime/generated/trace_law_bank.json")
print(json.dumps({
    "total_turns": law_bank["total_turns"],
    "mode_by_state": law_bank["mode_by_state"],
    "commit_by_state": law_bank["commit_by_state"],
    "top_motifs": law_bank["motif_bias"][:8],
}, indent=2, ensure_ascii=False))
