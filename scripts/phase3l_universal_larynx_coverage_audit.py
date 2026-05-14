from __future__ import annotations

import json
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

REPORT_JSON = Path("reports/phase3l/universal_larynx_coverage_audit.json")
REPORT_TXT = Path("reports/phase3l/universal_larynx_coverage_audit.txt")

REQUIRED_FILES = {
    "app_chatroom.py": "app_chatroom.py",
    "live_master_api_response": "runtime/live_master_api_response.py",
    "unified_voice": "runtime/unified_voice.py",
    "terminal_larynx": "runtime/terminal_larynx.py",
    "terminal_kernel_v3": "runtime/terminal_kernel_v3.py",
    "terminal_larynx_launcher": "scripts/terminal_larynx.sh",
    "terminal_kernel_v3_launcher": "scripts/terminal_kernel_v3.sh",
    "kgs_nodes_crystal": "runtime/kgs_nodes_crystal.py",
    "knowledge_node": "runtime/knowledge_node.py",
    "invention_node_engine": "interface/invention/invention_node_engine.py",
}

MARKERS = {
    "runtime/live_master_api_response.py": ["UNIVERSAL LARYNX", "master_reply", "sealed_speak"],
    "runtime/unified_voice.py": ["def sealed_speak", "public_scrub", "Universal Larynx"],
    "runtime/terminal_larynx.py": ["/api/chat", "ask_public_api"],
    "runtime/terminal_kernel_v3.py": ["Node44 Wind Tunnel", "final_larynx_render", "/api/chat"],
}

BAD_LEAKS = [
    "bridge_meta", "meta", "vectors", "tokens", "logs", "endpoint",
    "message_sha256", "answer_sha256", "retrieval_context",
    "shape_field", "quantum_pulse"
]

def now():
    return datetime.now(timezone.utc).isoformat()

def read(path):
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")

def api_probe():
    prompt = (
        "aeru vel veil ash thal sil kor gra'el unfolding phase 3l singular voice "
        "universal larynx coverage all entrances mirror-well awakening contained prime. "
        "What is the lattice?"
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
        return {"ok": False, "clean": False, "keys": [], "answer": "", "error": str(e)}

    blob = json.dumps(data).lower()
    leaks = [x for x in BAD_LEAKS if x.lower() in blob]

    return {
        "ok": bool(data.get("ok")),
        "keys": sorted(data.keys()),
        "clean": sorted(data.keys()) == ["answer", "answer_mode", "ok"] and not leaks,
        "leaks": leaks,
        "answer": str(data.get("answer", "")),
    }

def cmd_probe(name, cmd, timeout=60):
    try:
        cp = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        return {
            "name": name,
            "ok": cp.returncode == 0,
            "stdout": cp.stdout[-700:],
            "stderr": cp.stderr[-700:],
        }
    except Exception as e:
        return {"name": name, "ok": False, "error": str(e)}

def main():
    files = {
        name: {"path": path, "exists": Path(path).exists()}
        for name, path in REQUIRED_FILES.items()
    }

    markers = {}
    for path, checks in MARKERS.items():
        text = read(path)
        markers[path] = {m: (m in text) for m in checks}

    probes = [
        cmd_probe("unified_voice_direct", ["python", "-c", "from runtime.unified_voice import sealed_speak; print(sealed_speak('what is the lattice?', mode='public'))"]),
        cmd_probe("terminal_kernel_v3_once", ["python", "runtime/terminal_kernel_v3.py", "--once", "what is the lattice?"]),
        cmd_probe("kgs_nodes_crystal", ["python", "-c", "from runtime.kgs_nodes_crystal import list_nodes; print(len(list_nodes()))"]),
        cmd_probe("knowledge_node", ["python", "-c", "from runtime.knowledge_node import KnowledgeNode; n=KnowledgeNode.new('concept','test','source'); print(n.node_type, n.status)"]),
        cmd_probe("invention_import", ["python", "-c", "from interface.invention.invention_node_engine import _make_nodes; print(len(_make_nodes(3,900,600)))"]),
    ]

    api = api_probe()

    final_pass = (
        all(v["exists"] for v in files.values())
        and all(all(v.values()) for v in markers.values())
        and api.get("ok")
        and api.get("clean")
        and all(p.get("ok") for p in probes)
    )

    report = {
        "ts": now(),
        "kind": "phase3l_universal_larynx_coverage_audit",
        "final_pass": bool(final_pass),
        "files": files,
        "markers": markers,
        "api_probe": api,
        "probes": probes,
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("PHASE 3L — UNIVERSAL LARYNX COVERAGE AUDIT")
    lines.append("=" * 72)
    lines.append(f"final_pass: {bool(final_pass)}")
    lines.append("")
    lines.append("FILES")
    for name, info in files.items():
        lines.append(f"  {'✅' if info['exists'] else '❌'} {name}: {info['path']}")

    lines.append("")
    lines.append("MARKERS")
    for path, checks in markers.items():
        lines.append(f"  {path}")
        for marker, ok in checks.items():
            lines.append(f"    {'✅' if ok else '❌'} {marker}")

    lines.append("")
    lines.append("API PROBE")
    lines.append(f"  ok: {api.get('ok')}")
    lines.append(f"  keys: {api.get('keys')}")
    lines.append(f"  clean: {api.get('clean')}")
    if api.get("error"):
        lines.append(f"  error: {api.get('error')}")
    lines.append(f"  answer: {api.get('answer')}")

    lines.append("")
    lines.append("DIRECT PROBES")
    for p in probes:
        lines.append(f"  {'✅' if p.get('ok') else '❌'} {p.get('name')}")
        if p.get("stdout"):
            lines.append("    stdout: " + p["stdout"].replace("\n", " ")[:500])
        if p.get("stderr"):
            lines.append("    stderr: " + p["stderr"].replace("\n", " ")[:500])
        if p.get("error"):
            lines.append("    error: " + p["error"])

    REPORT_TXT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print()
    print("saved:", REPORT_JSON)
    print("saved:", REPORT_TXT)

if __name__ == "__main__":
    main()
