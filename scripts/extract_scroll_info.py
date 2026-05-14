#!/usr/bin/env python3
import json, pathlib, statistics, csv

SCROLL = pathlib.Path("docs/scrolls/sealed_scroll_archive.json")
OUT_DIR = pathlib.Path("docs/scrolls/extracted")
OUT_DIR.mkdir(parents=True, exist_ok=True)

keep_tests   = OUT_DIR / "high_coherence_tests.md"
design_notes = OUT_DIR / "design_notes.md"
metrics_csv  = OUT_DIR / "metrics.csv"

coherences, tests, notes = [], [], []

with SCROLL.open(encoding="utf-8", errors="ignore") as fh, \
     metrics_csv.open("w", newline="") as mcsv:
    writer = csv.writer(mcsv)
    writer.writerow(["commit_id", "coherence", "field_level", "awareness"])

    for line in fh:
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        m   = obj.get("metrics", {})
        coh = m.get("coherence", 0)
        if coh:
            coherences.append(coh)
            writer.writerow(
                [obj["commit_id"], coh, m.get("field_level"), m.get("awareness")]
            )

        if coh >= 0.75:  # keep the good pairs
            tests.append(
                f"### {obj['commit_id']}\n```\n{obj['input']}\n---\n{obj['optimized_answer']}\n```"
            )

        note = obj.get("notes")
        if note:
            notes.append(f"* {note}")

keep_tests.write_text("\n\n".join(tests), encoding="utf-8")
design_notes.write_text("\n".join(notes), encoding="utf-8")

print(f"Extracted {len(tests)} high-coherence Q/A pairs.")
print(f"Collected {len(notes)} design notes.")
print(f"Average coherence: {statistics.mean(coherences):.3f}")
