from runtime.governor import LeveonGovernor, Candidate
import json

gov = LeveonGovernor()

prompt = "How does fear shape attention?"
cands = [
    Candidate(text="This question is really about fear.", base_score=0.2, meta={"path_id": "bad"}),
    Candidate(
        text="Fear often narrows attention by shifting the mind into a protective focus.",
        base_score=0.7,
        meta={"path_id": "glyph:fear|phenome:TH|style:direct"},
    ),
    Candidate(
        text="Fear shapes attention because danger-signals compress focus and reduce scanning.",
        base_score=0.65,
        meta={"path_id": "glyph:fear|phenome:TH|style:causal"},
    ),
]

def run_once(i: int):
    out = gov.select(
        prompt=prompt,
        candidates=cands,
        prompt_memory_flag=True,
        last_resonance_vectors=[{"memory": 0.8, "boundary": 0.7}, {"memory": 0.6, "boundary": 0.75}],
        current_resonance_vector={"flow": 0.55, "boundary": 0.68, "memory": 0.50, "novelty": 0.64},
        path_id_for_winner="glyph:fear|phenome:TH|style:direct",
    )
    print(f"\n=== RUN {i} ===")
    print("chosen_output:", out["chosen_output"])
    print("metrics:", out["metrics"])
    print("reinforcement:", out["reinforcement"])
    print("gold_standard_stored:", out["gold_standard_stored"])
    # show the winner candidate debug line
    top = out["ranked_candidates"][0]
    print("winner_score_detail:", {"score": top["score"], "boosts": top["boosts"], "debug": top["debug"]})

run_once(1)
run_once(2)

