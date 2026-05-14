#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from runtime.packet_validator import validate_spiral


def validate_file(path: str) -> int:
    failures = 0
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                pkt = json.loads(line)
            except Exception as e:
                print(f"{lineno}: PARSE_ERROR {e}")
                failures += 1
                continue
            ok, msg = validate_spiral(pkt)
            status = "OK" if ok else f"FAIL:{msg}"
            print(f"{lineno}: {status}")
            if not ok:
                failures += 1
    return failures


def validate_single(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        pkt = json.load(f)
    ok, msg = validate_spiral(pkt)
    print("VALID" if ok else f"INVALID: {msg}")
    return 0 if ok else 1


def detect_mode(path: str) -> str:
    if path.endswith(".jsonl"):
        return "jsonl"
    if path.endswith(".json"):
        return "json"

    nonempty = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                nonempty.append(s)
            if len(nonempty) >= 2:
                break

    if len(nonempty) >= 2:
        return "jsonl"
    return "json"


def main() -> None:
    p = argparse.ArgumentParser(description="Validate spiral_out packets (JSON or JSONL)")
    p.add_argument("path", help="Path to packet.json or packets.jsonl")
    args = p.parse_args()

    mode = detect_mode(args.path)
    if mode == "json":
        raise SystemExit(validate_single(args.path))
    raise SystemExit(validate_file(args.path))


if __name__ == "__main__":
    main()

