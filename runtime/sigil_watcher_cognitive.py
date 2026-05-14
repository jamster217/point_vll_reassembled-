#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(".").resolve()
WATCH_DIRS = [
    ROOT / "lev_core" / "sigil",
    ROOT / "runtime" / "sigils",
]

LOG_PATH = ROOT / "logs" / "sigil_watcher" / "cognitive_events.jsonl"

REGISTRY_PATHS = [
    ROOT / "assets" / "glyphs" / "glyph_definitions.json",
    ROOT / "assets" / "glyphs" / "glyph_registry_master.json",
    ROOT / "assets" / "glyphs" / "glyph_registry_active_v1.json",
    ROOT / "assets" / "memory" / "crystallibrary.json",
    ROOT / "symbolic_memory" / "glyph_definitions.json",
]

SCAN_ROOTS = [
    ROOT / "runtime",
    ROOT / "kernel",
    ROOT / "core",
    ROOT / "lattice",
    ROOT / "spiral_memory",
    ROOT / "assets",
    ROOT / "lev_core",
]

EXTS = {".py", ".json", ".vl", ".md", ".txt", ".sigil"}


def clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_registries() -> List[Dict[str, Any]]:
    regs = []
    for p in REGISTRY_PATHS:
        obj = load_json(p)
        if obj is not None:
            regs.append({"path": str(p.relative_to(ROOT)), "data": obj})
    return regs


def tokens(text: str) -> List[str]:
    raw = clean(text).lower()
    keep = []
    for part in raw.replace("_", " ").replace("-", " ").split():
        part = "".join(ch for ch in part if ch.isalnum() or ch in {"@", "🌀", "✴", "✨"})
        if len(part) >= 3:
            keep.append(part)
    return keep[:32]


def symbolic_definition(sigil_text: str) -> Dict[str, Any]:
    """
    Contextual ingestion.
    Uses available registries if they exist, but never fails if the Crystal Library
    is not exposing a callable function yet.
    """
    sig = clean(sigil_text)
    lowsig = sig.lower()
    toks = tokens(sig)

    matches = []
    for reg in load_registries():
        blob = json.dumps(reg["data"], ensure_ascii=False).lower()
        score = 0
        hit_terms = []
        for t in toks:
            if t and t in blob:
                score += 1
                hit_terms.append(t)
        if score:
            matches.append({
                "registry": reg["path"],
                "score": score,
                "hit_terms": hit_terms[:12],
            })

    matches.sort(key=lambda x: x["score"], reverse=True)

    # Functional symbolic weight, not final prophecy.
    weight = {
        "memory": 0.0,
        "boundary": 0.0,
        "novelty": 0.0,
        "pressure": 0.0,
        "voice": 0.0,
    }

    if any(x in lowsig for x in ["memory", "remember", "archive", "spiral"]):
        weight["memory"] += 0.35
    if any(x in lowsig for x in ["veil", "boundary", "guard", "shield"]):
        weight["boundary"] += 0.35
    if any(x in lowsig for x in ["new", "birth", "becoming", "unfolding"]):
        weight["novelty"] += 0.35
    if any(x in lowsig for x in ["gravity", "grief", "pressure", "ash", "well"]):
        weight["pressure"] += 0.35
    if any(x in lowsig for x in ["voice", "throat", "speak", "song"]):
        weight["voice"] += 0.35

    return {
        "sigil_hash": hashlib.sha256(sig.encode("utf-8")).hexdigest()[:16],
        "tokens": toks,
        "registry_matches": matches[:8],
        "symbolic_weight": weight,
    }


