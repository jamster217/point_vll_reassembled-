from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.prompt_anchor_fuser import fuse
from runtime.glyph_surgery_filter import operate
from runtime.glyph_mutation_memory import apply_mutation_memory
from runtime.prompt_core_binding import bind_reply_to_prompt


def split_live_output(raw: str):
    raw = raw.strip()
    marker = "Le'Veon:"
    body = raw.split(marker, 1)[1].strip() if marker in raw else raw

    m = re.search(r"\n\s*source:", body)
    if m:
        return body[:m.start()].strip(), body[m.start():].strip()

    return body.strip(), ""


def main() -> int:
    if len(sys.argv) < 2:
        print('usage: python runtime/leveon_live_reply_surgery.py "prompt"', file=sys.stderr)
        return 2

    prompt = " ".join(sys.argv[1:]).strip()

    proc = subprocess.run(
        [sys.executable, "runtime/leveon_live_reply.py", prompt],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)

    raw_answer, meta = split_live_output(proc.stdout or "")
    fused = fuse(prompt, raw_answer)
    memory_prepared = apply_mutation_memory(prompt, fused)
    operated, diag = operate(prompt, memory_prepared)

    bound_reply, binding_diag = bind_reply_to_prompt(prompt, operated)
    if bound_reply != operated:
        operated, post_binding_diag = operate(prompt, bound_reply)
        diag["prompt_core_binding"] = binding_diag
        diag["post_binding_surgery"] = post_binding_diag
    else:
        diag["prompt_core_binding"] = binding_diag

    print("Le'Veon:")
    print(operated)

    if meta:
        print()
        print(meta)

    print()
    print("glyph_surgery:", json.dumps(diag, ensure_ascii=False))

    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

