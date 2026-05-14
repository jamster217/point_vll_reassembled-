from pathlib import Path
import json, time, os

ROOT = Path(__file__).resolve().parents[1]

CANDIDATES = [
    ROOT / "var" / "lattice",
    ROOT / "reports" / "v12_9" / "topology",
    ROOT / "reports" / "v12_9" / "visual_memory",
    ROOT / "reports" / "v12_9" / "visual_cycle",
    ROOT / "reports" / "v12_3",
]

OUT_STATE = ROOT / "var" / "lattice" / "render_outcome_judge_v125.json"
OUT_REPORT = ROOT / "reports" / "v12_5" / "render_outcome_judge_latest.json"
OUT_LOG = ROOT / "logs" / "v12_5" / "render_outcome_judge.jsonl"

SCORE_KEYS = {
    "score",
    "total",
    "topology_score",
    "coherence",
    "v106_total",
    "v124_total",
    "v125_total",
}

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def walk_scores(obj, found=None):
    if found is None:
        found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).lower()
            if lk in SCORE_KEYS and isinstance(v, (int, float)):
                found.append(float(v))
            else:
                walk_scores(v, found)
    elif isinstance(obj, list):
        for item in obj:
            walk_scores(item, found)
    return found

def recent_json_files(limit=80):
    files = []
    for base in CANDIDATES:
        if base.exists():
            files.extend(base.rglob("*.json"))
    files = [p for p in files if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]

def collect_events():
    events = []
    for path in recent_json_files():
        obj = load_json(path)
        if obj is None:
            continue
        scores = walk_scores(obj)
        if not scores:
            continue
        score = max(scores)
        events.append({
            "path": str(path.relative_to(ROOT)),
            "mtime": path.stat().st_mtime,
            "score": score,
        })
    events.sort(key=lambda e: e["mtime"])
    return events[-12:]

def judge():
    events = collect_events()
    previous = events[-2] if len(events) >= 2 else None
    current = events[-1] if events else None

    delta = None
    if previous and current:
        delta = round(current["score"] - previous["score"], 6)

    if current is None:
        verdict = "no_score_found"
        policy = "observe_only"
    elif delta is None:
        verdict = "first_score_seen"
        policy = "keep_current_render_policy"
    elif delta > 0.01:
        verdict = "render_policy_helped"
        policy = "reinforce_simplify_boundary_policy"
    elif delta < -0.01:
        verdict = "render_policy_hurt"
        policy = "loosen_simplify_or_shift_context"
    else:
        verdict = "stable_hold"
        policy = "preserve_thread_but_request_meaningful_variation"

    packet = {
        "active": True,
        "ts": time.time(),
        "version": "v12.5_render_outcome_judge",
        "previous": previous,
        "current": current,
        "score_delta": delta,
        "verdict": verdict,
        "next_render_policy": policy,
        "law": "v125_judges_whether_render_context_actually_helped",
        "protected_spine": True,
        "allowed_action": "write_state_only",
        "forbidden_action": "rewrite_source_from_score",
    }

    OUT_STATE.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_LOG.parent.mkdir(parents=True, exist_ok=True)

    text = json.dumps(packet, indent=2, ensure_ascii=False)
    OUT_STATE.write_text(text, encoding="utf-8")
    OUT_REPORT.write_text(text, encoding="utf-8")
    with OUT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")

    return packet

if __name__ == "__main__":
    print(json.dumps(judge(), indent=2, ensure_ascii=False))

