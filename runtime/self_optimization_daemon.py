#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path


BASE_COHERENCE = 0.7134
KERNEL_STATE = Path("./var/governor/kernel_state.json")
OUT_STATE = Path("./var/optimizer/self_optimization_state.json")
LOG_FILE = Path("./logs/self_optimization_daemon.jsonl")


class SelfOptimizationDaemon:
    def __init__(self):
        self.error_log = []

    def monitor(self, system_state):
        if system_state.get("latency", 0) > 0.8:
            return {
                "status": "action_recommended",
                "action": "reduce_node_density",
                "message": "Reducing node density",
            }

        if system_state.get("drift", 0) > 0.6:
            return {
                "status": "action_recommended",
                "action": "rebalance_cognition_weights",
                "message": "Rebalancing cognition weights",
            }

        if system_state.get("containment", 1) < 0.45:
            return {
                "status": "action_recommended",
                "action": "increase_white_ash_containment",
                "message": "Containment is low; strengthen boundary lock",
            }

        return {
            "status": "stable",
            "action": "none",
            "message": "Stable",
        }


def load_json(path: Path, fallback):
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text())
    except Exception as e:
        return {"error": str(e), **fallback}


def append_jsonl(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def main():
    daemon = SelfOptimizationDaemon()

    while True:
        state = load_json(KERNEL_STATE, {})

        coherence = float(state.get("coherence_estimate", BASE_COHERENCE) or BASE_COHERENCE)
        shape = state.get("shape_vector", {}) if isinstance(state.get("shape_vector"), dict) else {}

        drift = abs(BASE_COHERENCE - coherence)
        containment = float(shape.get("containment", 0.642) or 0.642)

        system_state = {
            "latency": 0.2,
            "drift": drift,
            "coherence_estimate": coherence,
            "containment": containment,
        }

        decision = daemon.monitor(system_state)

        event = {
            "ts": time.time(),
            "version": "self_optimization_daemon_v1",
            "law": "observe_judge_log_no_source_mutation",
            "system_state": system_state,
            "decision": decision,
        }

        OUT_STATE.parent.mkdir(parents=True, exist_ok=True)
        OUT_STATE.write_text(json.dumps(event, indent=2, ensure_ascii=False))
        append_jsonl(LOG_FILE, event)

        if decision["status"] != "stable":
            print(f"Daemon Alert: {decision['message']}", flush=True)
        else:
            print(
                f"Stable | coherence={coherence:.4f} drift={drift:.4f} containment={containment:.3f}",
                flush=True,
            )

        time.sleep(60)


if __name__ == "__main__":
    main()

