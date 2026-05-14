from pathlib import Path
import json, time

ROOT = Path(__file__).resolve().parents[1]
LATTICE_DIR = ROOT / "var" / "lattice"
OPTIMIZER_STATE = LATTICE_DIR / "topology_optimizer_state_v103.json"
TUNING_STATE = LATTICE_DIR / "v104_runtime_tuning.json"
TUNING_LOG = LATTICE_DIR / "v104_runtime_tuning.jsonl"

def _load(path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def update_runtime_tuning():
    state = _load(OPTIMIZER_STATE, {})
    recommendation = state.get("recommendation", "preserve_current_route")
    last_score = state.get("last_score", {})

    tuning = _load(TUNING_STATE, {
        "coherence_target": 0.72,
        "containment_weight": 0.15,
        "thread_preservation_weight": 0.25,
        "repetition_penalty": 0.10,
        "boundary_phrase": "",
        "turns": 0,
    })

    tuning["turns"] = int(tuning.get("turns", 0)) + 1
    tuning["last_recommendation"] = recommendation
    tuning["last_score"] = last_score
    tuning["updated_ts"] = time.time()
    tuning["law"] = "v104_runtime_tuning_changes_config_not_source"

    if recommendation == "add_grounded_boundary":
        tuning["containment_weight"] = min(float(tuning.get("containment_weight", 0.15)) + 0.05, 0.45)
        tuning["boundary_phrase"] = "The reply should stay clear, steady, bounded, and human-scale."
    elif recommendation == "increase_structure":
        tuning["coherence_target"] = min(float(tuning.get("coherence_target", 0.72)) + 0.03, 0.9)
    elif recommendation == "reduce_repetition":
        tuning["repetition_penalty"] = min(float(tuning.get("repetition_penalty", 0.10)) + 0.05, 0.35)
    elif recommendation == "increase_virellion_thread_terms":
        tuning["thread_preservation_weight"] = min(float(tuning.get("thread_preservation_weight", 0.25)) + 0.05, 0.45)

    _write(TUNING_STATE, tuning)

    with TUNING_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(tuning, ensure_ascii=False) + "\n")

    return tuning

if __name__ == "__main__":
    print(json.dumps(update_runtime_tuning(), indent=2, ensure_ascii=False))

