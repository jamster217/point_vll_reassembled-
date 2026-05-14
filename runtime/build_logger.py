from __future__ import annotations
import json, pathlib
from datetime import datetime

LOG = pathlib.Path("logs/build_history.jsonl")
LOG.parent.mkdir(parents=True, exist_ok=True)

def log_build(action, file=None, summary=None, command=None, result=None, error=None):
    entry = {
        "time": datetime.utcnow().isoformat(),
        "action": action,
        "file": file,
        "summary": summary,
        "command": command,
        "result": result,
        "error": error,
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

