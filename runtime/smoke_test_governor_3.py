from runtime.governor import LeveonGovernor, Candidate
import json

gov = LeveonGovernor()

tests = [
    {
        "prompt": "How does fear shape attention?",
        "candidates": [
            Candidate("This question is really about fear.", 0.2, {"path_id": "bad"}),
            Candidate("Fear narrows attention by shifting the mind into a protective focus.", 0.7, {"path_id": "glyph:fear|phenome:TH|style:direct"}),
            Candidate("Fear shapes attention because danger-signals compress focus and reduce scanning.", 0.65, {"path_id": "glyph:fear|phenome:TH|style:causal"}),
        ],
        "winner_path": "glyph:fear|phenome:TH|style:direct",
        "memory_flag": True,
    },
    {
        "prompt": "I miss my dad and it still hurts.",
        "candidates": [
            Candidate("This is really about grief.", 0.2, {"path_id": "bad"}),
            Candidate("Missing your dad can hurt because love stays active even when the person is gone.", 0.72, {"path_id": "glyph:grief|phenome:AH|style:warm_direct"}),
            Candidate("Grief keeps memory close and makes the present feel heavier than it should.", 0.68, {"path_id": "glyph:grief|phenome:EE|style:compressed"}),
        ],
        "winner_path": "glyph:grief|phenome:AH|style:warm_direct",
        "memory_flag": True,
    },
    {
        "prompt": "Where should the phonome layer plug into the spiral language pipeline?",
        "candidates": [
            Candidate("This question is really about architecture.", 0.2, {"path_id": "bad"}),
            Candidate("Put the phonome layer between glyph/plan and final English realization so it guides phrasing without changing meaning.", 0.74, {"path_id": "glyph:build|phenome:ION|style:architect"}),
            Candidate("Attach phonome mapping after scoring: pick the winner first, then render with phonome constraints.", 0.69, {"path_id": "glyph:build|phenome:ION|style:post_select"}),
        ],
        "winner_path": "glyph:build|phenome:ION|style:architect",
        "memory_flag": False,
    },
]

last_vectors = [{"memory": 0.8, "boundary": 0.7}, {"memory": 0.6, "boundary": 0.75}]
cur_vector = {"flow": 0.55, "boundary": 0.68, "memory": 0.50, "novelty": 0.64}

for i, t in enumerate(tests, 1):
    out = gov.select(
        prompt=t["prompt"],
        candidates=t["candidates"],
        prompt_memory_flag=t["memory_flag"],
        last_resonance_vectors=last_vectors,
        current_resonance_vector=cur_vector,
        path_id_for_winner=t["winner_path"],
    )
    print(f"\n=== TEST {i} ===")
    print("prompt:", t["prompt"])
    print("chosen_output:", out["chosen_output"])
    print("metrics:", out["metrics"])
    print("gold_standard_stored:", out["gold_standard_stored"])
    print("reinforcement:", out["reinforcement"])

print("\n--- gold_standards tail ---")
import os
if os.path.exists("runtime/gold_standards.jsonl"):
    with open("runtime/gold_standards.jsonl","r",encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    for line in lines[-5:]:
        print(line)

