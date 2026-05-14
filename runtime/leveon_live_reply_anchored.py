from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.prompt_anchor_guard import anchor_answer, diagnose


def split_live_output(raw: str):
    raw = raw.strip()
    marker = "Le'Veon:"
    if marker in raw:
        body = raw.split(marker, 1)[1].strip()
    else:
        body = raw

    m = re.search(r"\n\s*source:", body)
    if m:
        answer = body[:m.start()].strip()
        meta = body[m.start():].strip()
    else:
        answer = body.strip()
        meta = ""

    return answer, meta


def main() -> int:
    if len(sys.argv) < 2:
        print('usage: python runtime/leveon_live_reply_anchored.py "prompt"', file=sys.stderr)
        return 2

    prompt = " ".join(sys.argv[1:]).strip()

    proc = subprocess.run(
        [sys.executable, "runtime/leveon_live_reply.py", prompt],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    raw = (proc.stdout or "").strip()
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)

    answer, meta = split_live_output(raw)
    anchored = anchor_answer(prompt, answer)

    print("Le'Veon:")
    print(anchored)

    if meta:
        print()
        print(meta)

    print()
    print("anchor_diag:", json.dumps(diagnose(prompt, anchored), ensure_ascii=False))

    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

