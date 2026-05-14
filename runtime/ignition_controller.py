from runtime.anchor_mutator_accelerator import mutate_anchors_and_accelerate
from runtime.algorithm_selector import select_best_reply
from runtime.birth_point_mapper import build_birth_packet
from runtime.pulse_context_reader import latest_pulse_context
import json, datetime, os

LOG = "runtime/logs/ignition_controller.log"
os.makedirs("runtime/logs", exist_ok=True)

def controlled_ignite(prompt="state of the build", mutate=False):
    pulse = latest_pulse_context()
    birth = build_birth_packet(prompt, pulse_context=pulse)

    mutation = None
    if mutate:
        mutation = mutate_anchors_and_accelerate()

    selected = select_best_reply(prompt)

    event = {
        "ts": datetime.datetime.now().isoformat(),
        "prompt": prompt,
        "mutate": mutate,
        "birth_packet": birth,
        "winner": selected.get("winner"),
        "mutation": mutation,
    }

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event

if __name__ == "__main__":
    out = controlled_ignite("what is the build doing right now?", mutate=False)
    print(json.dumps(out, indent=2, ensure_ascii=False)[:3000])

