from pathlib import Path
import json, time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "v12_5" / "score_kind_audit_v125c.json"

SEARCH_ROOTS = [
    ROOT / "var" / "lattice",
    ROOT / "reports" / "v12_9" / "topology",
    ROOT / "reports" / "v12_9" / "visual_memory",
    ROOT / "reports" / "v12_9" / "visual_cycle",
    ROOT / "reports" / "v12_3",
    ROOT / "reports" / "v12_5",
]

SCORE_WORDS = {
    "score", "total", "topology_score", "coherence",
    "v106_total", "v124_total", "v125_total",
    "compile_ok", "applied_ok", "rollback_ready",
    "path_safety", "human_lock", "source_protection",
    "usefulness"
}

def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def classify_score(path, key):
    s = (str(path) + " " + str(key)).lower()

    if any(x in s for x in [
        "compile_ok", "applied_ok", "rollback_ready",
        "path_safety", "human_lock", "source_protection"
    ]):
        return "binary_patch_health"

    if any(x in s for x in [
        "topology_score", "topology_optimizer", "topology", "coherence"
    ]):
        return "topology_quality"

    if any(x in s for x in [
        "visual_memory", "visual_judge", "visual_cycle"
    ]):
        return "visual_quality"

    if any(x in s for x in [
        "render_decision", "render_outcome", "render"
    ]):
        return "render_policy"

    return "unknown_score"

def walk(obj, path, found=None, trail=""):
    if found is None:
        found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            here = f"{trail}.{k}" if trail else str(k)
            lk = str(k).lower()
            if lk in SCORE_WORDS and isinstance(v, (int, float)):
                found.append({
                    "json_path": here,
                    "key": str(k),
                    "value": float(v),
                    "kind": classify_score(path, k),
                })
            else:
                walk(v, path, found, here)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            walk(item, path, found, f"{trail}[{i}]")
    return found

events = []
for root in SEARCH_ROOTS:
    if not root.exists():
        continue
    for path in root.rglob("*.json"):
        obj = load(path)
        if obj is None:
            continue
        found = walk(obj, path)
        if not found:
            continue
        events.append({
            "path": str(path.relative_to(ROOT)),
            "mtime": path.stat().st_mtime,
            "scores": found,
        })

events.sort(key=lambda e: e["mtime"], reverse=True)

packet = {
    "active": True,
    "version": "v12.5c_score_kind_audit",
    "ts": time.time(),
    "recent_events": events[:25],
    "law": "do_not_compare_binary_health_scores_to_topology_quality_scores",
    "next": "filter_v125b_by_score_kind_before_policy_change",
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(packet, indent=2, ensure_ascii=False))

