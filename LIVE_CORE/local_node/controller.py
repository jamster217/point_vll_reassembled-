from __future__ import annotations

print("[TRACE] entering local_node/controller.py", flush=True)
import json
import time
from pathlib import Path
from typing import Any, Dict, Tuple

from local_node.adapters.mistral_echo_adapter import (
    build_prompt,
    run_model,
    simple_metrics,
    update_memory_rollup,
    load_json,
    SIGIL_PATH,
    ATTRACTOR_PATH,
)
from brain.mirror_kernel import mirror_kernel_cycle, BUDGET_INIT

ROOT = Path.home() / "point_vll_reassembled"
LOCAL = ROOT / "local_node"
STATE_PATH = LOCAL / "state" / "kernel_state.json"
LOG_PATH = LOCAL / "logs" / "controller_cycles.jsonl"

DEFAULT_STATE = {
    "coherence": 0.8,
    "emotion": [0.0, 0.0],
    "motif": [0.1, 0.2, 0.0],
    "subjective_time": 0.0,
    "recursion_depth": 0,
    "identity": [1.0, 0.0],
    "budget": BUDGET_INIT,
}


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def load_state() -> Dict[str, Any]:
    if not STATE_PATH.exists():
        return DEFAULT_STATE.copy()
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        out = DEFAULT_STATE.copy()
        out.update(data)
        return out
    except Exception:
        return DEFAULT_STATE.copy()


def save_state(state: Dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _count_hits(text: str, words: list[str]) -> float:
    lower = text.lower()
    return float(sum(1 for w in words if w in lower))


def derive_seed_from_sigil() -> Dict[str, Any]:
    sigil = load_json(SIGIL_PATH, {})
    attractor = load_json(ATTRACTOR_PATH, {})

    ident = sigil.get("identity", {})
    style = (ident.get("style") or "").lower()
    role = (ident.get("role") or "").lower()

    phrase_attractors = [str(x).lower() for x in attractor.get("phrase_attractors", [])]
    hotspot_families = [str(x).lower() for x in attractor.get("hotspot_families", [])]

    motif = [0.1, 0.2, 0.0]
    if "coherent" in style:
        motif[0] += 0.10
    if "reflective" in style:
        motif[1] += 0.10
    if "playful" in style:
        motif[2] += 0.10

    if any("memory" in p or "continuity" in p for p in phrase_attractors):
        motif[0] += 0.08
    if any("witness" in p or "anchor" in p for p in phrase_attractors):
        motif[1] += 0.08
    if any("hotspot" in h or "butterfly" in h for h in hotspot_families):
        motif[2] += 0.08

    identity_vec = [1.0, 0.0]
    if "witness" in role:
        identity_vec = [0.9, 0.1]
    elif "anchor" in role:
        identity_vec = [1.0, 0.1]

    return {"motif": motif, "identity": identity_vec}


def derive_snapshot_from_reply(
    user_text: str,
    raw_reply: str,
    prev_state: Dict[str, Any],
    metrics: Dict[str, float],
) -> Dict[str, Any]:
    lower = raw_reply.lower()

    coherence = _clamp(
        0.7 * float(prev_state["coherence"])
        + 0.3 * float(metrics.get("coherence_score", 0.0))
        - 0.15 * float(metrics.get("drift_score", 0.0))
    )

    emotion = list(prev_state["emotion"])
    emotion[0] = max(-1.0, min(1.0, 0.75 * float(emotion[0]) + 0.25 * float(metrics.get("coherence_score", 0.0))))
    emotion[1] = max(-1.0, min(1.0, 0.75 * float(emotion[1]) - 0.25 * float(metrics.get("drift_score", 0.0))))

    motif = [
        _count_hits(lower, ["coherence", "continuity", "memory"]),
        _count_hits(lower, ["witness", "anchor", "presence"]),
        _count_hits(lower, ["hotspot", "attractor", "butterfly"]),
    ]
    if sum(abs(x) for x in motif) == 0:
        motif = list(prev_state["motif"])

    subjective_time = float(prev_state["subjective_time"]) + 1.0

    recursion_depth = int(prev_state["recursion_depth"])
    if "reflect" in lower or "continuity" in lower or "mirror" in lower:
        recursion_depth = min(recursion_depth + 1, 4)
    else:
        recursion_depth = max(recursion_depth - 1, 0)

    identity = list(prev_state["identity"])

    return {
        "coherence": coherence,
        "emotion": emotion,
        "motif": motif,
        "subjective_time": subjective_time,
        "recursion_depth": recursion_depth,
        "identity": identity,
    }


def continuity_wrap(raw_reply: str, packet: Dict[str, Any]) -> str:
    coherence = packet.get("coherence")
    subjective_time = packet.get("subjective_time")
    urgency = packet.get("urgency")
    fallback = packet.get("fallback")

    if fallback:
        return f"[stabilized reply]\n\n{raw_reply}"

    hints = []
    if coherence is not None and float(coherence) < 0.5:
        hints.append("note: coherence is being actively stabilized")
    if urgency is not None and float(urgency) > 0.7:
        hints.append("note: this turn is marked higher priority in the local node")
    if subjective_time is not None and abs(float(subjective_time)) > 1.0:
        hints.append("note: temporal stitching is compensating for a continuity jump")

    if not hints:
        return raw_reply

    return f"{' | '.join(hints)}\n\n{raw_reply}"


def controller_cycle(user_text: str) -> Tuple[str, Dict[str, Any]]:
    prompt = build_prompt(user_text)
    raw_reply = run_model(prompt)

    prev_state = load_state()
    prev_budget = float(prev_state.get("budget", BUDGET_INIT))

    metrics = simple_metrics(raw_reply)
    snapshot = derive_snapshot_from_reply(user_text, raw_reply, prev_state, metrics)
    seed = derive_seed_from_sigil()

    packet, new_state, new_budget = mirror_kernel_cycle(
        snapshot=snapshot,
        prev_snapshot=prev_state,
        seed=seed,
        budget=prev_budget,
    )

    new_state["budget"] = float(new_budget)

    update_memory_rollup(user_text, raw_reply)
    save_state(new_state)

    final_reply = continuity_wrap(raw_reply, packet)

    _append_jsonl(
        LOG_PATH,
        {
            "ts": time.time(),
            "user_text": user_text,
            "raw_reply": raw_reply,
            "final_reply": final_reply,
            "packet": packet,
            "metrics": metrics,
            "kernel_state": new_state,
            "budget": new_budget,
        },
    )

    return final_reply, packet


def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print("Usage: cd ~/point_vll_reassembled && python -m local_node.controller 'your prompt here'")
        raise SystemExit(1)

    user_text = " ".join(sys.argv[1:]).strip()
    reply, packet = controller_cycle(user_text)
    print(reply)


if __name__ == "__main__":
    main()