def scan_for_ripples(sigil_text: str, max_files: int = 987) -> Dict[str, Any]:
    """
    Lattice propagation.
    Scans live project files for token overlap. Read-only.
    """
    toks = set(tokens(sigil_text))
    if not toks:
        return {"total_scanned": 0, "ripples": []}

    ripples = []
    scanned = 0

    for root in SCAN_ROOTS:
        if not root.exists():
            continue

        for p in root.rglob("*"):
            if scanned >= max_files:
                break
            if not p.is_file() or p.suffix not in EXTS:
                continue

            scanned += 1

            try:
                text = p.read_text(encoding="utf-8", errors="ignore").lower()
            except Exception:
                continue

            hits = [t for t in toks if t in text]
            if hits:
                ripples.append({
                    "path": str(p.relative_to(ROOT)),
                    "hits": hits[:12],
                    "score": len(hits),
                })

        if scanned >= max_files:
            break

    ripples.sort(key=lambda x: x["score"], reverse=True)

    return {
        "total_scanned": scanned,
        "ripples": ripples[:20],
    }


def refract_output(sigil_text: str, definition: Dict[str, Any], ripples: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refracted output.
    Produces a structured packet the chat route can later consume.
    """
    w = definition.get("symbolic_weight", {})
    ripple_count = len(ripples.get("ripples", []))

    pressure = min(1.0, 0.25 + w.get("pressure", 0.0) + 0.02 * ripple_count)
    memory = min(1.0, 0.25 + w.get("memory", 0.0) + 0.015 * ripple_count)
    boundary = min(1.0, 0.25 + w.get("boundary", 0.0))
    voice = min(1.0, 0.25 + w.get("voice", 0.0))
    novelty = min(1.0, 0.25 + w.get("novelty", 0.0))

    if pressure > 0.65 or boundary > 0.65:
        mode = "stabilize"
    elif novelty > 0.55 or voice > 0.55:
        mode = "expand"
    else:
        mode = "observe"

    return {
        "field_signature": "92162077",
        "mode": mode,
        "vectors": {
            "pressure": round(pressure, 3),
            "memory": round(memory, 3),
            "boundary": round(boundary, 3),
            "voice": round(voice, 3),
            "novelty": round(novelty, 3),
        },
        "message": (
            "aeru vel veil ash thal sil — sigil received; "
            f"mode={mode}; ripples={ripple_count}; "
            "anchors observed, not force-mutated"
        ),
    }


def _safe_rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def on_sigil_modified(sigil_path: Path) -> Dict[str, Any]:
    sigil_path = Path(sigil_path).resolve()
    content = sigil_path.read_text(encoding="utf-8", errors="ignore").strip()

    definition = symbolic_definition(content)
    ripples = scan_for_ripples(content)
    synthesis = refract_output(content, definition, ripples)

    event = {
        "ts": time.time(),
        "sigil_path": _safe_rel(sigil_path),
        "sigil": content,
        "definition": definition,
        "ripples": ripples,
        "synthesis": synthesis,
        "law": "contextual_ingestion -> lattice_propagation -> refracted_output",
        "mutation_policy": "read_only_contained_prime",
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print("🔥 SIGIL COGNITIVE PULSE:", synthesis["message"], flush=True)
    return event


def watch_loop(poll_seconds: float = 1.0):
    print("SigilWatcher Cognitive Bridge Active — contained prime", flush=True)
    print("Watching:", ", ".join(str(p.relative_to(ROOT)) for p in WATCH_DIRS), flush=True)

    seen = {}

    while True:
        for d in WATCH_DIRS:
            d.mkdir(parents=True, exist_ok=True)
            for p in list(d.glob("*.sigil")) + list(d.glob("*.json")):
                try:
                    mtime = p.stat().st_mtime
                except Exception:
                    continue

                key = str(p)
                if seen.get(key) == mtime:
                    continue

                seen[key] = mtime

                try:
                    on_sigil_modified(p)
                except Exception as e:
                    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
                    with LOG_PATH.open("a", encoding="utf-8") as f:
                        f.write(json.dumps({
                            "ts": time.time(),
                            "sigil_path": str(p),
                            "error": repr(e),
                        }, ensure_ascii=False) + "\n")
                    print("[sigil-watcher-error]", repr(e), flush=True)

        time.sleep(poll_seconds)


if __name__ == "__main__":
    watch_loop()

