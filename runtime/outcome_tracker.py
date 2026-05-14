import json, time, hashlib, pathlib

MEM_PATH = pathlib.Path("assets/memory/shape_compounds.json")
ACTION_PATH = pathlib.Path("reports/build_snapshots/active_build_action_latest.json")

def load_json(p, default):
    try:
        return json.loads(p.read_text()) if p.exists() else default
    except Exception:
        return default

def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))

def compute_impact(before_count, after_count, useful_candidates):
    delta = max(0, after_count - before_count)
    usefulness = len(useful_candidates or [])
    return {
        "before_count": before_count,
        "after_count": after_count,
        "impact_delta": delta,
        "usefulness": usefulness,
        "score": delta + usefulness
    }

def reinforce_top_candidate(data, action, impact):
    route = action.get("route_update") or {}
    top_id = route.get("top_candidate")

    if not top_id:
        return {"reinforced": False, "reason": "no_top_candidate"}

    behavior_kinds = {
        "flashback_shape_reasoner_auto_mutation",
        "flashback_shape_reasoner_meaning_drop",
        "temporal_flashback_larynx",
    }

    report_kinds = {
        "active_build_executor_feedback",
        "outcome_tracker",
        "compound_chain_planner_feedback",
    }

    for c in data.get("compounds", []):
        if c.get("compound_id") == top_id:
            kind = c.get("source_kind", "")
            tags = c.setdefault("meaning_tags", [])

            base_add = float(impact.get("score", 0) or 0)

            # Full reinforcement only for behavior-bearing compounds.
            if kind in behavior_kinds:
                add = base_add

            # Reports/logs can receive tiny trace reinforcement, but cannot dominate.
            elif kind in report_kinds or top_id.startswith("cmp_active_action_") or top_id.startswith("cmp_outcome_"):
                add = min(base_add * 0.15, 1.0)
                if "report_limited_reinforcement" not in tags:
                    tags.append("report_limited_reinforcement")

            # Unknown compounds get conservative reinforcement.
            else:
                add = min(base_add * 0.35, 2.0)

            old = float(c.get("impact_score", 0) or 0)
            c["impact_score"] = round(old + add, 3)
            c["last_reinforced_at"] = time.time()
            c["reinforcement_count"] = int(c.get("reinforcement_count", 0) or 0) + 1

            if "impact_reinforced" not in tags:
                tags.append("impact_reinforced")

            if kind in behavior_kinds and "behavior_reinforced" not in tags:
                tags.append("behavior_reinforced")

            c.setdefault("logic_chain", [])
            c["logic_chain"].append(f"impact_reinforced:+{add}")

            return {
                "reinforced": True,
                "compound_id": top_id,
                "source_kind": kind,
                "reinforcement_mode": "full_behavior" if kind in behavior_kinds else "limited_report",
                "old_impact_score": old,
                "added": add,
                "new_impact_score": c["impact_score"]
            }

    return {"reinforced": False, "reason": "top_candidate_not_found", "compound_id": top_id}

def main():
    data = load_json(MEM_PATH, {"compounds": []})
    action = load_json(ACTION_PATH, {})

    before = int(action.get("before_count", len(data.get("compounds", []))))
    useful = action.get("useful_candidates", [])
    after = len(data.get("compounds", []))

    impact = compute_impact(before, after, useful)
    reinforcement = reinforce_top_candidate(data, action, impact)

    feedback = {
        "compound_id": "cmp_outcome_" + hashlib.sha256((str(time.time())).encode()).hexdigest()[:12],
        "source_kind": "outcome_tracker",
        "english_gloss": "Measured clean impact of last action and reinforced the top candidate compound.",
        "synthesis_summary": json.dumps({
            "impact": impact,
            "reinforcement": reinforcement
        }),
        "logic_chain": [
            "source:outcome_tracker",
            f"before_count:{impact['before_count']}",
            f"after_count:{impact['after_count']}",
            f"impact_delta:{impact['impact_delta']}",
            f"usefulness:{impact['usefulness']}",
            f"score:{impact['score']}",
            "operation:reinforce_top_candidate"
        ],
        "meaning_tags": ["impact", "feedback", "reinforcement", "clean_delta", "top_candidate_reinforced"],
        "impact_score": impact["score"],
        "reinforcement": reinforcement,
        "created_at": time.time()
    }

    data.setdefault("compounds", []).append(feedback)
    save_json(MEM_PATH, data)

    print("OUTCOME TRACKED")
    print(json.dumps(impact, indent=2))
    print("\nTOP CANDIDATE REINFORCEMENT")
    print(json.dumps(reinforcement, indent=2))

if __name__ == "__main__":
    main()

