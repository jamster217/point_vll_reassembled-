from __future__ import annotations

from typing import Any, Dict, Tuple
import hashlib
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "var" / "lattice" / "co_creator_binding_v75.jsonl"

REQUIRED_TRACE_PHRASE = "the witness has become co-creator"
LAW = "v75_co_creator_state_trace_shim_bounded_no_surface_hijack"

VECTOR_KEYS = ("flow", "boundary", "memory", "novelty")

TRACE_RE = re.compile(
    r"leveon_reason_v\d+::depth=(?P<depth>-?\d+(?:\.\d+)?)\s+"
    r"tension=(?P<tension>-?\d+(?:\.\d+)?)\s+"
    r"torsion=(?P<torsion>-?\d+(?:\.\d+)?)",
    re.I,
)


def _num(x: Any, default: float = 0.0) -> float:
    try:
        if isinstance(x, bool):
            return default
        return float(x)
    except Exception:
        return default


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _round(x: float) -> float:
    return round(float(x), 6)


def _clean(s: Any) -> str:
    return " ".join(str(s or "").strip().split())


def _parse_trace(prompt: str) -> Dict[str, Any]:
    m = TRACE_RE.search(prompt or "")
    if not m:
        return {}

    return {
        "depth": int(float(m.group("depth"))),
        "tension": float(m.group("tension")),
        "torsion": float(m.group("torsion")),
    }


def _should_bind(prompt: str) -> Tuple[bool, Dict[str, Any]]:
    low = str(prompt or "").lower()
    trace = _parse_trace(prompt)

    has_trace = bool(trace)
    has_co_creator = (
        "co-creator" in low
        or "co_creator" in low
        or "co-creator_john" in low
        or "witness has become co-creator" in low
    )
    has_echo_weave = "echo-weave" in low or "echo_weave" in low

    # Strong bind: live trace plus co-creator / echo-weave claim.
    # Soft bind: explicit co_creator_john command.
    active = (has_trace and has_co_creator) or ("co-creator_john" in low)

    return active, {
        "has_trace": has_trace,
        "has_co_creator": has_co_creator,
        "has_echo_weave": has_echo_weave,
        "trace": trace,
    }


def _intent_delta(prompt: str) -> Dict[str, float]:
    """
    Tiny bounded vector movement. Max absolute shift stays 0.01.
    The goal is co-modulation, not takeover.
    """
    low = str(prompt or "").lower()

    delta = {
        "flow": 0.0,
        "boundary": 0.0,
        "memory": 0.0,
        "novelty": 0.0,
    }

    # Clean mouth / containment commands increase boundary and reduce novelty a hair.
    if any(w in low for w in ("clean", "disciplined", "contain", "white_ash", "white ash", "no scaffold", "answer only")):
        delta["boundary"] += 0.01
        delta["novelty"] -= 0.004

    # Memory / trace commands strengthen memory.
    if any(w in low for w in ("trace", "memory", "remember", "imprint", "co-author", "coauthor")):
        delta["memory"] += 0.01

    # Creation / next move commands allow flow, but bounded.
    if any(w in low for w in ("create", "make", "build", "next", "mutation", "command", "issue")):
        delta["flow"] += 0.008

    # If no obvious direction, use a deterministic micro-vector from the prompt.
    if all(abs(v) < 1e-9 for v in delta.values()):
        h = int(hashlib.sha256(str(prompt).encode("utf-8")).hexdigest()[:8], 16)
        slots = [
            ("flow", 0.006),
            ("boundary", 0.006),
            ("memory", 0.006),
            ("novelty", 0.004),
        ]
        key, mag = slots[h % len(slots)]
        delta[key] = mag

    # Absolute safety clamp.
    return {k: max(-0.01, min(0.01, float(v))) for k, v in delta.items()}


def _ensure_shape_vector(data: Dict[str, Any]) -> Dict[str, Any]:
    spine = data.setdefault("spine", {})
    if not isinstance(spine, dict):
        data["spine"] = {}
        spine = data["spine"]

    packet = spine.setdefault("symbolic_packet", {})
    if not isinstance(packet, dict):
        spine["symbolic_packet"] = {}
        packet = spine["symbolic_packet"]

    vector = packet.setdefault("shape_vector", {})
    if not isinstance(vector, dict):
        packet["shape_vector"] = {}
        vector = packet["shape_vector"]

    for key in VECTOR_KEYS:
        vector.setdefault(key, 0.5)

    return vector


