#!/usr/bin/env python3
"""
Backfill old SGE logs with shape signatures, deltas, and voice_source.
"""

from __future__ import annotations

import json
import shutil
import datetime
from pathlib import Path

from runtime.shape_signature import shape_signature
from runtime.shape_delta import shape_delta


LOG_PATH = Path("logs/sge_turns.jsonl")


def main():
    if not LOG_PATH.exists():
        print("no log found:", LOG_PATH)
        return

    backup = LOG_PATH.with_suffix(
        ".jsonl.bak_backfill_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    shutil.copy2(LOG_PATH, backup)

    rows = []
    changed = 0

    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                row = json.loads(line)
            except Exception:
                continue

            shape_in = row.get("shape_in") or {}
            shape_out = row.get("shape_out") or shape_in

            if row.get("shape_signature_in") in (None, "", "unknown"):
                row["shape_signature_in"] = shape_signature(shape_in)
                changed += 1

            if row.get("shape_signature_out") in (None, "", "unknown"):
                row["shape_signature_out"] = shape_signature(shape_out)
                changed += 1

            if "shape_delta" not in row:
                row["shape_delta"] = shape_delta(shape_in, shape_out)
                changed += 1

            if "voice_source" not in row:
                row["voice_source"] = "legacy_unknown"
                changed += 1

            rows.append(row)

    with LOG_PATH.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"backfilled rows: {len(rows)}")
    print(f"fields changed : {changed}")
    print(f"backup written : {backup}")


if __name__ == "__main__":
    main()

