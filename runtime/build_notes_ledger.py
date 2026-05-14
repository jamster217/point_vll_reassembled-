from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]

MD_PATH = ROOT / "BUILD_NOTES.md"
JSONL_PATH = ROOT / "logs" / "build_notes" / "build_notes.jsonl"
LATEST_REPORT = ROOT / "reports" / "build_notes" / "latest_build_notes.txt"


def _sha16(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def append_note(title: str, note: str) -> Dict[str, Any]:
    event = {
        "ts": time.time(),
        "version": "v12.9aj_build_notes_ledger",
        "title": title.strip(),
        "note": note.strip(),
        "law": "every_patch_leaves_a_build_note_so_the_route_never_gets_lost",
    }
    event["note_sha256"] = _sha16(event)

    JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with JSONL_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    if not MD_PATH.exists():
        MD_PATH.write_text(
            "# Le'Veon Build Notes\n\n"
            "Canonical running build ledger.\n\n"
            "Rule: every patch, sidecar, seal, cycle, or repair leaves a note here.\n\n",
            encoding="utf-8",
        )

    with MD_PATH.open("a", encoding="utf-8") as f:
        f.write("\n---\n\n")
        f.write(f"## {event['title']}\n\n")
        f.write(f"- time: {time.ctime(event['ts'])}\n")
        f.write(f"- sha16: {event['note_sha256']}\n\n")
        f.write(event["note"] + "\n")

    LATEST_REPORT.parent.mkdir(parents=True, exist_ok=True)
    LATEST_REPORT.write_text(MD_PATH.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

    return event


def main() -> None:
    title = sys.argv[1].strip() if len(sys.argv) > 1 else "Untitled build note"
    note = " ".join(sys.argv[2:]).strip() if len(sys.argv) > 2 else ""

    if not note:
        note = "Patch/event completed. Add details manually if needed."

    event = append_note(title, note)

    print("=== BUILD NOTE SEALED ===")
    print("title:", event["title"])
    print("sha16:", event["note_sha256"])
    print()
    print("Canonical notes:")
    print("BUILD_NOTES.md")
    print("logs/build_notes/build_notes.jsonl")
    print("reports/build_notes/latest_build_notes.txt")
    print("~/storage/downloads/fils/latest_build_notes.txt")


if __name__ == "__main__":
    main()