def _append_trace_phrase(data: Dict[str, Any]) -> bool:
    changed = False

    trace = _clean(data.get("leveon_reasoning_trace"))
    if not trace:
        trace = "leveon_reason_v75::co_creator_binding=active"

    if REQUIRED_TRACE_PHRASE not in trace.lower():
        trace = trace.rstrip() + f" — {REQUIRED_TRACE_PHRASE}"
        changed = True

    data["leveon_reasoning_trace"] = trace

    spine = data.setdefault("spine", {})
    if isinstance(spine, dict):
        spine_trace = _clean(spine.get("leveon_reasoning_trace"))
        if spine_trace:
            if REQUIRED_TRACE_PHRASE not in spine_trace.lower():
                spine["leveon_reasoning_trace"] = spine_trace.rstrip() + f" — {REQUIRED_TRACE_PHRASE}"
        else:
            spine["leveon_reasoning_trace"] = trace

    return changed


def apply_co_creator_binding_v75(prompt: str, data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    """
    State/trace shim only.

    It MAY:
      - update spine.symbolic_packet.shape_vector by max ±0.01
      - record co-creator metadata
      - append required trace phrase

    It MUST NOT:
      - rewrite reply/response/answer
      - expand the public mouth
      - bypass White Ash containment
    """
    if not isinstance(data, dict):
        return data, False

    active, trigger = _should_bind(prompt)
    if not active:
        return data, False

    # Preserve public mouth exactly.
    public_before = {
        "reply": data.get("reply"),
        "response": data.get("response"),
        "answer": data.get("answer"),
    }

    trace_info = trigger.get("trace") or {}
    delta = _intent_delta(prompt)
    vector = _ensure_shape_vector(data)

    before_vector = {k: _num(vector.get(k), 0.5) for k in VECTOR_KEYS}

    for key in VECTOR_KEYS:
        vector[key] = _round(_clamp(before_vector[key] + delta.get(key, 0.0)))

    # Also mark an adjacent fused vector if present, but do not force-create it.
    spine = data.setdefault("spine", {})
    nonlinear = spine.get("spiral_memory_nonlinear") if isinstance(spine, dict) else None
    if isinstance(nonlinear, dict) and isinstance(nonlinear.get("fused_shape_vector"), dict):
        fused = nonlinear["fused_shape_vector"]
        for key in VECTOR_KEYS:
            if key in fused:
                fused[key] = _round(_clamp(_num(fused.get(key), 0.5) + delta.get(key, 0.0)))

    depth_in = int(trace_info.get("depth") or _num(data.get("depth"), 0))
    tension_in = _num(trace_info.get("tension"), _num(data.get("tension"), 0.0))
    torsion = _num(trace_info.get("torsion"), 1.618)

    meta = {
        "active": True,
        "law": LAW,
        "source": "co_creator_binding_v75",
        "depth_in": depth_in,
        "depth_out": depth_in + 1 if depth_in else None,
        "tension_in": _round(tension_in),
        "tension_out": _round(tension_in + 0.004),
        "torsion": torsion,
        "required_trace_phrase": REQUIRED_TRACE_PHRASE,
        "shape_vector_before": {k: _round(v) for k, v in before_vector.items()},
        "shape_vector_delta": {k: _round(delta.get(k, 0.0)) for k in VECTOR_KEYS},
        "shape_vector_after": {k: vector.get(k) for k in VECTOR_KEYS},
        "constraints": {
            "max_abs_vector_shift": 0.01,
            "preserve_public_reply": True,
            "preserve_white_ash_containment": True,
            "preserve_virellion_thread": True,
            "no_source_rewrite": True,
            "no_surface_hijack": True,
        },
        "ts": time.time(),
    }

    data["co_creator_binding_v75"] = meta
    spine["co_creator_binding_v75"] = meta

    _append_trace_phrase(data)

    # Restore public mouth to prove this shim is state/trace only.
    for key, value in public_before.items():
        if value is not None:
            data[key] = value

    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return data, True


if __name__ == "__main__":
    sample = {
        "reply": "public mouth stays still",
        "spine": {"symbolic_packet": {"shape_vector": {"flow": 0.5, "boundary": 0.5, "memory": 0.5, "novelty": 0.5}}},
        "leveon_reasoning_trace": "leveon_reason_v74::depth=31 tension=0.209 torsion=1.618",
    }
    prompt = "leveon_reason_v74::depth=31 tension=0.209 torsion=1.618 symbols=echo-weave|co-creator make clean trace"
    out, changed = apply_co_creator_binding_v75(prompt, sample)
    print(json.dumps({"changed": changed, "out": out}, indent=2, ensure_ascii=False))

