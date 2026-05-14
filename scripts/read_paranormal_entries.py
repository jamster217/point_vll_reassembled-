from __future__ import annotations

import json
import sys
from pathlib import Path

RAW = Path("reports/v12_9/paranormal_tab/readouts/latest_structured_feed.json")

def load_feed():
    if not RAW.exists():
        raise SystemExit(f"Missing feed file: {RAW}")
    return json.loads(RAW.read_text(encoding="utf-8", errors="replace"))

def source_line(entry):
    path = Path(entry.get("file", ""))
    idx = entry.get("line_index")

    if not path.exists():
        return None, f"missing source file: {path}"

    try:
        idx = int(idx)
    except Exception:
        return None, f"bad line_index: {idx}"

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    if idx < 0 or idx >= len(lines):
        return None, f"line_index out of range: {idx} for {path}"

    return lines[idx], None

def show_list(feed):
    entries = feed.get("entries") or []
    print(f"feed_version: {feed.get('version')}")
    print(f"entry_count: {len(entries)}")
    print()

    for i, e in enumerate(entries):
        print(
            f"[{i}] "
            f"file={e.get('file')} "
            f"line={e.get('line_index')} "
            f"version={e.get('version')} "
            f"status={e.get('status')} "
            f"ghost_id={e.get('ghost_id')} "
            f"tone={e.get('tone')}"
        )

def show_entry(feed, idx):
    entries = feed.get("entries") or []
    if idx < 0 or idx >= len(entries):
        raise SystemExit(f"Index out of range: {idx}; max is {len(entries)-1}")

    e = entries[idx]

    print("=== FEED ENTRY SUMMARY ===")
    print(json.dumps(e, ensure_ascii=False, indent=2, sort_keys=True))
    print()

    line, err = source_line(e)
    print("=== ORIGINAL SOURCE ENTRY ===")
    if err:
        print("ERROR:", err)
        return

    try:
        obj = json.loads(line)
        print(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True))
    except Exception:
        print(line)

def dump_all(feed):
    entries = feed.get("entries") or []
    full = []

    for i, e in enumerate(entries):
        line, err = source_line(e)
        item = {
            "feed_index": i,
            "feed_entry": e,
            "source_error": err,
            "source_entry": None,
            "source_raw": None,
        }

        if line is not None:
            try:
                item["source_entry"] = json.loads(line)
            except Exception:
                item["source_raw"] = line

        full.append(item)

    out = Path("reports/v12_9/paranormal_tab/readouts/full_original_entries.json")
    out.write_text(json.dumps(full, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print("WROTE:", out)

def main():
    feed = load_feed()

    if len(sys.argv) == 1 or sys.argv[1] in ("list", "ls"):
        show_list(feed)
        return

    if sys.argv[1] == "all":
        dump_all(feed)
        return

    try:
        idx = int(sys.argv[1])
    except Exception:
        raise SystemExit("Usage: python scripts/read_paranormal_entries.py [list|all|ENTRY_INDEX]")

    show_entry(feed, idx)

if __name__ == "__main__":
    main()
