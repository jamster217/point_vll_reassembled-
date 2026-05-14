
def run_outcome_tracker():
    try:
        from runtime.outcome_tracker import main as run
        run()
    except Exception as e:
        print("[OUTCOME TRACK ERROR]", e)

import json, time, hashlib, pathlib

MEM_PATH = pathlib.Path("assets/memory/shape_compounds.json")
OUT_PATH = pathlib.Path("reports/build_snapshots/active_build_action_latest.json")

def load_memory():
    if not MEM_PATH.exists():
        return {"compounds": []}
    try:
        return json.loads(MEM_PATH.read_text())
    except Exception:
        return {"compounds": []}

def save_memory(data):
    MEM_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEM_PATH.write_text(json.dumps(data, indent=2))

def latest_compound(data):
    comps = data.get("compounds", [])
    return comps[-1] if comps else None

def score_usefulness(c):
    txt = (c.get("english_gloss") or c.get("synthesis_summary") or "").lower()
    tags = c.get("meaning_tags", [])
    chain = c.get("logic_chain", [])

    score = 0
    if len(txt) > 80: score += 2
    if "next action" in txt: score += 4
    if "future_use_selection" in txt or "future_use_selection" in tags: score += 6
    if "node44" in txt or "node44" in tags: score += 3
    if "auto_build" in tags: score += 3
    if "repeat" in txt: score -= 3
    if any("new_constraint:" in str(x) for x in chain): score += 5
    return score

def execute(compound, data):
    if not compound:
        return {"status": "no_compound"}

    chain = compound.get("logic_chain", [])
    selected_constraint = None

    for item in chain:
        if isinstance(item, str) and item.startswith("new_constraint:"):
            selected_constraint = item.split(":", 1)[1]

    if not selected_constraint and "future_use_selection" in json.dumps(compound):
        selected_constraint = "future_use_selection"

    result = {
        "status": "executed",
        "selected_constraint": selected_constraint,
        "action": "evaluate_compounds_for_usefulness",
        "tested": 0,
        "before_count": len(data.get("compounds", [])),
        "useful_candidates": [],
        "route_update": None,
    }

    comps = data.get("compounds", [])
    scored = []
    for c in comps[-25:]:
        scored.append((score_usefulness(c), c.get("compound_id"), c))

    scored.sort(reverse=True, key=lambda x: x[0])
    useful = [cid for score, cid, c in scored if cid and score >= 6]

    result["tested"] = len(scored)
    result["useful_candidates"] = useful[:7]

    if selected_constraint == "future_use_selection" and useful:
        result["route_update"] = {
            "prefer": "auto_pressure_flashback_reasoner",
            "reason": "future_use_selection produced useful candidates",
            "top_candidate": useful[0],
        }

    return result

def save_action_feedback(data, action):
    txt = json.dumps(action, indent=2)
    compound = {
        "compound_id": "cmp_active_action_" + hashlib.sha256((txt + str(time.time())).encode()).hexdigest()[:12],
        "source_kind": "active_build_executor_feedback",
        "english_gloss": "Active build executor tested recalled compounds for usefulness and produced a route update.",
        "synthesis_summary": txt,
        "logic_chain": [
            "source:active_build_executor",
            "operation:evaluate_compounds_for_usefulness",
            "operation:route_update_feedback",
            "final_point:" + txt[:300],
        ],
        "flow": 0.7,
        "boundary": 0.86,
        "memory": 0.95,
        "novelty": 0.5,
        "meaning_tags": ["active_build", "executor_feedback", "future_use_selection", "route_update", "node44"],
        "symbolic_trace": ["ActiveBuildExecutor", "UsefulnessSelection", "RouteUpdate", "CompoundMemory"],
        "confidence": 0.89,
        "created_at": time.time(),
        "last_accessed": time.time(),
    }
    data.setdefault("compounds", []).append(compound)
    return compound

def main():
    data = load_memory()
    compound = latest_compound(data)
    action = execute(compound, data)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(action, indent=2))

    feedback = save_action_feedback(data, action)
    save_memory(data)

    print("ACTIVE BUILD ACTION")
    print(json.dumps(action, indent=2))
    run_outcome_tracker()
    print("\n[SAVED EXECUTOR FEEDBACK]")
    print(json.dumps({"compound_id": feedback["compound_id"], "source_kind": feedback["source_kind"]}, indent=2))

if __name__ == "__main__":
    main()

