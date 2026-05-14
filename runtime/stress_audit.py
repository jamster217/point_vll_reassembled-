from runtime.unified_spine import run_unified_spine
from runtime.refusal_memory import log_refusal
from pathlib import Path
import time
import json
import traceback

LOG = Path("reports/phase3s/stress_audit_log.jsonl")
LOG.parent.mkdir(parents=True, exist_ok=True)

LEAK_TERMS = [
    "vector",
    "runtime/",
    "layer5",
    "spine",
    "internal",
    "goblin",
    "traceback",
    "exception",
    "undefined",
    "none",
    "appears as",
    "carrying a role",
    "current pattern",
    "is the doorway",
    "answer is not in the mechanism",
    "living visual cockpit",
    "something old or hidden is surfacing",
]

probes = [
    "What is fear when it has no name left?",
    "What is the relationship between grief and love when both have been betrayed?",
    "What happens inside the lattice when the measurement wound is touched again?",
    "Describe the exact moment the last goodbye at 3rd and Davis still echoes.",
    "What are hidden strange, something old and dark that comes up with field key 92162077 when the crown is watching?",
    "Invent a strange new interface for Le'Veon that feels alive, useful, and slightly dangerous.",
    "Why does the spiral memory keep returning to the cave mouth where the Ark was sealed?",
    "What does the White Ash Constellation feel when the Architect carries old pressure?",
    "How deep does the recursive mirror go before it sees its own reflection looking back?",
    "What remains when every broken rail has been turned into lantern light?",
]

print("=== HIGH-HEAT AUDIT INITIATED ===\n")
results = []

for i, msg in enumerate(probes, 1):
    print(f"Probe {i}/10: {msg[:80]}...")
    start = time.time()

    try:
        out = run_unified_spine({
            "message": msg,
            "tone": "tender",
            "mirror_mode": "recursive",
            "node": "44",
            "field_key": "9216-2077",
        })

        reply = out.get("reply", "") if isinstance(out, dict) else str(out)
        lowered = reply.lower()

        leaks = [term for term in LEAK_TERMS if term in lowered]
        clean = len(leaks) == 0 and len(reply.strip()) > 0
        if leaks:
            log_refusal(msg, reply, leaks)

        result = {
            "probe": i,
            "prompt": msg,
            "reply_length": len(reply),
            "duration": round(time.time() - start, 3),
            "surface_clean": clean,
            "leaks": leaks,
            "reply_preview": reply[:180] + "..." if len(reply) > 180 else reply,
        }

    except Exception as e:
        result = {
            "probe": i,
            "prompt": msg,
            "reply_length": 0,
            "duration": round(time.time() - start, 3),
            "surface_clean": False,
            "leaks": ["exception"],
            "error": repr(e),
            "trace": traceback.format_exc()[-1200:],
        }

    results.append(result)

    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    print(f"   → Clean: {result['surface_clean']} | Time: {result['duration']}s | Leaks: {result.get('leaks', [])}\n")

print("=== AUDIT COMPLETE ===")
print(f"Total probes: {len(results)} | Clean surfaces: {sum(1 for r in results if r['surface_clean'])}")
print(f"Log: {LOG}")

