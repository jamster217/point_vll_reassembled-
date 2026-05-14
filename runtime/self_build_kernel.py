import json
import datetime
from pathlib import Path

from runtime.algorithm_selector import select_best_reply

REPORT_DIR = Path("runtime/logs/self_build_kernel")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

TEST_PROMPTS = [
    "what is grief in relation to time?",
    "what is love?",
    "what is recursion?",
    "what is the build doing right now?",
    "what is a gravity well?",
    "how does memory become intelligence?",
]

def judge_reply(reply):
    low = reply.lower()
    flaws = []

    if "savariel answers" in low or "akasha echo" in low:
        flaws.append("echo_leak")

    if "the best answer should" in low:
        flaws.append("meta_scaffold")

    if "relation field" in low and "plainly" not in low:
        flaws.append("shape_not_realized")

    if len(reply.split()) < 12:
        flaws.append("too_short")

    if len(reply.split()) > 140:
        flaws.append("too_long")

    score = 1.0 - (0.18 * len(flaws))
    return max(0.0, round(score, 3)), flaws

def run_cycle(cycle_id):
    rows = []

    for prompt in TEST_PROMPTS:
        out = select_best_reply(prompt)
        reply = out["winner"]["reply"]
        score, flaws = judge_reply(reply)

        rows.append({
            "prompt": prompt,
            "shape": out.get("shape"),
            "memory_score": out.get("memory_match", {}).get("score"),
            "winner": out["winner"]["name"],
            "selector_score": out["winner"]["score"],
            "reply_quality": score,
            "flaws": flaws,
            "reply": reply,
        })

    flaw_counts = {}
    for row in rows:
        for flaw in row["flaws"]:
            flaw_counts[flaw] = flaw_counts.get(flaw, 0) + 1

    recommendation = "hold"
    if flaw_counts.get("meta_scaffold", 0) >= 2:
        recommendation = "patch_reasoning_mouth_remove_meta"
    elif flaw_counts.get("echo_leak", 0) >= 1:
        recommendation = "increase_echo_filter"
    elif flaw_counts.get("shape_not_realized", 0) >= 2:
        recommendation = "patch_shape_to_plain_english"
    elif sum(r["reply_quality"] for r in rows) / len(rows) < 0.78:
        recommendation = "improve_english_mouth_naturalness"

    report = {
        "ts": datetime.datetime.now().isoformat(),
        "cycle": cycle_id,
        "rows": rows,
        "flaw_counts": flaw_counts,
        "recommendation": recommendation,
    }

    path = REPORT_DIR / f"cycle_{cycle_id}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"SELF-BUILD CYCLE {cycle_id}")
    print("recommendation:", recommendation)
    print("flaws:", flaw_counts)
    for row in rows:
        print("-", row["prompt"], "|", row["winner"], "| quality", row["reply_quality"], "| flaws", row["flaws"])

    return report

if __name__ == "__main__":
    for i in range(1, 4):
        run_cycle(i)

