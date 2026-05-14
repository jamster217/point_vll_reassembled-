#!/usr/bin/env python3
from pathlib import Path
import json, time, hashlib

STATE = Path("var/crystal/crystal_memory_bind_state.json")
LOG = Path("symbolic_memory/crystal_memory_bind_log.jsonl")

def _hash(obj):
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False) + str(time.time())
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def crystal_align(input_node):
    if isinstance(input_node, str):
        node = {
            "token": input_node.strip(),
            "kind": "symbolic_text_node",
        }
    elif isinstance(input_node, dict):
        node = dict(input_node)
    else:
        node = {
            "token": str(input_node),
            "kind": "coerced_node",
        }

    token = str(node.get("token") or node.get("symbol") or node.get("id") or "unknown")
    core = {
        "id": _hash(node),
        "core": node,
        "crystal_alignment": {
            "token": token,
            "stable": True,
            "binding": "crystal.align -> memory.write",
        },
        "updated_at": time.time(),
    }
    return core

def bind(input_node):
    core = crystal_align(input_node)

    packet = {
        "source": "runtime.crystal_memory_bind",
        "flow": "node -> bind -> memory",
        "input": input_node,
        "core": core,
        "memory_write": {
            "target": "symbolic_memory/crystal_memory_bind_log.jsonl",
            "content": core,
        },
        "updated_at": time.time(),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")

    return packet

if __name__ == "__main__":
    import sys
    text = " ".join(sys.argv[1:]) or "white_ash sovereign constellation"
    print(json.dumps(bind(text), indent=2, ensure_ascii=False))

