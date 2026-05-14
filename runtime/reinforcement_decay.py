import json, time, pathlib

MEM_PATH = pathlib.Path("assets/memory/shape_compounds.json")
REPORT_PATH = pathlib.Path("reports/build_snapshots/reinforcement_decay_latest.json")

BEHAVIOR_KINDS = {
    "flashback_shape_reasoner_auto_mutation",
    "flashback_shape_reasoner_meaning_drop",
    "temporal_flashback_larynx",
}

REPORT_KINDS = {
    "active_build_executor_feedback",
    "outcome_tracker",
    "compound_chain_planner_feedback",
}

def load_memory():
    if not MEM_PATH.exists():
        return {"compounds": []}
    return json.loads(MEM_PATH.read_text())

def save_memory(data):
    MEM_PATH.write_text(json.dumps(data, indent=2))

def main():
    data = load_memory()
    comps = data.get("compounds", [])

    reinforced_behavior = 0
    reinforced_reports_limited = 0
    decayed = 0
    archived = 0
    skipped = 0

    now = time.time()

    for c in comps:
        kind = c.get("source_kind", "")
        score = float(c.get("impact_score", 0) or 0)
        tags = c.setdefault("meaning_tags", [])

        if c.get("archived"):
            skipped += 1
            continue

        # Full amplification ONLY for behavior-bearing compounds.
        if kind in BEHAVIOR_KINDS and score >= 8:
            c["impact_score"] = round(score + 1.0, 3)
            c["reinforcement_count"] = int(c.get("reinforcement_count", 0) or 0) + 1
            c["last_reinforced_at"] = now
            if "reinforced_path" not in tags:
                tags.append("reinforced_path")
            if "behavior_reinforced" not in tags:
                tags.append("behavior_reinforced")
            reinforced_behavior += 1

        # Reports/logs get capped and marked, not amplified into anchors.
        elif kind in REPORT_KINDS:
            if score > 12:
                c["impact_score"] = 12
            if "report_support_memory" not in tags:
                tags.append("report_support_memory")
            reinforced_reports_limited += 1

        # Weak generated compounds decay.
        elif (
            kind in BEHAVIOR_KINDS
            and score < 8
            and "impact_reinforced" not in tags
        ):
            old_decay = float(c.get("decay_score", 0) or 0)
            c["decay_score"] = round(old_decay + 1.0, 3)
            decayed += 1

            if c["decay_score"] >= 3:
                c["archived"] = True
                if "shadow_archived_low_impact" not in tags:
                    tags.append("shadow_archived_low_impact")
                archived += 1

        else:
            skipped += 1

    report = {
        "timestamp": now,
        "total_compounds": len(comps),
        "reinforced_behavior": reinforced_behavior,
        "reinforced_reports_limited": reinforced_reports_limited,
        "decayed": decayed,
        "archived": archived,
        "skipped": skipped,
        "law": "full amplification only for behavior compounds; reports capped as support memory"
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    save_memory(data)

    print("REINFORCEMENT DECAY PASS")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()

