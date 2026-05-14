#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

url = "http://127.0.0.1:5055/api/chat"

core = """
Long-Range Echo Test.
Enter Node44. Stabilize the core_knot.
Explain how the Deep Braid, Live Adaptation Pulse Ledger, Performance Oracle, public scrub, Visual Cockpit, Recursive Mirror, Watcher Mode, clean mouth, source body stability, and dense symbolic routing work together over a long-range symbolic payload.

Keep visible English clean.
Do not expose private metadata.
Do not include logs, hashes, vectors, tokens, endpoints, JSON internals, or debug scaffolding.
Answer as a clear public-facing explanation.

Symbolic density:
Node44, core_knot, Algorithm C, Performance Oracle, prompt density, live adaptation pulse ledger, public scrub, clean mouth, sealed braid, recursive mirror, visual cockpit, hidden machinery, runtime pulse, source stable, watcher mode, sovereign handover, lattice, memory, signal, containment, bloom, reflective core, deep braid registry.
"""

message = (core + "\n") * 12

payload = json.dumps({
    "message": message,
    "controller_detail": False,
    "answer_mode": "full"
}).encode("utf-8")

req = urllib.request.Request(
    url,
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(req, timeout=90) as r:
    body = r.read().decode("utf-8", errors="replace")

Path("reports/long_range_echo_probe.json").write_text(body, encoding="utf-8")

print("saved: reports/long_range_echo_probe.json")
print(body[:2500])
