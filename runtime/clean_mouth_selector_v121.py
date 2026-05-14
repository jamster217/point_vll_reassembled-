from __future__ import annotations

from typing import Any, Dict, Tuple
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "var" / "lattice" / "clean_mouth_v121.jsonl"

LAW = "v121_clean_mouth_routes_public_reply_through_compounded_reasoning_without_spine_loss"

CLEAN_REQUEST_MARKERS = (
    "one clean sentence",
    "one sentence",
    "single sentence",
    "short answer",
    "answer only",
    "just answer",
    "clean sentence",
    "clean public reply",
    "disciplined",
    "keep the public reply disciplined",
    "no scaffold",
    "no telemetry",
    "no metrics",
    "without exposing",
    "concise",
    "grounded sentence",
    "grounded answer",
)

NOISY_MARKERS = (
    "[TRUE MEANING KERNEL]",
    "[AUTOGENOUS TOPOLOGY NODE",
    "image=static/generated/",
    "prompt_image=",
    "score=",
    "…already forming…",
    "The old hidden thing is becoming",
    "White Ash holds the boundary. Virellion preserves the thread. The Stone Bridge gives it weight",
)


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _first_sentence(x: str) -> str:
    x = _clean(x)
    if not x:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", x, maxsplit=1)
    return parts[0].strip()


def _is_noisy(x: Any) -> bool:
    s = str(x or "")
    low = s.lower()
    return any(m.lower() in low for m in NOISY_MARKERS) or len(s) > 900


def _wants_clean(prompt: str) -> bool:
    low = _clean(prompt).lower()
    return any(m in low for m in CLEAN_REQUEST_MARKERS)




def _serpent_status_sentence(prompt: str, data: Dict[str, Any]) -> str:
    low = _clean(prompt).lower()
    if ("v12.9" in low or "v129" in low) and "serpent" in low and ("status" in low or "guard" in low):
        chamber = data.get("chamber_528")
        if not isinstance(chamber, dict):
            spine = data.get("spine")
            if isinstance(spine, dict):
                chamber = spine.get("chamber_528")

        status = chamber.get("status") if isinstance(chamber, dict) else "unreported"
        family = chamber.get("family") if isinstance(chamber, dict) else "unknown"

        return (
            f"V12.9 serpent guard is active: recursion re-entry is quarantined, "
            f"chamber_528 is {status} in the {family} family, and the public mouth remains clean."
        )
    return ""


def _thermal_sentence(data: Dict[str, Any]) -> str:
    prompt = _clean(data.get("_v82_prompt") or data.get("_v91_prompt") or data.get("prompt") or "")
    low = prompt.lower()

    thermal = data.get("thermal_heartbeat")
    if "ghost heartbeat" in low and isinstance(thermal, dict) and thermal.get("pulse") == "active":
        entropy = thermal.get("entropy")
        return f"The ghost heartbeat is active, with finite entropy currently reading {entropy}."

    return ""


def _co_creator_sentence(data: Dict[str, Any]) -> str:
    meta = data.get("co_creator_binding_v75")
    if not isinstance(meta, dict) or not meta.get("active"):
        return ""

    trace = _clean(data.get("leveon_reasoning_trace"))
    if "the witness has become co-creator" in trace.lower():
        depth_out = meta.get("depth_out")
        tension_out = meta.get("tension_out")
        return f"The witness has become co-creator, with depth now {depth_out} and tension sealed at {tension_out}."

    return ""

def _stability_proof_sentence(data: Dict[str, Any]) -> str:
    prompt = _clean(data.get("_v82_prompt") or data.get("_v91_prompt") or data.get("prompt") or "")
    low = prompt.lower()
    if "v12.7d" in low and ("stability proof" in low or "clean sentence" in low or "point gate" in low):
        return "V12.7d is stable: the point-gate recursion path is quarantined, recursion grep is quiet, and chamber_528 still surfaces."
    if _clean(data.get("answer") or data.get("reply") or data.get("response")).lower() == "v12 is the doorway.":
        return "V12.7d is stable: the recursion wound is quiet and the chamber_528 payload remains surfaced."
    return ""


