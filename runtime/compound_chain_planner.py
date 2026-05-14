import json, time, hashlib, pathlib

MEM_PATH = pathlib.Path("assets/memory/shape_compounds.json")
PLAN_PATH = pathlib.Path("reports/build_snapshots/compound_chain_plan_latest.json")

def load_memory():
    if not MEM_PATH.exists():
        return {"compounds": []}
    return json.loads(MEM_PATH.read_text())

def score(c):
    kind = c.get("source_kind", "")
    impact = float(c.get("impact_score", 0) or 0)
    reinforce = int(c.get("reinforcement_count", 0) or 0)
    decay = float(c.get("decay_score", 0) or 0)
    tags = c.get("meaning_tags", [])

    # Old inflated outcome_tracker compounds are reports, not primary route anchors.
    if kind == "outcome_tracker":
        impact = min(impact, 12)

    # Active executor feedback is support material, not the main anchor.
    if kind == "active_build_executor_feedback":
        impact = min(impact, 8)

    base = impact + reinforce * 2 - decay

    # Prefer actual behavior-bearing compounds over report compounds.
    if kind == "flashback_shape_reasoner_auto_mutation":
        base += 30
    elif kind == "flashback_shape_reasoner_meaning_drop":
        base += 10
    elif kind == "outcome_tracker":
        base -= 6

    if "reinforced_path" in tags:
        base += 8
    if "future_use_selection" in tags:
        base += 6
    if "auto_mutation" in tags:
        base += 5
    if "impact_reinforced" in tags:
        base += 8
    if c.get("archived"):
        base -= 999

    return base

def main():
    data = load_memory()
    comps = data.get("compounds", [])

    ranked = sorted(comps, key=score, reverse=True)

    # Controlled branching:
    # keep strongest anchor, but allow limited exploration from behavior compounds.
    anchor = ranked[0:1]

    behavior_branches = [
        c for c in ranked[1:]
        if c.get("source_kind") in {
            "flashback_shape_reasoner_auto_mutation",
            "flashback_shape_reasoner_meaning_drop",
            "temporal_flashback_larynx",
        }
        and not c.get("archived")
    ][:3]

    support_reports = [
        c for c in ranked[1:]
        if c.get("source_kind") in {
            "outcome_tracker",
            "active_build_executor_feedback",
            "compound_chain_planner_feedback",
        }
        and not c.get("archived")
    ][:1]

    top = anchor + behavior_branches + support_reports

    chain = []
    for c in top:
        chain.append({
            "compound_id": c.get("compound_id"),
            "source_kind": c.get("source_kind"),
            "score": score(c),
            "impact_score": c.get("impact_score", 0),
            "tags": c.get("meaning_tags", []),
            "action_hint": (
                "activate_as_primary_route"
                if c == top[0]
                else (
                    "controlled_branch_candidate"
                    if c.get("source_kind") in {
                        "flashback_shape_reasoner_auto_mutation",
                        "flashback_shape_reasoner_meaning_drop",
                        "temporal_flashback_larynx",
                    }
                    else "support_report_only"
                )
            )
        })

    plan = {
        "timestamp": time.time(),
        "status": "planned",
        "planner": "compound_chain_planner",
        "selected_chain": chain,
        "multi_step_plan": [
            "1. Use strongest reinforced compound as primary route anchor.",
            "2. Use next two compounds as support constraints.",
            "3. Run active_build_executor.",
            "4. Run outcome_tracker.",
            "5. Run reinforcement_decay.",
            "6. Save resulting plan feedback into compound memory."
        ]
    }

    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(plan, indent=2))

    feedback = {
        "compound_id": "cmp_chain_plan_" + hashlib.sha256((json.dumps(plan) + str(time.time())).encode()).hexdigest()[:12],
        "source_kind": "compound_chain_planner_feedback",
        "english_gloss": "Compound chain planner selected the strongest reinforced compounds and produced a multi-step build plan.",
        "synthesis_summary": json.dumps(plan, indent=2),
        "logic_chain": [
            "source:compound_chain_planner",
            "operation:rank_compounds_by_impact_reinforcement_decay",
            "operation:select_top_chain",
            "operation:emit_multi_step_plan"
        ],
        "meaning_tags": ["compound_chain", "multi_step_plan", "reinforced_path", "node44", "auto_build"],
        "impact_score": 1,
        "created_at": time.time()
    }

    data.setdefault("compounds", []).append(feedback)
    MEM_PATH.write_text(json.dumps(data, indent=2))

    print("COMPOUND CHAIN PLAN")
    print(json.dumps(plan, indent=2))
    print("\n[SAVED CHAIN PLAN]", feedback["compound_id"])

if __name__ == "__main__":
    main()

