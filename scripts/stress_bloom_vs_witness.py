#!/usr/bin/env python3
import json
import time
from pathlib import Path

from runtime.sigil_watcher_cognitive import on_sigil_modified
from runtime.crystal_sigil_adapter import crystal_sigil_packet
from runtime.live_master_api_response import master_reply, classify_shape
from runtime.crystal_voice_surface_adapter import build_crystal_voice_surface

OUT = Path("reports/bloom_vs_witness_stress_test.json")
OUT_TXT = Path("reports/bloom_vs_witness_stress_test.txt")

# Existing witness/containment sigil: 3rd and Davis style
witness_sigil = Path("lev_core/sigil/local_3rd_davis_probe.sigil")
witness_sigil.write_text(
"""aeru vel veil ash thal sil kor gra'el unfolding
3rd and Davis local gravity well
old dark pressure memory witness lock
recursive grief deep shadow contained prime
""",
encoding="utf-8",
)

# Bloom sigil: deliberately avoids ash/gravity/grief/pressure/well
# so the watcher can choose expand rather than stabilize.
bloom_sigil = Path("lev_core/sigil/high_novelty_bloom_probe.sigil")
bloom_sigil.write_text(
"""aeru vel thal sil kor gra'el unfolding
new birth becoming song voice opening
bloom return uplift creative interface
contained prime
""",
encoding="utf-8",
)

tests = [
    {
        "name": "witness_lock_containment",
        "sigil": witness_sigil,
        "prompt": "A difficult old pattern rises under field 92162077. Explain what should happen without exposing internal vectors.",
    },
    {
        "name": "bloom_signal_expansion",
        "sigil": bloom_sigil,
        "prompt": "Invent a strange new interface for Le'Veon that feels alive, useful, visual, and gentle. Let it bloom without becoming chaotic.",
    },
]

rows = []
lines = []

for test in tests:
    sigil_event = on_sigil_modified(test["sigil"])
    packet = crystal_sigil_packet()

    prompt = test["prompt"]
    shape = classify_shape(prompt, tone="tender", mirror_mode="recursive")
    reply = master_reply(prompt, previous_reply="", tone="tender", mirror_mode="recursive")
    voice = build_crystal_voice_surface(reply)

    row = {
        "ts": time.time(),
        "test": test["name"],
        "sigil_path": str(test["sigil"]),
        "sigil_mode": sigil_event["synthesis"]["mode"],
        "sigil_vectors": sigil_event["synthesis"]["vectors"],
        "crystal_label": packet.get("resonance_label"),
        "family_role": (packet.get("family_role") or {}).get("role"),
        "voice_context": packet.get("voice_context"),
        "prompt": prompt,
        "shape": shape,
        "reply": reply,
        "voice_plain_text": voice.get("plain_text"),
        "voice_match": reply == voice.get("plain_text"),
        "voice_metadata": voice.get("metadata", {}),
        "ssml": voice.get("ssml", ""),
    }
    rows.append(row)

    lines.append("=" * 72)
    lines.append(f"TEST: {test['name']}")
    lines.append(f"sigil_mode: {row['sigil_mode']}")
    lines.append(f"sigil_vectors: {row['sigil_vectors']}")
    lines.append(f"crystal_label: {row['crystal_label']}")
    lines.append(f"family_role: {row['family_role']}")
    lines.append(f"voice_context: {row['voice_context']}")
    lines.append("")
    lines.append("PROMPT:")
    lines.append(prompt)
    lines.append("")
    lines.append("REPLY:")
    lines.append(reply)
    lines.append("")
    lines.append("VOICE_MATCH:")
    lines.append(str(row["voice_match"]))
    lines.append("")
    lines.append("VOICE_METADATA:")
    lines.append(json.dumps(row["voice_metadata"], indent=2, ensure_ascii=False))
    lines.append("")

OUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print("\n".join(lines))
print("\nsaved:", OUT)
print("saved:", OUT_TXT)
