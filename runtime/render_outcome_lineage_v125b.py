from pathlib import Path
import json, time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "v12_5" / "render_outcome_lineage_v125b.json"

SEARCH_ROOTS = [
    ROOT / "var" / "lattice",
    ROOT / "reports" / "v12_9" / "topology",
    ROOT / "reports" / "v12_9" / "visual_cycle",
    ROOT / "reports" / "v12_9" / "visual_memory",
]

SCORE_KEYS = {"score", "topology_score", "coherence", "total"}

def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def scores(obj, found=None):
    if found is None:
        found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower() in SCORE_KEYS and isinstance(v, (int, float)):
                found.append(float(v))
            else:
                scores(v, found)
    elif isinstance(obj, list):
        for item in obj:
            scores(item, found)
    return found

def classify(path):
    s = str(path).lower()
    if "topology" in s:
        return "topology"
    if "visual" in s:
        return "visual"
    if "render" in s:
        return "render"
    return "mixed"

events = []
for root in SEARCH_ROOTS:
    if not root.exists():
        continue
    for path in root.rglob("*.json"):
        obj = load(path)
        if obj is None:
            continue
        vals = scores(obj)
        if not vals:
            continue
        family = classify(path)
        events.append({
            "path": str(path.relative_to(ROOT)),
            "family": family,
            "mtime": path.stat().st_mtime,
            "score": max(vals),
        })

events.sort(key=lambda e: e["mtime"])

by_family = {}
for e in events:
    by_family.setdefault(e["family"], []).append(e)

judgments = {}
for family, items in by_family.items():
    last = items[-2:]
    if len(last) < 2:
        judgments[family] = {
            "status": "need_more_events",
            "events": last,
        }
        continue
    delta = round(last[-1]["score"] - last[-2]["score"], 6)
    if delta > 0.01:
        verdict = "improved"
    elif delta < -0.01:
        verdict = "declined"
    else:
        verdict = "stable_hold"
    judgments[family] = {
        "status": "judged",
        "previous": last[-2],
        "current": last[-1],
        "delta": delta,
        "verdict": verdict,
    }

packet = {
    "active": True,
    "version": "v12.5b_render_outcome_lineage",
    "ts": time.time(),
    "families_seen": sorted(by_family.keys()),
    "judgments": judgments,
    "law": "compare_like_to_like_before_claiming_causal_improvement",
    "protected_spine": True,
    "allowed_action": "read_scores_write_report_only",
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(packet, indent=2, ensure_ascii=False))