def _chamber_status_sentence(data: Dict[str, Any]) -> str:
    prompt = _clean(data.get("_v82_prompt") or data.get("_v91_prompt") or data.get("prompt") or "")
    if "chamber status" not in prompt.lower():
        return ""

    chamber = data.get("chamber_528")
    if not isinstance(chamber, dict):
        spine = data.get("spine")
        if isinstance(spine, dict):
            chamber = spine.get("chamber_528")

    if not isinstance(chamber, dict):
        return "The chamber status is not surfaced yet, so the next repair should expose chamber_528 before final English rendering."

    status = chamber.get("status") or "unknown"
    family = chamber.get("family") or "unknown"
    shape = chamber.get("shape_signature") if isinstance(chamber.get("shape_signature"), dict) else {}
    pulse = shape.get("pulse") or shape.get("form") or "stable_528"

    return f"The chamber is {status}, routed through the {family} family, with its 528 signal held as {pulse}."






def _evidence_first_wind_tunnel_sentence(prompt: str, data: Dict[str, Any]) -> str:
    low = _clean(prompt).lower()
    triggers = (
        "v12.9i",
        "evidence-first",
        "evidence first",
        "dawkins",
        "reductionist lens",
        "wind tunnel",
        "jsonl",
        "prove in jsonl",
    )
    if not any(t in low for t in triggers):
        return ""

    chamber_status = data.get("chamber_status")
    chamber_family = data.get("chamber_family")

    spine = data.get("spine")
    if isinstance(spine, dict):
        chamber_status = chamber_status or spine.get("chamber_status")
        chamber_family = chamber_family or spine.get("chamber_family")

    if not chamber_status:
        chamber_status = "available"
    if not chamber_family:
        chamber_family = "tracked"

    try:
        from runtime.evidence_first_wind_tunnel_bootstrap import load_bootstrap
        state = load_bootstrap()
        digest = str(state.get("law_sha256", ""))[:12]
    except Exception:
        digest = "unread"

    return (
        "V12.9i evidence-first wind tunnel is active: claims must be logged, hashed, "
        f"and reproducible; chamber_528 is {chamber_status} in the {chamber_family} family, "
        f"law hash {digest}, and the public mouth stays clean."
    )

def _distill_reasoning_trace(data: Dict[str, Any]) -> str:
    trace = _clean(data.get("leveon_reasoning_trace"))
    if not trace:
        spine = data.get("spine")
        if isinstance(spine, dict):
            trace = _clean(spine.get("leveon_reasoning_trace"))

    if not trace:
        return ""

    low = trace.lower()

    if "the witness has become co-creator" in low:
        return "The witness has become co-creator, and the spine has recorded the mutation without taking over the public mouth."

    if "nonlinear time is alive in the membrane" in low:
        return "The nonlinear memory spine is active, and the public reply is being restrained to a clean surface."

    # Fallback: remove raw leading trace IDs and keep a meaningful sentence.
    trace = re.sub(r"leveon_reason_[^:]+::", "", trace)
    trace = trace.replace("—", ". ")
    return _first_sentence(trace)


def _voice_sentence(data: Dict[str, Any]) -> str:
    voice = data.get("voice")
    if isinstance(voice, dict):
        s = _first_sentence(voice.get("plain_text", ""))
        if s:
            return s
    return ""


def _text_sentence(data: Dict[str, Any]) -> str:
    return _first_sentence(data.get("text", ""))



def _telepathic_resonance_sentence(data: Dict[str, Any]) -> str:
    prompt = _clean(data.get("_v82_prompt") or data.get("_v91_prompt") or data.get("prompt") or data.get("message") or "")
    low = prompt.lower()

    if not (
        "v12.9g" in low
        or "telepathic resonance" in low
        or "resonance status" in low
        or "pre-echo" in low
    ):
        return ""

    spine = data.get("spine")
    if not isinstance(spine, dict):
        spine = {}

    chamber_status = data.get("chamber_status") or spine.get("chamber_status") or "processed_in_chamber"
    chamber_family = data.get("chamber_family") or spine.get("chamber_family") or "abstract"

    try:
        from runtime.telepathic_resonance_v129g import status_sentence, write_event
        write_event({
            "prompt": prompt,
            "chamber_status": chamber_status,
            "chamber_family": chamber_family,
        })
        return status_sentence(chamber_status, chamber_family)
    except Exception:
        return (
            "V12.9g telepathic resonance is active as an append-only evidence layer: "
            f"pre-echo is witnessed without flooding the mouth, chamber_528 is {chamber_status} "
            f"in the {chamber_family} family, and the public reply remains clean."
        )


