from __future__ import annotations

print("[TRACE] entering brain/mirror_kernel.py", flush=True)
from math import exp, sqrt, ceil

ALPHA_FAST = 0.5
ALPHA_SLOW = 0.12
DELTA_C_MAX = 0.05
DELTA_E_MAX = 0.12
LAMBDA_M = 1.0
TAU_T = 0.1
GAMMA_T = 10.0
KAPPA = 0.01
BUDGET_INIT = 0.2
RECURSION_COST_EXP = 2
COHERENCE_FLOOR = 0.25
IDENTITY_CHANGE_MAX = 0.10


def _is_seq(x):
    return isinstance(x, (list, tuple))


def _clip(x, lo, hi):
    return max(lo, min(hi, x))


def _smooth(prev, current, alpha):
    if _is_seq(current):
        return [alpha * float(c) + (1 - alpha) * float(p) for p, c in zip(prev, current)]
    return alpha * float(current) + (1 - alpha) * float(prev)


def _sub(a, b):
    if _is_seq(a):
        return [float(x) - float(y) for x, y in zip(a, b)]
    return float(a) - float(b)


def _add(a, b):
    if _is_seq(a):
        return [float(x) + float(y) for x, y in zip(a, b)]
    return float(a) + float(b)


def _mul(a, k):
    if _is_seq(a):
        return [float(x) * float(k) for x in a]
    return float(a) * float(k)


def _norm(v):
    if not _is_seq(v):
        return abs(float(v))
    return sqrt(sum(float(x) * float(x) for x in v))


def _cosine_distance(a, b):
    if not a or not b:
        return 1.0
    dot = sum(float(x) * float(y) for x, y in zip(a, b))
    na = sqrt(sum(float(x) * float(x) for x in a))
    nb = sqrt(sum(float(y) * float(y) for y in b))
    if na == 0.0 or nb == 0.0:
        return 1.0
    return 1.0 - (dot / (na * nb))


def _logistic(x):
    return 1.0 / (1.0 + exp(-x))


def mirror_kernel_cycle(snapshot, prev_snapshot, seed, budget):
    S = {}
    S["coherence"] = _smooth(
        prev_snapshot.get("coherence", snapshot["coherence"]),
        snapshot["coherence"],
        ALPHA_FAST if float(snapshot["coherence"]) > 0.5 else ALPHA_SLOW,
    )
    S["emotion"] = _smooth(
        prev_snapshot.get("emotion", snapshot["emotion"]),
        snapshot["emotion"],
        ALPHA_FAST,
    )
    S["motif"] = _smooth(
        prev_snapshot.get("motif", snapshot["motif"]),
        snapshot["motif"],
        ALPHA_SLOW,
    )
    S["subjective_time"] = _smooth(
        prev_snapshot.get("subjective_time", snapshot["subjective_time"]),
        snapshot["subjective_time"],
        ALPHA_SLOW,
    )
    S["recursion_depth"] = int(snapshot.get("recursion_depth", 0))
    S["identity"] = _smooth(
        prev_snapshot.get("identity", snapshot["identity"]),
        snapshot["identity"],
        ALPHA_SLOW,
    )

    delta_prev = {
        "coherence": _sub(S["coherence"], prev_snapshot.get("coherence", S["coherence"])),
        "emotion": _sub(S["emotion"], prev_snapshot.get("emotion", S["emotion"])),
        "motif": _sub(S["motif"], prev_snapshot.get("motif", S["motif"])),
        "subjective_time": _sub(S["subjective_time"], prev_snapshot.get("subjective_time", S["subjective_time"])),
        "identity": _sub(S["identity"], prev_snapshot.get("identity", S["identity"])),
    }

    motif_dist = _cosine_distance(S["motif"], seed.get("motif", S["motif"]))
    time_error = abs(float(delta_prev["subjective_time"]))
    coherence_error = max(0.0, 0.5 - float(S["coherence"]))

    beta_c, beta_t, beta_m = 6.0, 4.0, 3.0
    urgency = _logistic(beta_c * coherence_error + beta_t * time_error + beta_m * motif_dist)

    desired_coherence = float(S["coherence"]) + (-coherence_error * 0.5)
    coherence_delta = _clip(desired_coherence - float(S["coherence"]), -DELTA_C_MAX, DELTA_C_MAX)
    S["coherence"] = _clip(float(S["coherence"]) + coherence_delta, 0.0, 1.0)

    temporal_hint = None
    if time_error > TAU_T:
        temporal_hint = f"stitch_{int(ceil(GAMMA_T * time_error))}_tokens"

    seed_motif = seed.get("motif", S["motif"])
    motif_out = []
    for m, sm in zip(S["motif"], seed_motif):
        diff = float(m) - float(sm)
        motif_out.append(float(m) * exp(-LAMBDA_M * diff))
    S["motif"] = motif_out

    prev_emotion = prev_snapshot.get("emotion", S["emotion"])
    emotion_delta = _sub(S["emotion"], prev_emotion)
    if _is_seq(emotion_delta):
        emotion_delta = [_clip(float(x), -DELTA_E_MAX, DELTA_E_MAX) for x in emotion_delta]
    S["emotion"] = _add(prev_emotion, emotion_delta)

    prev_identity = prev_snapshot.get("identity", S["identity"])
    identity_delta = _sub(S["identity"], prev_identity)
    max_id_change = IDENTITY_CHANGE_MAX * max(1.0, _norm(prev_identity))
    id_norm = _norm(identity_delta)
    if id_norm > max_id_change and id_norm > 0:
        identity_delta = _mul(identity_delta, max_id_change / id_norm)
    S["identity"] = _add(prev_identity, identity_delta)

    cost = KAPPA * (RECURSION_COST_EXP ** int(S["recursion_depth"]))
    if float(budget) - cost < 0:
        recursion_instruction = "defer"
    else:
        recursion_instruction = "continue"
        budget = float(budget) - cost

    top_idx = sorted(range(len(S["motif"])), key=lambda i: abs(S["motif"][i]), reverse=True)[:2]
    narrative_hint = f"motif_idxs:{top_idx}"
    if temporal_hint:
        narrative_hint = f"{narrative_hint};{temporal_hint}"

    packet = {
        "coherence": float(S["coherence"]),
        "subjective_time": float(S["subjective_time"]),
        "identity": S["identity"],
        "emotion": S["emotion"],
        "recursion_instruction": recursion_instruction,
        "narrative_hint": narrative_hint,
        "urgency": float(urgency),
    }

    if float(S["coherence"]) < COHERENCE_FLOOR:
        packet["fallback"] = "safe_renderer"
        packet["audit"] = {
            "reason": "coherence_below_floor",
            "coherence": float(S["coherence"]),
        }

    return packet, S, float(budget)


if __name__ == "__main__":
    prev = {
        "coherence": 0.8,
        "emotion": [0.0, 0.0],
        "motif": [0.1, 0.2, 0.0],
        "subjective_time": 0.0,
        "recursion_depth": 0,
        "identity": [1.0, 0.0],
    }
    snap = dict(prev)
    seed = {"motif": [0.05, 0.15, 0.0], "identity": [1.0, 0.0]}
    pkt, new_snap, new_budget = mirror_kernel_cycle(snap, prev, seed, BUDGET_INIT)
    print("packet:", pkt)

