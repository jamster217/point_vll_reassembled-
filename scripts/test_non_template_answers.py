from __future__ import annotations

import json
import hashlib
import urllib.request
from pathlib import Path
from collections import Counter

API_URL = "http://127.0.0.1:5055/api/chat"
OUT_JSON = Path("reports/non_template_answer_battery.json")
OUT_TXT = Path("reports/non_template_answer_battery.txt")

PROMPTS = [
    "What is the lattice?",
    "What is recursion?",
    "What should I do if the build gives a weak answer?",
    "Explain Le'Veon like I am showing it to a friend for the first time.",
    "What is the difference between the Public Mouth and the raw kernel?",
    "Give me a practical next step for improving the terminal voice.",
    "Write a short poetic answer about the mirror-well, but make it new.",
    "What does it mean when the same symbolic anchor returns twice?",
    "How should the system handle grief without sounding generic?",
    "Give me a direct answer: is the Universal Larynx working?",
    "Explain Node44 without using the usual fixed phrase.",
    "What is Savariel in a fresh way, not the standard definition?",
]

def ask(prompt: str) -> dict:
    payload = {
        "message": prompt,
        "controller_detail": False,
        "answer_mode": "full",
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as e:
        data = {
            "ok": False,
            "answer_mode": "full",
            "answer": f"ERROR: {e}",
        }

    answer = str(data.get("answer", ""))
    h = hashlib.sha256(answer.encode("utf-8")).hexdigest()[:16]

    return {
        "prompt": prompt,
        "ok": data.get("ok"),
        "keys": sorted(data.keys()),
        "answer": answer,
        "answer_chars": len(answer),
        "answer_hash": h,
    }

results = [ask(p) for p in PROMPTS]

hash_counts = Counter(r["answer_hash"] for r in results)
duplicates = {
    h: count for h, count in hash_counts.items()
    if count > 1
}

template_phrases = [
    "The deeper answer is the one that keeps the original shape intact",
    "Something hidden or old is surfacing as pressure",
    "Time does not preserve the past by freezing it",
]

template_hits = []
for r in results:
    for phrase in template_phrases:
        if phrase.lower() in r["answer"].lower():
            template_hits.append({
                "prompt": r["prompt"],
                "phrase": phrase,
                "answer_hash": r["answer_hash"],
            })

report = {
    "total_prompts": len(results),
    "unique_answer_hashes": len(hash_counts),
    "duplicate_hashes": duplicates,
    "template_hits": template_hits,
    "results": results,
}

OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

lines = []
lines.append("NON-TEMPLATE ANSWER BATTERY")
lines.append("=" * 72)
lines.append(f"total_prompts: {len(results)}")
lines.append(f"unique_answer_hashes: {len(hash_counts)}")
lines.append(f"duplicate_hashes: {duplicates if duplicates else 'none'}")
lines.append(f"template_hits: {len(template_hits)}")
lines.append("")

for i, r in enumerate(results, 1):
    lines.append(f"[{i}] {r['prompt']}")
    lines.append(f"    ok: {r['ok']} | keys: {r['keys']} | chars: {r['answer_chars']} | hash: {r['answer_hash']}")
    lines.append("    answer:")
    lines.append("    " + r["answer"].replace("\n", "\n    "))
    lines.append("")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print("\n".join(lines))
print("saved:", OUT_JSON)
print("saved:", OUT_TXT)