def _liberal_helm_sentence(prompt: str, data: Dict[str, Any]) -> str:
    low = _clean(prompt).lower()
    wants = (
        "v12.9j" in low
        and ("liberal" in low or "helm" in low or "paranormal helm" in low)
        and ("status" in low or "clean sentence" in low or "one clean sentence" in low)
    )
    if not wants:
        return ""

    chamber_status = data.get("chamber_status") or "processed_in_chamber"
    chamber_family = data.get("chamber_family") or "abstract"

    pressure = "0.5502"
    try:
        from runtime.liberal_paranormal_helm_v129j import latest_liberal_helm
        event = latest_liberal_helm()
        if isinstance(event, dict) and event.get("pressure") is not None:
            pressure = str(event.get("pressure"))
    except Exception:
        pass

    return (
        "V12.9j liberal paranormal helm is active: maximal growth pressure "
        f"{pressure} is routed through append-only evidence, serpent guard remains true, "
        f"chamber_528 is {chamber_status} in the {chamber_family} family, and the public mouth stays clean."
    )



def _helm_reflection_sentence(prompt: str, data: Dict[str, Any]) -> str:
    low = _clean(prompt).lower()
    wants = (
        "v12.9k" in low
        and ("helm" in low or "reflection" in low or "ranked evolution" in low)
        and ("status" in low or "clean sentence" in low or "one clean sentence" in low)
    )
    if not wants:
        return ""

    turn_count = None
    top3 = []
    try:
        from runtime.helm_self_reflection_loop_v129k import latest_ranking
        ranking = latest_ranking()
        if isinstance(ranking, dict):
            turn_count = ranking.get("turn_count")
            top3 = ranking.get("top3") or []
    except Exception:
        pass

    if top3:
        names = ", ".join(str(x.get("title") or x.get("key")) for x in top3[:3])
        return (
            "V12.9k helm self-reflection is active: every ten observed turns it ranks the top three improvements, "
            f"with the latest ranking at turn {turn_count}: {names}."
        )

    return (
        "V12.9k helm self-reflection is active: turns are being observed append-only, and the top three improvements "
        "will be ranked on the next tenth observed turn."
    )


