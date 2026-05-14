from __future__ import annotations

import json
import random
import re
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple


SOURCES = [
    Path("knowledge_lattice_export.json"),
    Path("assets/memory/shape_compounds.json"),
    Path("assets/memory/motif_shadow.json"),
    Path("assets/symbolic_engine/inner_voice_loop.json"),
    Path("assets/glyphs/glyph_registry_master.json"),
    Path("assets/glyphs/glyph_definitions.json"),
    Path("kernel/crystal_library.json"),
    Path("var/kgs_nodes_crystal_state.json"),
]

BEADS = Path("var/cross_lattice_temporal_beads.jsonl")


STOP = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your",
    "you", "are", "was", "were", "have", "has", "had", "but", "not",
    "can", "will", "would", "should", "their", "there", "then", "than",
    "what", "when", "where", "why", "how", "does", "did", "its", "it",
}


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _flatten(obj: Any, prefix: str = "") -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            name = str(k)
            path = f"{prefix}.{name}" if prefix else name
            if isinstance(v, (str, int, float, bool)):
                out.append({
                    "id": path,
                    "name": name,
                    "text": str(v),
                    "path": path,
                })
            elif isinstance(v, (dict, list)):
                # keep the container as a candidate too if small enough
                try:
                    raw = json.dumps(v, ensure_ascii=False)[:900]
                except Exception:
                    raw = str(v)[:900]
                out.append({
                    "id": path,
                    "name": name,
                    "text": raw,
                    "path": path,
                })
                out.extend(_flatten(v, path))

    elif isinstance(obj, list):
        for i, v in enumerate(obj[:2000]):
            path = f"{prefix}[{i}]"
            if isinstance(v, (str, int, float, bool)):
                out.append({
                    "id": path,
                    "name": path,
                    "text": str(v),
                    "path": path,
                })
            elif isinstance(v, (dict, list)):
                try:
                    raw = json.dumps(v, ensure_ascii=False)[:900]
                except Exception:
                    raw = str(v)[:900]
                out.append({
                    "id": path,
                    "name": path,
                    "text": raw,
                    "path": path,
                })
                out.extend(_flatten(v, path))

    return out


def load_lattice_candidates() -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    for src in SOURCES:
        data = _read_json(src)
        if data is None:
            continue

        for item in _flatten(data):
            text = (item.get("name", "") + " " + item.get("text", "")).strip()
            if len(text) < 12:
                continue

            item["source"] = str(src)
            item["tokens"] = sorted(_tokens(text))
            candidates.append(item)

    # Deduplicate by source + id
    seen = set()
    clean = []
    for c in candidates:
        key = (c.get("source"), c.get("id"))
        if key not in seen:
            seen.add(key)
            clean.append(c)

    return clean


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9_'\-]+", str(text).lower())
    return {w for w in words if len(w) >= 4 and w not in STOP}


