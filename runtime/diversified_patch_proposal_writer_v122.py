from pathlib import Path
import json, time, hashlib

ROOT = Path(__file__).resolve().parents[1]
PROPOSALS = ROOT / "var" / "patch_gate" / "proposals"
STATE = ROOT / "var" / "patch_gate" / "diversified_proposal_state_v122.json"
EVENTS = ROOT / "var" / "patch_gate" / "diversified_proposal_events_v122.jsonl"

def _load(path, fallback=None):
    try:
        if Path(path).exists():
            return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def _write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _append(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def _proposal_id(title, content):
    return "v122_" + title + "_" + hashlib.sha256(content.encode()).hexdigest()[:12]

def _already_exists(path):
    return (ROOT / path).exists()

def _module_visual_tag_index():
    path = "runtime/visual_tag_index_v122.py"
    content = r'''from pathlib import Path
import json, collections, time

ROOT = Path(__file__).resolve().parents[1]
IMAGE_MEMORY = ROOT / "var" / "image_memory"
DEEP = IMAGE_MEMORY / "deep_visual_memory_analysis_v114.jsonl"
OUT = IMAGE_MEMORY / "visual_tag_index_v122.json"

def _read_jsonl(path):
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out

def build_index(limit=80):
    counts = collections.Counter()
    buckets = {"emotional": [], "memory": [], "structural": []}

    for row in _read_jsonl(DEEP):
        for tag in row.get("emotional_tags", []):
            counts[tag] += 2
            if tag not in buckets["emotional"]:
                buckets["emotional"].append(tag)
        for tag in row.get("memory_connections", []):
            counts[tag] += 2
            if tag not in buckets["memory"]:
                buckets["memory"].append(tag)
        for tag in row.get("structural_tags", []):
            counts[tag] += 2
            if tag not in buckets["structural"]:
                buckets["structural"].append(tag)
        for tag in row.get("all_tags", []):
            counts[tag] += 1

    ranked = [{"tag": k, "weight": v} for k, v in counts.most_common(limit)]

    packet = {
        "active": True,
        "ts": time.time(),
        "ranked_tags": ranked,
        "buckets": {k: v[:32] for k, v in buckets.items()},
        "law": "v122_visual_tag_index_from_deep_memory",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    print(json.dumps(build_index(), indent=2, ensure_ascii=False))
'''
    return path, content, "Create visual tag index from deep visual memory"

def _module_patch_health_summary():
    path = "runtime/patch_health_summary_v122.py"
    content = r'''from pathlib import Path
import json, time

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "var" / "patch_gate"
OUT = PATCH / "patch_health_summary_v122.json"

def _load(path, fallback=None):
    try:
        if Path(path).exists():
            return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def summarize():
    judge = _load(PATCH / "patch_judge_state_v118.json", {})
    auto = _load(PATCH / "auto_patch_loop_state_v120.json", {})
    rapid = _load(PATCH / "rapid_improvement_state_v121.json", {})

    packet = {
        "active": True,
        "ts": time.time(),
        "latest_judge_total": judge.get("event_judgment", {}).get("scores", {}).get("total"),
        "latest_proposal_total": judge.get("proposal_judgment", {}).get("scores", {}).get("total"),
        "auto_status": auto.get("status"),
        "auto_result": auto.get("result"),
        "rapid_status": rapid.get("status"),
        "rapid_stop_reason": rapid.get("stop_reason"),
        "source_protected": (
            judge.get("loop_state", {}).get("source_protected") is True
            and auto.get("source_protected") is True
        ),
        "law": "v122_patch_health_summary_reads_gate_metrics",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2, ensure_ascii=False))
'''
    return path, content, "Create patch health summary from gate metrics"

def _module_render_feedback_weights():
    path = "runtime/render_feedback_weights_v122.py"
    content = r'''from pathlib import Path
import json, time

ROOT = Path(__file__).resolve().parents[1]
VISUAL_INDEX = ROOT / "var" / "image_memory" / "visual_tag_index_v122.json"
RENDER_CONTEXT = ROOT / "var" / "lattice" / "deep_visual_memory_state_v114.json"
OUT = ROOT / "var" / "lattice" / "render_feedback_weights_v122.json"

def _load(path, fallback=None):
    try:
        if Path(path).exists():
            return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def compute_weights():
    index = _load(VISUAL_INDEX, {})
    deep = _load(RENDER_CONTEXT, {})

    ranked = index.get("ranked_tags", []) if isinstance(index, dict) else []
    weights = {}

    for row in ranked[:24]:
        tag = row.get("tag")
        weight = row.get("weight", 1)
        if tag:
            weights[tag] = round(min(1.0, 0.10 + float(weight) / 20.0), 4)

    for tag in ["white_ash", "virellion", "echoforge", "thalveil", "anchor"]:
        weights[tag] = max(weights.get(tag, 0.0), 0.85)

    packet = {
        "active": True,
        "ts": time.time(),
        "weights": weights,
        "render_hints": [
            "use higher weights to choose recurring visual anchors",
            "preserve structural glyph continuity",
            "do not convert inferred personal memory into confirmed fact",
        ],
        "law": "v122_render_feedback_weights_from_visual_index",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    print(json.dumps(compute_weights(), indent=2, ensure_ascii=False))
'''
    return path, content, "Create render feedback weights from visual tag index"

def _module_topology_score_history():
    path = "runtime/topology_score_history_v122.py"
    content = r'''from pathlib import Path
import json, time

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "var" / "lattice" / "autogenous_topology_v103.jsonl"
OUT = ROOT / "var" / "lattice" / "topology_score_history_v122.json"

def _rows():
    if not LOG.exists():
        return []
    out = []
    for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out

def summarize(limit=40):
    rows = _rows()[-limit:]
    scores = []

    for row in rows:
        score = row.get("score", {})
        if isinstance(score, dict):
            scores.append({
                "ts": row.get("ts"),
                "image": row.get("image"),
                "depth": row.get("node", {}).get("depth"),
                "total": score.get("total"),
                "coherence": score.get("coherence"),
                "containment": score.get("containment"),
                "thread": score.get("thread"),
            })

    totals = [x["total"] for x in scores if isinstance(x.get("total"), (int, float))]
    trend = "unknown"
    if len(totals) >= 2:
        trend = "rising" if totals[-1] >= totals[0] else "falling"

    packet = {
        "active": True,
        "ts": time.time(),
        "count": len(scores),
        "latest": scores[-1] if scores else None,
        "avg_total": round(sum(totals) / len(totals), 4) if totals else None,
        "trend": trend,
        "scores": scores,
        "law": "v122_topology_score_history_for_self_improvement",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2, ensure_ascii=False))
'''
    return path, content, "Create topology score history for self-improvement"

def choose_candidate():
    candidates = [
        _module_visual_tag_index(),
        _module_patch_health_summary(),
        _module_render_feedback_weights(),
        _module_topology_score_history(),
    ]

    # Prefer missing modules first.
    for path, content, title in candidates:
        if not _already_exists(path):
            return path, content, title

    # If all exist, rotate by updating topology score history, because it is safely refreshable.
    return _module_topology_score_history()

def write_proposal():
    path, content, title = choose_candidate()
    pid = _proposal_id(path.replace("/", "_").replace(".py", ""), content)

    proposal = {
        "proposal_id": pid,
        "title": title,
        "human_approved": False,
        "ops": [
            {
                "op": "create",
                "path": path,
                "overwrite": True,
                "content": content,
            }
        ],
        "compile": [path],
        "reason": "Diversify rapid self-improvement proposals so V12.1 does not repeat the same patch fingerprint.",
        "target_file": path,
        "law": "v122_diversified_patch_proposal_writer",
    }

    PROPOSALS.mkdir(parents=True, exist_ok=True)
    out = PROPOSALS / f"{pid}.json"
    _write(out, proposal)

    event = {
        "ts": time.time(),
        "proposal": str(out),
        "target_file": path,
        "title": title,
        "law": "v122_diversified_writer_event",
    }
    _append(EVENTS, event)
    _write(STATE, event)

    return out

if __name__ == "__main__":
    print(write_proposal())

