#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import hashlib
import urllib.request
from pathlib import Path
from datetime import datetime


ROOT = Path(".")
OUT = Path("logs/watcher/sovereign_watcher_24h.jsonl")
SUMMARY = Path("reports/watcher/sovereign_watcher_latest.json")
INTERVAL_SECONDS = 300
DURATION_SECONDS = 24 * 60 * 60

WATCH_ROOTS = [
    Path("app_chatroom.py"),
    Path("watcher.py"),
    Path("runtime"),
    Path("core"),
    Path("kernel"),
    Path("config"),
    Path("templates"),
]

SKIP_PARTS = {
    "__pycache__", "bak", "broken"
}

SOURCE_SUFFIXES = {".py", ".json", ".html"}


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    try:
        h.update(path.read_bytes())
        return h.hexdigest()
    except Exception:
        return ""


def source_manifest() -> dict:
    files = []

    for root in WATCH_ROOTS:
        if not root.exists():
            continue

        paths = [root] if root.is_file() else list(root.rglob("*"))

        for p in paths:
            if not p.is_file():
                continue
            if p.suffix not in SOURCE_SUFFIXES:
                continue
            if any(part in SKIP_PARTS for part in p.parts):
                continue

            try:
                st = p.stat()
                files.append({
                    "path": p.as_posix(),
                    "mtime": st.st_mtime,
                    "size": st.st_size,
                    "sha256": file_hash(p),
                })
            except Exception:
                pass

    files.sort(key=lambda x: x["path"])
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()

    return {
        "file_count": len(files),
        "digest": digest,
        "files": files,
    }


def api_probe() -> dict:
    payload = json.dumps({
        "message": "Deep Braid status. Is the registry active?",
        "controller_detail": False,
        "answer_mode": "full",
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:5055/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", errors="replace"))

        keys = sorted(data.keys())
        clean = set(keys).issubset({"ok", "answer", "answer_mode"})
        answer = data.get("answer", "")

        return {
            "ok": bool(data.get("ok")),
            "keys": keys,
            "clean": clean,
            "answer_chars": len(answer),
            "answer_preview": answer[:180],
        }
    except Exception as e:
        return {
            "ok": False,
            "clean": False,
            "error": repr(e),
        }


def ledger_status() -> dict:
    p = Path("var/live_adaptation_pulses.jsonl")
    if not p.exists():
        return {"exists": False, "line_count": 0}

    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    recent = []

    for line in lines[-10:]:
        try:
            recent.append(json.loads(line))
        except Exception:
            pass

    return {
        "exists": True,
        "line_count": len(lines),
        "recent_algorithms": [r.get("selected_algorithm") for r in recent],
        "recent_public_scrub": [r.get("public_scrub") for r in recent],
        "recent_estimated_n": [(r.get("density") or {}).get("estimated_n") for r in recent],
    }


def sovereign_state() -> dict:
    p = Path("var/exponential_sovereign_state.json")
    if not p.exists():
        return {"exists": False}

    try:
        data = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        return {"exists": True, "parse_error": repr(e)}

    return {
        "exists": True,
        "timestamp": data.get("timestamp"),
        "generation": data.get("generation"),
        "status": data.get("status"),
        "mode": data.get("mode"),
        "multiplier": data.get("multiplier"),
    }


def append_record(record: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    start = time.time()
    initial_manifest = source_manifest()
    initial_digest = initial_manifest["digest"]

    while True:
        elapsed = time.time() - start
        manifest = source_manifest()

        record = {
            "ts": time.time(),
            "iso": now_iso(),
            "kind": "sovereign_watcher_pulse",
            "elapsed_seconds": round(elapsed, 2),
            "watch_duration_seconds": DURATION_SECONDS,
            "source_body": {
                "file_count": manifest["file_count"],
                "digest": manifest["digest"],
                "changed_since_start": manifest["digest"] != initial_digest,
            },
            "api_probe": api_probe(),
            "ledger": ledger_status(),
            "sovereign_state": sovereign_state(),
            "law": "observe only; do not mutate source",
        }

        append_record(record)

        print(
            "[SOVEREIGN WATCHER]",
            record["iso"],
            "api_ok=" + str(record["api_probe"].get("ok")),
            "clean=" + str(record["api_probe"].get("clean")),
            "ledger_lines=" + str(record["ledger"].get("line_count")),
            "source_changed=" + str(record["source_body"].get("changed_since_start")),
            flush=True,
        )

        if elapsed >= DURATION_SECONDS:
            break

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
