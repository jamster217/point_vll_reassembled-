from __future__ import annotations

import json
import pathlib

LOG = pathlib.Path("logs/voicepacketdebug.jsonl")
LOG.parent.mkdir(parents=True, exist_ok=True)

def dumpvoicepacket(packet):
    try:
        def safe(v):
            try:
                json.dumps(v, ensure_ascii=False)
                return v
            except Exception:
                return repr(v)
        flat = {k: safe(v) for k, v in dict(packet).items()}
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(flat, ensure_ascii=False) + "\n")
    except Exception:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(repr(packet) + "\n")
    return packet