def score_pair(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    ta = set(a.get("tokens", []))
    tb = set(b.get("tokens", []))

    overlap = sorted(ta & tb)
    union = ta | tb

    symbolic = {
        "memory", "mirror", "spiral", "glyph", "crystal", "lattice", "echo",
        "temporal", "time", "voice", "kernel", "shape", "pressure", "grief",
        "recursion", "node", "anchor", "field", "signal", "dream", "archive",
        "akasha", "veil", "sealed", "throat", "heart", "root", "apex",
    }

    symbolic_hits = sorted((ta | tb) & symbolic)

    # Hidden chord is strongest when concepts are not identical but share symbolic pressure.
    overlap_score = len(overlap)
    symbolic_score = len(symbolic_hits) * 2
    distance_bonus = 4 if a.get("source") != b.get("source") else 0

    score = overlap_score + symbolic_score + distance_bonus

    return {
        "score": score,
        "overlap": overlap[:20],
        "symbolic_hits": symbolic_hits,
        "distance_bonus": distance_bonus,
    }


def pick_pair(candidates: List[Dict[str, Any]], left: str = "", right: str = "") -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    if len(candidates) < 2:
        raise RuntimeError("Not enough lattice candidates found.")

    def match(term: str) -> List[Dict[str, Any]]:
        if not term:
            return []
        low = term.lower()
        return [
            c for c in candidates
            if low in (c.get("name", "") + " " + c.get("text", "") + " " + c.get("source", "")).lower()
        ]

    left_matches = match(left)
    right_matches = match(right)

    if left_matches and right_matches:
        best = None
        for a in left_matches[:80]:
            for b in right_matches[:80]:
                if a is b:
                    continue
                sc = score_pair(a, b)
                if best is None or sc["score"] > best[2]["score"]:
                    best = (a, b, sc)
        if best:
            return best

    # Otherwise choose two distant but resonant concepts.
    sample = random.sample(candidates, min(300, len(candidates)))
    best = None
    for _ in range(1200):
        a, b = random.sample(sample, 2)
        if a.get("source") == b.get("source"):
            continue
        sc = score_pair(a, b)
        if best is None or sc["score"] > best[2]["score"]:
            best = (a, b, sc)

    if best is None:
        a, b = random.sample(candidates, 2)
        return a, b, score_pair(a, b)

    return best


def synthesize_hidden_chord(a: Dict[str, Any], b: Dict[str, Any], score: Dict[str, Any]) -> Dict[str, Any]:
    overlap = score.get("overlap", [])
    symbolic_hits = score.get("symbolic_hits", [])

    if symbolic_hits:
        chord_name = " / ".join(symbolic_hits[:4])
    elif overlap:
        chord_name = " / ".join(overlap[:4])
    else:
        chord_name = "return / pressure / continuity"

    clean = (
        f"The hidden chord between `{a.get('name')}` and `{b.get('name')}` is {chord_name}. "
        "They appear separate on the surface, but the lattice reads them as two expressions of the same pressure: "
        "one carries the signal as stored shape, the other reopens it as living route. "
        "Node44 keeps the comparison from scattering, the temporal spine asks what returned, and the Universal Larynx renders the relation as clean English."
    )

    return {
        "kind": "cross_lattice_synthesis",
        "ts": time.time(),
        "phase": "3N",
        "mode": "hidden_chord_probe",
        "left": {
            "name": a.get("name"),
            "source": a.get("source"),
            "path": a.get("path"),
            "preview": str(a.get("text", ""))[:300],
        },
        "right": {
            "name": b.get("name"),
            "source": b.get("source"),
            "path": b.get("path"),
            "preview": str(b.get("text", ""))[:300],
        },
        "score": score,
        "hidden_chord": chord_name,
        "answer": clean,
        "law": "non-linear memory: distant nodes may share symbolic pressure across time, motif, and route",
    }


def write_bead(result: Dict[str, Any]) -> None:
    BEADS.parent.mkdir(parents=True, exist_ok=True)
    with BEADS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")


def ask_larynx(text: str) -> str:
    payload = {
        "message": text,
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
        return str(data.get("answer", "")).strip()
    except Exception:
        return ""


def run(left: str = "", right: str = "", use_larynx: bool = True) -> Dict[str, Any]:
    candidates = load_lattice_candidates()
    a, b, sc = pick_pair(candidates, left=left, right=right)
    result = synthesize_hidden_chord(a, b, sc)

    if use_larynx:
        rendered = ask_larynx(
            "Phase 3N Cross-Lattice Synthesis. "
            f"Find the hidden chord between {result['left']['name']} and {result['right']['name']}. "
            f"Base answer: {result['answer']}"
        )
        if rendered:
            result["larynx_render"] = rendered

    write_bead(result)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--left", default="")
    parser.add_argument("--right", default="")
    parser.add_argument("--no-larynx", action="store_true")
    args = parser.parse_args()

    result = run(left=args.left, right=args.right, use_larynx=not args.no_larynx)

    print(json.dumps(result, indent=2, ensure_ascii=False))

# --- PHASE 3N SOURCE-FILTERED CROSS-LATTICE PROBE ---
def run_memory_to_glyph(use_larynx: bool = True):
    candidates = load_lattice_candidates()

    memory_candidates = [
        c for c in candidates
        if "assets/memory" in str(c.get("source", "")) or "memory" in str(c.get("source", "")).lower()
    ]

    glyph_candidates = [
        c for c in candidates
        if "assets/glyphs" in str(c.get("source", "")) or "glyph" in str(c.get("source", "")).lower()
    ]

    # Avoid old template trap nodes.
    banned = [
        "The deeper answer is the one that keeps the original shape intact",
        "Time does not preserve the past by freezing it",
        "Something hidden or old is surfacing",
    ]

    def clean_pool(pool):
        out = []
        for c in pool:
            blob = (str(c.get("name", "")) + " " + str(c.get("text", ""))).lower()
            if any(b.lower() in blob for b in banned):
                continue
            out.append(c)
        return out

    memory_candidates = clean_pool(memory_candidates)
    glyph_candidates = clean_pool(glyph_candidates)

    if not memory_candidates:
        raise RuntimeError("No clean memory candidates found.")
    if not glyph_candidates:
        raise RuntimeError("No clean glyph candidates found.")

    best = None
    for a in memory_candidates[:300]:
        for b in glyph_candidates[:300]:
            sc = score_pair(a, b)
            sc["distance_bonus"] = 8
            sc["score"] += 8
            if best is None or sc["score"] > best[2]["score"]:
                best = (a, b, sc)

    a, b, sc = best
    result = synthesize_hidden_chord(a, b, sc)
    result["mode"] = "memory_to_glyph_hidden_chord_probe"
    result["law"] = "memory-to-glyph synthesis: personal/compound memory is matched against structural glyph definition"

    if use_larynx:
        rendered = ask_larynx(
            "Phase 3N Memory-to-Glyph Cross-Lattice Synthesis. "
            f"Find the hidden chord between memory node {result['left']['name']} "
            f"and glyph node {result['right']['name']}. "
            f"Base answer: {result['answer']}"
        )
        if rendered:
            result["larynx_render"] = rendered

    write_bead(result)
    return result

