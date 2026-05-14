from pathlib import Path
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

