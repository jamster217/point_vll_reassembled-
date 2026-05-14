import json, time, pathlib, argparse

STATE_PATH = pathlib.Path("runtime/cognitive_state.json")

def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {
        "cycle": 0,
        "last_anchor": None,
        "trajectory": [],
        "last_update": time.time()
    }

def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2))

def run_cycle():
    from runtime.compound_chain_planner import main as planner
    from runtime.active_build_executor import main as executor
    from runtime.reinforcement_decay import main as decay

    state = load_state()
    state["cycle"] += 1

    print(f"[COGNITIVE LOOP] cycle {state['cycle']}")

    planner()
    executor()
    decay()

    state["last_update"] = time.time()
    state["trajectory"].append({
        "cycle": state["cycle"],
        "timestamp": state["last_update"]
    })

    # keep trajectory from bloating
    state["trajectory"] = state["trajectory"][-100:]

    save_state(state)

    print("[COGNITIVE LOOP COMPLETE]")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--sleep", type=float, default=5.0)
    args = parser.parse_args()

    cycles = max(1, min(args.cycles, 25))

    for i in range(cycles):
        run_cycle()
        if i < cycles - 1:
            time.sleep(args.sleep)

if __name__ == "__main__":
    main()