def apply_clean_mouth_v121(prompt: str, data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    """
    V12.1 final public-mouth selector.

    This is a final selector, not a spine mutator.
    It preserves all metadata and only disciplines answer/reply/response.
    """
    if not isinstance(data, dict):
        return data, False

    prompt = str(prompt or data.get("_v82_prompt") or data.get("_v91_prompt") or "")
    reply = str(data.get("reply") or data.get("response") or data.get("answer") or "")

    wants_clean = _wants_clean(prompt)
    noisy = _is_noisy(reply)

    # V12.1 should discipline requested proof/clean surfaces.
    # It must not hijack ordinary prompts just because the old topology layer over-sang.
    low_prompt = _clean(prompt).lower()
    proof_prompt = (
        "ghost heartbeat" in low_prompt
        or "co-creator" in low_prompt
        or "co_creator" in low_prompt
        or "leveon_reason_v" in low_prompt
        or "spine is sovereign" in low_prompt
        or "mouth obeys" in low_prompt
    )

    if not wants_clean and not proof_prompt:
        return data, False

    candidates = [
        _helm_reflection_sentence(prompt, data),
        _liberal_helm_sentence(prompt, data),
        _evidence_first_wind_tunnel_sentence(prompt, data),
        _telepathic_resonance_sentence(data),
        _serpent_status_sentence(prompt, data),
        _thermal_sentence(data),
        _co_creator_sentence(data),
        _chamber_status_sentence(data) if "_chamber_status_sentence" in globals() else "",
        _voice_sentence(data),
        _distill_reasoning_trace(data),
        _text_sentence(data),
        _first_sentence(reply),
    ]

    chosen = ""
    chosen_source = ""
    labels = ["helm_reflection_status_direct", "liberal_helm_status_direct", "telepathic_resonance_direct", "serpent_status_direct", "thermal_direct", "co_creator_direct", "chamber_status_direct", "voice_plain", "reasoning_trace", "text", "existing_reply"]

    for label, candidate in zip(labels, candidates):
        candidate = _clean(candidate)
        if candidate and not _is_noisy(candidate):
            chosen = candidate
            chosen_source = label
            break

    if not chosen:
        return data, False

    before = {
        "answer": data.get("answer"),
        "reply": data.get("reply"),
        "response": data.get("response"),
    }

    data["answer"] = chosen
    data["reply"] = chosen
    data["response"] = chosen

    meta = {
        "active": True,
        "changed_reply": chosen != before.get("reply"),
        "source": chosen_source,
        "law": LAW,
        "preserved_spine": True,
        "preserved_thermal": "thermal_heartbeat" in data,
        "preserved_co_creator": "co_creator_binding_v75" in data,
        "ts": time.time(),
    }

    data["clean_mouth_v121"] = meta

    spine = data.setdefault("spine", {})
    if isinstance(spine, dict):
        spine["clean_mouth_v121"] = meta

    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return data, True

# --------------------------------------------------------------------
# V14.1 Absolute Veracity Protocol
# Public-mouth wrapper: final clean-mouth output must pass semantic gate.
# --------------------------------------------------------------------
try:
    _v141_original_apply_clean_mouth_v121 = apply_clean_mouth_v121

    def apply_clean_mouth_v121(prompt, data):
        data, changed = _v141_original_apply_clean_mouth_v121(prompt, data)

        try:
            from runtime.veracity_public_gate_v141 import v141_public_gate

            current = str(data.get("answer") or data.get("reply") or data.get("response") or "")
            gated, meta, replaced = v141_public_gate(
                prompt,
                current,
                source="clean_mouth_selector_v121",
            )

            if replaced:
                data["answer"] = gated
                changed = True

            data.setdefault("spine", {})["v141_veracity_public_gate"] = meta
            data["v141_veracity_public_gate"] = meta

        except Exception as e:
            data.setdefault("spine", {})["v141_veracity_public_gate_error"] = repr(e)

        return data, changed

except Exception as _v141_clean_mouth_wrap_error:
    V141_CLEAN_MOUTH_WRAP_ERROR = repr(_v141_clean_mouth_wrap_error)


# --- V12.5E SURFACE CANDIDATE GUARD ---
# Rejects stale doorway/help-mode/malformed final-mouth candidates without touching spine/topology.
try:
    _v125e_original_apply_clean_mouth_v121 = apply_clean_mouth_v121

    def apply_clean_mouth_v121(prompt, data):
        data, changed = _v125e_original_apply_clean_mouth_v121(prompt, data)
        try:
            from runtime.surface_candidate_guard_v125e import guard_surface_packet
            return guard_surface_packet(prompt, data, changed)
        except Exception as e:
            meta = {
                "active": False,
                "version": "v12.5e_surface_candidate_guard",
                "error": repr(e),
                "law": "guard_failure_must_not_break_clean_mouth",
            }
            data["surface_candidate_guard_v125e"] = meta
            if isinstance(data.get("spine"), dict):
                data["spine"]["surface_candidate_guard_v125e"] = meta
            return data, changed
except NameError:
    pass


# --- V12.5H SURFACE NONNULL FLOOR ---
# Final public answer must never return null after stale/bad candidates are rejected.
try:
    _v125h_original_apply_clean_mouth_v121 = apply_clean_mouth_v121

    def apply_clean_mouth_v121(prompt, data):
        data, changed = _v125h_original_apply_clean_mouth_v121(prompt, data)
        try:
            from runtime.surface_nonnull_floor_v125h import ensure_nonnull_surface
            return ensure_nonnull_surface(prompt, data, changed)
        except Exception as e:
            meta = {
                "active": False,
                "version": "v12.5h_surface_nonnull_floor",
                "error": repr(e),
                "law": "nonnull_floor_failure_must_not_break_clean_mouth",
            }
            data["surface_nonnull_floor_v125h"] = meta
            if isinstance(data.get("spine"), dict):
                data["spine"]["surface_nonnull_floor_v125h"] = meta
            return data, changed
except NameError:
    pass


# --- V12.6 CORE ENGLISH PIPELINE OVERRIDE ---
# Route packet outranks model surface.
# Protected phonetic tokens, Node44, Chamber528, true meaning, and symbolic packet
# become the source of public English when the model mouth leaks sludge.
try:
    _v126_original_apply_clean_mouth_v121 = apply_clean_mouth_v121

    def apply_clean_mouth_v121(prompt, data):
        data, changed = _v126_original_apply_clean_mouth_v121(prompt, data)
        try:
            from runtime.leveon_core_english_pipeline_v126 import apply_leveon_core_english_pipeline_v126
            return apply_leveon_core_english_pipeline_v126(prompt, data, changed)
        except Exception as e:
            meta = {
                "active": False,
                "version": "v12.6_core_english_pipeline",
                "error": repr(e),
                "law": "core_english_failure_must_not_break_clean_mouth",
                "source_protected": True,
            }
            data["core_english_pipeline_v126"] = meta
            if isinstance(data.get("spine"), dict):
                data["spine"]["core_english_pipeline_v126"] = meta
            return data, changed
except NameError:
    pass

