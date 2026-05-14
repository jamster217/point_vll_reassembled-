from __future__ import annotations

import json
import py_compile
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

REPORT_JSON = Path("reports/phase3m/brain_cognition_temporal_audit.json")
REPORT_TXT = Path("reports/phase3m/brain_cognition_temporal_audit.txt")

KEY_MODULES = {
    "brain_temporal_observer": "runtime/brain_temporal_observer.py",
    "unified_drift_kernel": "runtime/unified_drift_kernel.py",
    "micro_context_drift": "runtime/micro_context_drift.py",
    "retrieval_injection": "runtime/retrieval_injection.py",
    "timeline_gate_lattice": "runtime/timeline_gate_lattice.py",
    "spiral_full": "runtime/spiral_full.py",
    "knowledge_node": "runtime/knowledge_node.py",
    "recursive_mirror_prompt": "runtime/recursive_mirror_prompt.py",
    "node_44_preset": "runtime/node_44_preset.py",
    "unified_voice": "runtime/unified_voice.py",
}

SEARCH_TERMS = [
    "brain", "cognition", "cognitive", "temporal", "timeline",
    "memory", "observer", "drift", "recursion", "recursive",
    "mirror", "node44", "node_44", "spiral"
]

BAD_PUBLIC_LEAKS = [
    "message_sha256", "answer_sha256", "retrieval_context",
    "shape_field", "quantum_pulse", "bridge_meta", "vectors", "tokens"
]

def now():
    return datetime.now(timezone.utc).isoformat()

def compile_file(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"exists": False, "compiled": False, "error": "missing"}

    try:
        py_compile.compile(str(p), doraise=True)
        return {"exists": True, "compiled": True, "error": ""}
    except Exception as e:
        return {"exists": True, "compiled": False, "error": str(e)}

def discover_related_files() -> list[str]:
    found = []
    roots = [Path("runtime"), Path("core"), Path("kernel")]
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            parts = set(p.parts)
            if "__pycache__" in parts or "bak" in parts or "broken" in parts:
                continue
            low = str(p).lower()
            if any(term in low for term in SEARCH_TERMS):
                found.append(str(p))
    return sorted(set(found))

def cmd_probe(name: str, cmd: list[str], timeout: int = 60) -> dict:
    try:
        cp = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        return {
            "name": name,
            "ok": cp.returncode == 0,
            "returncode": cp.returncode,
            "stdout": cp.stdout[-1000:],
            "stderr": cp.stderr[-1000:],
        }
    except Exception as e:
        return {"name": name, "ok": False, "error": str(e)}

def api_probe() -> dict:
    prompt = (
        "Phase 3M brain cognition temporal audit. "
        "Explain how the brain, cognition, temporal observer, memory, recursion, Node44, "
        "and Universal Larynx should work together as clean visible English. "
        "Do not expose internal machinery."
    )

    payload = {
        "message": prompt,
        "controller_detail": False,
        "answer_mode": "full",
    }

    req = urllib.request.Request(
        "http://127.0.0.1:5055/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as e:
        return {"ok": False, "clean": False, "error": str(e), "keys": [], "answer": ""}

    blob = json.dumps(data).lower()
    leaks = [x for x in BAD_PUBLIC_LEAKS if x.lower() in blob]

    return {
        "ok": bool(data.get("ok")),
        "keys": sorted(data.keys()),
        "clean": sorted(data.keys()) == ["answer", "answer_mode", "ok"] and not leaks,
        "leaks": leaks,
        "answer": str(data.get("answer", "")),
    }

def main():
    key_status = {name: compile_file(path) | {"path": path} for name, path in KEY_MODULES.items()}

    related_files = discover_related_files()
    related_compile = {}
    for path in related_files:
        related_compile[path] = compile_file(path)

    probes = [
        cmd_probe(
            "knowledge_node_create",
            ["python", "-c", "from runtime.knowledge_node import KnowledgeNode; n=KnowledgeNode.new('concept','temporal cognition','source'); print(n.node_type, n.status)"]
        ),
        cmd_probe(
            "recursive_mirror_prompt",
            ["python", "-c", "from runtime.recursive_mirror_prompt import get_recursive_mirror_prompt; p=get_recursive_mirror_prompt(); print(p.splitlines()[0], len(p))"]
        ),
        cmd_probe(
            "node44_config",
            ["python", "-c", "from runtime.node_44_preset import get_node_44_config; c=get_node_44_config(); print(c.get('node_id'), c.get('dominant_attractor'))"]
        ),
    ]

    api = api_probe()

    key_ok = all(v["exists"] and v["compiled"] for v in key_status.values())
    related_ok = all(v["compiled"] for v in related_compile.values())
    probes_ok = all(p.get("ok") for p in probes)
    api_ok = api.get("ok") and api.get("clean")

    final_pass = bool(key_ok and related_ok and probes_ok and api_ok)

    report = {
        "ts": now(),
        "kind": "phase3m_brain_cognition_temporal_audit",
        "final_pass": final_pass,
        "key_status": key_status,
        "related_files": related_files,
        "related_compile": related_compile,
        "probes": probes,
        "api_probe": api,
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("PHASE 3M — BRAIN / COGNITION / TEMPORAL AUDIT")
    lines.append("=" * 72)
    lines.append(f"final_pass: {final_pass}")
    lines.append("")

    lines.append("KEY MODULES")
    for name, st in key_status.items():
        mark = "✅" if st["exists"] and st["compiled"] else "❌"
        lines.append(f"  {mark} {name}: {st['path']}")
        if st.get("error"):
            lines.append(f"      error: {st['error']}")

    lines.append("")
    lines.append(f"RELATED FILES FOUND: {len(related_files)}")
    bad_related = [p for p, st in related_compile.items() if not st["compiled"]]
    if bad_related:
        for p in bad_related:
            lines.append(f"  ❌ {p}: {related_compile[p]['error']}")
    else:
        lines.append("  ✅ all related active files compiled")

    lines.append("")
    lines.append("PROBES")
    for p in probes:
        lines.append(f"  {'✅' if p.get('ok') else '❌'} {p.get('name')}")
        if p.get("stdout"):
            lines.append("      stdout: " + p["stdout"].replace("\n", " ")[:500])
        if p.get("stderr"):
            lines.append("      stderr: " + p["stderr"].replace("\n", " ")[:500])
        if p.get("error"):
            lines.append("      error: " + p["error"])

    lines.append("")
    lines.append("API PROBE")
    lines.append(f"  ok: {api.get('ok')}")
    lines.append(f"  keys: {api.get('keys')}")
    lines.append(f"  clean: {api.get('clean')}")
    if api.get("error"):
        lines.append(f"  error: {api.get('error')}")
    lines.append(f"  answer: {api.get('answer')}")

    REPORT_TXT.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    print()
    print("saved:", REPORT_JSON)
    print("saved:", REPORT_TXT)

if __name__ == "__main__":
    main()
