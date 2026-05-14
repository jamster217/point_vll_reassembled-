from __future__ import annotations

print("[TRACE] entering runtime/run_analysis_profile.py", flush=True)
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Tuple

from artifacts.analysis.route_comparison_artifact import compare_routes
from artifacts.analysis.memory_pressure_sim_artifact import simulate_memory_pressure
from artifacts.analysis.hotspot_transition_map_artifact import map_hotspot_transitions
from artifacts.analysis.self_critique_loop_artifact import run_self_critique

from runtime.leveon_pipeline_with_spiral_memory import leveon_pipeline
from core.hybrid_shape_bridge import render_via_shape_kernel
from core.shape_signal_policy import should_use_shape_kernel
from core.conceptual_domain_policy import promoted_conceptual_domain
from language_realizer import render_from_route


COMPETITIVE_DOMAINS = [
    "structure",
    "memory_structure",
    "memory_emotional",
    "balancing",
    "balancing_structure",
    "causal",
    "causal_emotional",
    "emotional_depth",
    "lattice",
]


def _run_live_prompt(prompt: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
    out = leveon_pipeline({
        "text": prompt,
        "tone": "neutral",
        "mirror_mode": "contained",
        "hotspot_history": [],
    })
    meta = out.get("meta", {}) or {}
    lp = meta.get("language_pass", {}) or {}
    return out, lp


def _domain_score(domain: str) -> float:
    return {
        "emotional_depth": 0.84,
        "causal": 0.83,
        "causal_emotional": 0.82,
        "memory_emotional": 0.81,
        "structure": 0.80,
        "memory_structure": 0.79,
        "balancing": 0.80,
        "balancing_structure": 0.79,
        "lattice": 0.79,
    }.get(domain or "", 0.72)



def _prompt_domain_bonus(prompt: str, domain: str) -> float:
    t = (prompt or "").lower()
    d = domain or ""

    bonus = 0.0

    is_causal_surface = any(x in t for x in (
        "underneath",
        "surface words",
        "what is really shaping",
        "what is shaping",
    ))
    is_causal_force = any(x in t for x in (
        "tone stop being mood",
        "start becoming a force",
        "becoming a force",
        "tone",
        "force",
    ))
    is_memory_reactivation = any(x in t for x in (
        "small reminder",
        "emotional field",
        "whole emotional field",
        "same weight",
        "return",
        "returns",
    ))

    if d == "memory_emotional":
        if "small reminder" in t:
            bonus += 0.14
        if "emotional field" in t or "whole emotional field" in t:
            bonus += 0.12
        if "same weight" in t or "return" in t or "returns" in t:
            bonus += 0.08

    if d == "causal":
        if "tone stop being mood" in t:
            bonus += 0.12
        if "start becoming a force" in t or "becoming a force" in t:
            bonus += 0.12
        if "tone" in t and "force" in t:
            bonus += 0.08

    if d == "causal_emotional":
        if "surface words" in t or "underneath" in t:
            bonus += 0.08
        if "small reminder" in t:
            bonus -= 0.10
        if "emotional field" in t or "whole emotional field" in t:
            bonus -= 0.08
        if "tone stop being mood" in t or "start becoming a force" in t:
            bonus -= 0.12

    if d == "structure":
        if is_memory_reactivation:
            bonus -= 0.22
        if "small reminder" in t:
            bonus -= 0.06
        if "emotional field" in t or "whole emotional field" in t:
            bonus -= 0.06
        if is_causal_surface:
            bonus -= 0.10
        if is_causal_force:
            bonus -= 0.12

    if d == "memory_structure":
        if is_memory_reactivation:
            bonus -= 0.06
        if is_causal_surface:
            bonus -= 0.08
        if is_causal_force:
            bonus -= 0.10

    return bonus


def _candidate_domains_from_prompt(prompt: str, live_domain: str) -> List[str]:
    t = (prompt or "").lower()
    out: List[str] = []

    def add(domain: str) -> None:
        if domain and domain not in out:
            out.append(domain)

    add(live_domain)

    promoted = promoted_conceptual_domain(prompt, "basic_query")
    if promoted != "basic_query":
        add(promoted)

    emotional_markers = (
        "grief", "miss", "dad", "father", "mother", "love", "loss", "trust",
        "space", "distance", "protective", "feeling", "ache", "closeness",
        "longing", "hope", "hurt", "boundary", "cold"
    )
    structure_markers = (
        "structure", "coherence", "constraint", "constraints", "layers", "form",
        "shape"
    )
    memory_markers = (
        "memory", "anchor", "anchors", "continuity", "remember", "reminder",
        "return", "returns", "reactivate", "old memory", "same weight"
    )
    causal_markers = (
        "causal", "tone", "pressure", "reaction", "underneath", "surface words",
        "steering", "steer", "what is really shaping", "what shapes", "what is shaping",
        "before i do", "before i have chosen", "force", "field",
        "why does", "why does this", "change", "becoming a force",
        "start becoming", "emotional field", "whole emotional field"
    )
    guarded_markers = (
        "space", "distance", "boundary", "boundaries", "protective", "protect",
        "protect itself", "pulling back", "back away", "erase the love",
        "do not trust", "don't trust", "came back", "turning cold", "cruelty"
    )
    balance_markers = (
        "balance", "clarity", "depth", "drift", "more than one demand",
        "competing goals", "collapse"
    )

    strong_causal_markers = (
        "why does", "tone stop being mood", "start becoming a force",
        "small reminder", "emotional field", "whole emotional field",
        "steering me", "before i have chosen", "before i do"
    )

    strong_causal_pure_markers = (
        "tone stop being mood",
        "start becoming a force",
        "tone",
        "force",
        "steering",
        "what is shaping",
        "what is really shaping"
    )

    strong_causal_memory_markers = (
        "small reminder",
        "reminder",
        "whole emotional field",
        "emotional field",
        "same weight",
        "returns",
        "return with"
    )

    strong_structure_markers = (
        "keep coherence", "coherence", "layers", "constraints", "holds form together",
        "form together", "answer-shape", "shape from drifting"
    )

    is_emotional = any(x in t for x in emotional_markers)
    is_structural = any(x in t for x in structure_markers)
    is_memory = any(x in t for x in memory_markers)
    is_causal = any(x in t for x in causal_markers)
    is_guarded = any(x in t for x in guarded_markers)
    is_balancing = any(x in t for x in balance_markers)

    strong_causal = any(x in t for x in strong_causal_markers)
    strong_causal_pure = any(x in t for x in strong_causal_pure_markers)
    strong_causal_memory = any(x in t for x in strong_causal_memory_markers)
    strong_structure = any(x in t for x in strong_structure_markers)

    if is_emotional or live_domain == "emotional_depth":
        add("emotional_depth")
        add("memory_emotional")
        add("causal_emotional")

    if is_guarded:
        add("emotional_depth")
        add("memory_emotional")
        add("balancing")

    if is_memory:
        add("memory_emotional")
        add("memory_structure")

    if is_causal:
        add("causal")
        add("causal_emotional")
        add("memory_emotional")

    if is_structural:
        add("structure")
        add("memory_structure")
        add("balancing_structure")

    if is_balancing:
        add("balancing")
        add("balancing_structure")

    if "lattice" in t:
        add("lattice")
        add("structure")

    if is_guarded and ("miss" in t or "loss" in t or "love" in t):
        add("memory_emotional")
        add("causal_emotional")
        add("balancing")

    if is_structural and is_emotional:
        add("structure")
        add("balancing_structure")
        add("memory_structure")

    if is_memory and is_causal:
        add("memory_emotional")
        add("causal")
        add("causal_emotional")

    for d in COMPETITIVE_DOMAINS:
        if len(out) >= 8:
            break
        if d not in out:
            if is_causal and d in {"causal", "causal_emotional", "memory_emotional"}:
                add(d)
            elif is_guarded and d in {"emotional_depth", "memory_emotional", "balancing"}:
                add(d)
            elif is_structural and d in {"structure", "memory_structure", "balancing_structure", "causal"}:
                add(d)
            elif is_memory and d in {"memory_structure", "memory_emotional", "structure"}:
                add(d)

    # hard promote the right family for the strongest query shapes
    if strong_causal_pure and not strong_causal_memory:
        prioritized = ["causal", "causal_emotional", "structure"]
        out = prioritized + [d for d in out if d not in prioritized]

    elif strong_causal_memory:
        prioritized = ["memory_emotional", "causal_emotional", "causal"]
        out = prioritized + [d for d in out if d not in prioritized]

    elif strong_causal:
        prioritized = ["causal_emotional", "causal", "memory_emotional"]
        out = prioritized + [d for d in out if d not in prioritized]

    elif strong_structure:
        prioritized = ["structure", "memory_structure", "balancing_structure"]
        out = prioritized + [d for d in out if d not in prioritized]

    return [d for d in out if d]

def _render_domain_candidate(prompt: str, domain: str) -> str:
    t = (prompt or "").strip()

    if domain == "emotional_depth":
        if any(x in t.lower() for x in ["dad", "father", "grief", "miss"]):
            return "Something in it reaches toward closeness, with a quiet sense of soft ache."
        if any(x in t.lower() for x in ["boundary", "distance", "space", "protect", "protective"]):
            return "There is a gentle need for distance, with a quiet sense of protective care."
        return "What you said seems to carry feeling that wants to be met before it is explained."

    if domain == "memory_emotional":
        low = t.lower()
        if "small reminder" in low or "emotional field" in low:
            return "One small reminder can change the whole emotional field when it reactivates older feeling that was already waiting beneath the surface. Then the moment is no longer carrying only the present; it is carrying what the reminder woke back up."
        return "What is shaping this is not only the present moment. Older feeling is getting reactivated, so the reaction arrives with memory already inside it."

    if domain == "causal_emotional":
        low = t.lower()
        if "surface words" in low or "underneath" in low:
            return "What is underneath the surface words is not just the feeling itself, but the pressure pattern shaping how the feeling forms. Tone, expectation, and memory are all helping decide the route before the explanation fully arrives."
        if "tone" in low and "force" in low:
            return "Tone starts becoming a force when it no longer just colors the moment, but begins steering what the system reaches for next. Then mood turns into pressure that can influence the route itself."
        return "The feeling changes the route because tone, expectation, and memory start steering what the system reaches for next. That is why the answer can bend before the words fully form."

    if domain == "memory_structure":
        low = t.lower()
        if "tone" in low and "force" in low:
            return "Tone becomes a force when remembered patterns start pre-shaping the route before you consciously choose it. Then mood is no longer just present; it is helping decide what comes next."
        if "surface words" in low or "underneath" in low:
            return "What is shaping the reaction underneath the surface words is the interaction between stored anchors and active constraints. Older patterning is deciding what rises first, which is why the reaction can feel stronger than the moment itself."
        if "memory pressure" in low or "holds form" in low:
            return "What holds form together when memory pressure rises is structure. Memory keeps reactivating the same routes, and structure is what keeps that pressure from scattering the whole response."
        return "Memory and structure work together when stored anchors keep influencing which constraints stay active. That is how continuity can shape the response before deliberate choice catches up."

    if domain == "structure":
        return "A system keeps coherence by deciding what can combine, what must stay separate, and when a layer has gone far enough. That is what stops feeling from bending the route so far that the answer loses its shape."

    if domain == "causal":
        if any(x in t.lower() for x in ["small reminder", "emotional field", "same weight", "close to it"]):
            return "One small reminder can change the whole emotional field when it touches a live chain underneath the surface. Then it is not just a detail entering the moment; it is reactivating a larger route that was already waiting."
        if "tone" in t.lower() and "force" in t.lower():
            return "Tone stops being just mood when it begins steering what feels possible, what feels distant, and which path the response can take. At that point it is helping choose the outcome, not only color it."
        return "Causality appears when one active pressure begins steering the route instead of merely coloring the experience."

    if domain == "balancing":
        return "Clarity and depth hold each other together when the answer names the center first, then opens wider without leaving it. Depth should make the line truer, not harder to follow."

    if domain == "balancing_structure":
        return "Drift is prevented when clarity keeps the answer anchored while depth keeps it alive. The reply can move and deepen, but it should not wander away from what it is really answering."

    if domain == "basic_query":
        return "Answer it directly in terms of structure, memory, time, emotion, and relation."

    if domain == "lattice":
        return "The lattice is the relation map that shapes which paths become available before an answer settles into words."

    return "Answer it directly in terms of structure, memory, time, emotion, and relation."

def _default_hotspot_trace(prompt: str, live_domain: str = ""):
    t = (prompt or "").lower()
    d = (live_domain or "").lower()

    if d == "emotional_depth" or any(x in t for x in ("memory", "dad", "grief", "loss", "space", "trust")):
        return ["H_1224", "H_1314", "H_1224", "H_3134", "H_1314"]
    if any(x in t for x in ("structure", "coherence", "lattice", "causal")):
        return ["H_2224", "H_1224", "H_1314", "H_1314", "H_3134"]
    return ["H_1224", "H_1314", "H_3134"]



def _winner_final_english(out: dict) -> str:
    artifacts = out.get("artifacts", {}) or {}
    route_compare = artifacts.get("route_compare", {}) or {}
    winner = route_compare.get("best_route", {}) or {}
    return str(winner.get("final_english", "") or "").strip()

def _default_draft_output(prompt: str):
    t = (prompt or "").lower()
    if any(x in t for x in ("grief", "miss", "dad")):
        return "Something in it reaches toward closeness, with a quiet sense of soft ache."
    if any(x in t for x in ("space", "distance", "protective")):
        return "There is a gentle need for space, with a quiet sense of protective distance."
    if any(x in t for x in ("structure", "coherence")):
        return "Structure supports coherence by limiting how layers combine and resolve."
    return "That is a conceptual question. Answer it directly in terms of structure."



def _decision_strength(score_gap: float | None) -> str:
    if score_gap is None:
        return "single_candidate"
    if score_gap >= 0.05:
        return "strong"
    if score_gap >= 0.02:
        return "moderate"
    return "narrow"


def _critique_action(critique_packet: dict | None) -> str:
    if not isinstance(critique_packet, dict):
        return "no_critique"
    notes = critique_packet.get("notes") or []
    joined = " ".join(str(x) for x in notes).lower()
    if not joined:
        return "keep"
    if "repetitive" in joined:
        return "keep_but_watch_variation"
    if "generic framing phrase" in joined:
        return "revise_for_directness"
    if "too terse" in joined:
        return "expand"
    if "too much surface density" in joined or "reduce drift" in joined:
        return "tighten"
    return "review"




def _prompt_family(prompt: str) -> str:
    plow = (prompt or "").lower()

    grief_markers = ("miss", "dad", "father", "mother", "grief", "loss", "gone", "death")
    longing_markers = ("longing", "yearn", "wish", "want", "hope", "open", "trust", "closeness", "love")
    guarded_markers = (
        "space", "distance", "protective", "guarded", "boundary", "boundaries",
        "back away", "pulling back", "protect itself", "erase the love",
        "do not trust", "don't trust", "cruelty", "turning cold", "cold"
    )
    structural_markers = ("structure", "coherence", "constraint", "constraints", "layers", "clarity", "depth", "form", "shape")
    causal_markers = ("causal", "pressure", "tone", "steering", "force", "underneath", "surface words", "reaction", "field", "what is shaping")
    memory_markers = ("memory", "reminder", "return", "returns", "same weight", "old memory", "before i do", "before i have chosen")

    has_grief = any(k in plow for k in grief_markers)
    has_longing = any(k in plow for k in longing_markers)
    has_guarded = any(k in plow for k in guarded_markers)
    has_structural = any(k in plow for k in structural_markers)
    has_causal = any(k in plow for k in causal_markers)
    has_memory = any(k in plow for k in memory_markers)

    if has_guarded and has_grief:
        return "guarded_grief"
    if has_guarded and has_longing:
        return "guarded_longing"
    if has_memory and has_causal:
        return "memory_causal"
    if has_structural and (has_longing or has_grief or "feeling" in plow):
        return "structure_feeling"
    if has_grief:
        return "grief"
    if has_guarded:
        return "guardedness"
    if has_longing:
        return "longing"
    if has_causal:
        return "causal_pressure"
    if has_memory:
        return "memory_emotional"
    if has_structural:
        return "structural"
    return "general"

def _build_reply_deepening(
    prompt: str,
    selected_text: str,
    winner_domain: str,
    runner_domain: str | None,
    memory_profile: str | None,
    critique_action: str | None,
) -> str:
    family = _prompt_family(prompt)

    if winner_domain == "emotional_depth":
        if family == "guarded_grief":
            return (
                "What you said sounds like love and self-protection are pulling against each other at the same time. "
                "So Leveon did not treat the boundary like the opposite of care. "
                "It tried to stay close to the ache while still leaving room for what in you is trying to stay safe."
            )
        if family == "guarded_longing":
            return (
                "What you said sounds like part of you still wants closeness, but not at the cost of getting hurt again. "
                "So Leveon kept the answer soft enough to honor the reaching, while also respecting the part of you that is holding back."
            )
        if family == "grief":
            return (
                "What you said sounds like something that needs to be met before it can be explained. "
                "So Leveon stayed near the ache instead of stepping away from it too quickly. "
                "It kept closeness at the center because that feels like where the truth of what you said is still living."
            )
        if family == "longing":
            return (
                "What you said sounds like part of you is reaching, but carefully. "
                "So Leveon answered in a way that let that reaching stay gentle instead of forcing it into certainty too fast. "
                "It tried to keep the openness real."
            )
        if family == "guardedness":
            return (
                "What you said sounds more protective than rejecting. "
                "So Leveon gave that distance a softer shape, because sometimes what needs space still deserves care. "
                "It tried to let the boundary stay human instead of turning hard."
            )
        return (
            "What you said sounds like it needed the feeling to stay in the center. "
            "So Leveon did not try to rise above it too quickly. "
            "It left the response close enough to feel human-sized."
        )

    if winner_domain == "memory_emotional":
        if family == "memory_causal":
            return (
                "What you said sounds like memory is already setting the tone before your conscious choice can catch up to it. "
                "So Leveon followed that deeper imprint instead of answering only the surface wording. "
                "That lets the reply stay close to the sense that something older is still steering the moment."
            )
        return (
            "What you said sounds shaped by both feeling and memory at once. "
            "So Leveon followed that emotional imprint instead of only answering the surface meaning. "
            "That lets the reply carry recognition as well as sense."
        )

    if winner_domain == "causal_emotional":
        return (
            "What you said sounds like you are trying to feel what is underneath the reaction, not just describe the reaction itself. "
            "So Leveon followed the deeper pressure under the feeling and treated tone and memory as part of what is shaping the moment."
        )

    if winner_domain == "causal":
        return (
            "What you said sounds like you want the force underneath the experience named more clearly. "
            "So Leveon answered in terms of what is steering the route, not just what appears on the surface."
        )

    if winner_domain == "memory_structure":
        return (
            "What you said sounds like it needs both continuity and shape. "
            "So Leveon tried to keep it from scattering while still turning it into something readable."
        )

    if winner_domain == "structure":
        if family == "structure_feeling":
            return (
                "What you said sounds like you want shape without losing contact with the feeling that is bending the route. "
                "So Leveon answered more cleanly, but kept the pressure visible instead of flattening it into abstraction."
            )
        return (
            "What you said sounds like it needs shape more than atmosphere right now. "
            "So Leveon answered more cleanly and directly before widening into anything extra."
        )

    if winner_domain in {"balancing", "balancing_structure"}:
        return (
            "What you said sounds like it is holding more than one demand at once. "
            "So Leveon tried to keep clarity and depth together without letting the answer flatten or drift."
        )

    return (
        "What you said has a living line inside it, and Leveon tried to stay with that line as it turned into language."
    )

def _build_winner_rationale(out: dict) -> dict:
    artifacts = out.get("artifacts", {}) or {}
    route_compare = artifacts.get("route_compare", {}) or {}
    ranked = route_compare.get("ranked_routes", []) or []
    winner = route_compare.get("best_route") or {}
    runner_up = None
    if len(ranked) > 1:
        winner_domain = str(winner.get("domain", "") or "")
        for cand in ranked[1:]:
            cand_domain = str(cand.get("domain", "") or "")
            if cand_domain != winner_domain:
                runner_up = cand
                break
        if runner_up is None:
            runner_up = ranked[1]

    winner_score = winner.get("_artifact_score")
    runner_score = runner_up.get("_artifact_score") if isinstance(runner_up, dict) else None
    score_gap = round(float(winner_score) - float(runner_score), 4) if winner_score is not None and runner_score is not None else None

    winner_breakdown = winner.get("_artifact_score_breakdown", {}) or {}
    runner_breakdown = runner_up.get("_artifact_score_breakdown", {}) if isinstance(runner_up, dict) else {}
    memory_pressure = artifacts.get("memory_pressure", {}) or {}
    critique = artifacts.get("self_critique", {}) or {}
    critique_packet = critique.get("critique_packet", {}) or {}
    route_meta = out.get("route_meta", {}) or {}

    winner_domain = str(winner.get("domain", "") or "")
    runner_domain = str(runner_up.get("domain", "") or "") if isinstance(runner_up, dict) else ""
    memory_profile = str(memory_pressure.get("recommended_profile", "") or "")

    reasons = []
    if winner_domain:
        reasons.append(f"{winner_domain} matched the prompt best")
    if winner_breakdown.get("pressure_fidelity") is not None:
        reasons.append(f"pressure_fidelity={winner_breakdown.get('pressure_fidelity')}")
    if score_gap is not None:
        reasons.append(f"score_gap={score_gap}")
    if route_meta.get("shadow_match"):
        reasons.append("live/shape shadow agreement")
    if route_meta.get("domain_match"):
        reasons.append("domain-render agreement")
    if memory_profile:
        reasons.append(f"memory_profile={memory_profile}")

    action = _critique_action(critique_packet)

    summary = f"{winner_domain or 'winner'} won"
    if runner_domain:
        summary += f" over {runner_domain}"
    if score_gap is not None:
        summary += f" by {score_gap}"
    if memory_profile:
        summary += f" with {memory_profile} memory pressure recommended"
    summary += "."

    reply_deepening = _build_reply_deepening(
        prompt=out.get("prompt", ""),
        selected_text=str(winner.get("final_english", "") or ""),
        winner_domain=winner_domain,
        runner_domain=runner_domain or None,
        memory_profile=memory_profile or None,
        critique_action=action,
    )

    return {
        "winner_id": winner.get("id"),
        "winner_domain": winner_domain,
        "winner_score": winner_score,
        "winner_pressure_fidelity": winner_breakdown.get("pressure_fidelity"),
        "runner_up_id": runner_up.get("id") if isinstance(runner_up, dict) else None,
        "runner_up_domain": runner_domain or None,
        "runner_up_score": runner_score,
        "runner_up_pressure_fidelity": runner_breakdown.get("pressure_fidelity") if isinstance(runner_breakdown, dict) else None,
        "score_gap": score_gap,
        "decision_strength": _decision_strength(score_gap),
        "recommended_memory_profile": memory_profile or None,
        "critique_action": action,
        "shadow_agreement": bool(route_meta.get("shadow_match")),
        "domain_agreement": bool(route_meta.get("domain_match")),
        "reasons": reasons,
        "summary": summary,
        "reply_deepening": reply_deepening,
        "leveon_explanation": reply_deepening,
        "why_this_won": reply_deepening,
    }

def _build_selection_output(out: dict) -> dict:
    artifacts = out.get("artifacts", {}) or {}
    route_compare = artifacts.get("route_compare", {}) or {}
    memory_pressure = artifacts.get("memory_pressure", {}) or {}
    self_critique = artifacts.get("self_critique", {}) or {}
    winner_rationale = out.get("winner_rationale", {}) or {}

    winner = route_compare.get("best_route") or {}
    winner_text = str(winner.get("final_english", "") or "")
    winner_domain = str(winner.get("domain", "") or "")
    winner_id = winner.get("id")
    winner_score = winner.get("_artifact_score")

    revised_text = str(self_critique.get("revised_output", "") or "")
    critique_action = str(winner_rationale.get("critique_action", "") or "keep")
    memory_profile = str(memory_pressure.get("recommended_profile", "") or "")

    use_revised = (
        critique_action in {"revise_for_directness", "tighten", "expand", "review"}
        and revised_text
        and revised_text != winner_text
    )

    selected_text = revised_text if use_revised else winner_text

    return {
        "selected_route_id": winner_id,
        "selected_domain": winner_domain or None,
        "selected_text": selected_text or None,
        "selected_memory_profile": memory_profile or None,
        "selected_revision_policy": critique_action or None,
        "selected_score": winner_score,
        "decision_strength": winner_rationale.get("decision_strength"),
        "score_gap": winner_rationale.get("score_gap"),
        "shadow_agreement": bool(winner_rationale.get("shadow_agreement")),
        "domain_agreement": bool(winner_rationale.get("domain_agreement")),
        "used_revised_text": bool(use_revised),
    }

def _build_competitive_route_candidates_from_live(
    prompt: str,
    live_out: Dict[str, Any],
    live_lp: Dict[str, Any],
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    live_domain = str(live_lp.get("domain", "") or "").strip()
    live_text = str(
        live_out.get("final_english")
        or live_lp.get("rendered_english")
        or ""
    ).strip()

    if live_text:
        base = _domain_score(live_domain)
        candidates.append({
            "id": f"live_{live_domain or 'general'}",
            "source": "live_governed",
            "domain": live_domain or "general",
            "score": round(base, 4),
            "confidence": round(max(0.55, min(0.92, base - 0.03)), 4),
            "coherence": round(max(0.60, min(0.95, base + 0.03)), 4),
            "cost": 0.12,
            "novelty": 0.28 if live_domain == "emotional_depth" else 0.22,
            "final_english": live_text,
        })

    if should_use_shape_kernel(prompt, live_domain):
        shape_text = str(render_via_shape_kernel(prompt) or "").strip()
        if shape_text:
            candidates.append({
                "id": "shape_shadow",
                "source": "shape_shadow",
                "domain": "emotional_depth",
                "score": 0.78,
                "confidence": 0.75,
                "coherence": 0.79,
                "cost": 0.14,
                "novelty": 0.31,
                "final_english": shape_text,
            })

    domains = _candidate_domains_from_prompt(prompt, live_domain)
    for domain in domains:
        if not domain:
            continue
        domain_text = _render_domain_candidate(prompt, domain)
        if not domain_text:
            continue
        candidates.append({
            "id": f"domain_{domain}",
            "source": f"domain_render:{domain}",
            "domain": domain,
            "score": round(_domain_score(domain) - 0.03, 4),
            "confidence": 0.74,
            "coherence": 0.82,
            "cost": 0.13,
            "novelty": 0.20 if domain != "emotional_depth" else 0.27,
            "final_english": domain_text,
        })

    for c in candidates:
        domain = str(c.get("domain", "") or "")
        try:
            base_score = float(c.get("score", 0.0) or 0.0)
        except Exception:
            base_score = 0.0
        bonus = _prompt_domain_bonus(prompt, domain)

        t = (prompt or "").lower()
        steering_override = 0.0
        if "before i even choose" in t or ("steering" in t and "choose" in t):
            if domain == "causal":
                steering_override += 0.18
            elif domain == "causal_emotional":
                steering_override -= 0.14
            elif domain == "structure":
                steering_override -= 0.10

        total_bonus = bonus + steering_override
        if total_bonus:
            c["score"] = round(base_score + total_bonus, 4)
            c["_prompt_domain_bonus"] = total_bonus

    deduped, meta = _dedupe_candidates(candidates)
    meta["candidate_sources_before_dedupe"] = [c.get("source") for c in candidates]
    meta["candidate_domains_before_dedupe"] = [c.get("domain") for c in candidates]
    return deduped, meta

def _dedupe_candidates(candidates: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = {}
    shadow_match = False
    shadow_match_sources: List[str] = []
    domain_match = False
    domain_match_sources: List[str] = []

    for c in candidates:
        text_key = str(c.get("final_english", "")).strip().lower()
        source = str(c.get("source", "")).strip()

        if not text_key:
            continue

        if text_key in seen:
            prev_source = seen[text_key]
            pair = sorted([prev_source, source])
            label = "+".join(pair)

            if {prev_source, source} == {"live_governed", "shape_shadow"}:
                shadow_match = True
                if label not in shadow_match_sources:
                    shadow_match_sources.append(label)

            if "domain_render" in prev_source or "domain_render" in source:
                domain_match = True
                if label not in domain_match_sources:
                    domain_match_sources.append(label)

            continue

        seen[text_key] = source
        out.append(c)

    meta = {
        "shadow_match": shadow_match,
        "shadow_match_sources": shadow_match_sources,
        "domain_match": domain_match,
        "domain_match_sources": domain_match_sources,
        "candidate_count_before_dedupe": len(candidates),
        "candidate_count_after_dedupe": len(out),
    }
    return out, meta

def _build_live_route_candidates_from_live(
    prompt: str,
    live_out: Dict[str, Any],
    live_lp: Dict[str, Any],
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    live_domain = str(live_lp.get("domain", "") or "").strip()
    live_text = str(
        live_out.get("final_english")
        or live_lp.get("rendered_english")
        or ""
    ).strip()

    if live_text:
        base = _domain_score(live_domain)
        candidates.append({
            "id": f"live_{live_domain or 'general'}",
            "source": "live_governed",
            "domain": live_domain or "general",
            "score": round(base, 4),
            "confidence": round(max(0.55, min(0.92, base - 0.03)), 4),
            "coherence": round(max(0.60, min(0.95, base + 0.03)), 4),
            "cost": 0.12,
            "novelty": 0.28 if live_domain == "emotional_depth" else 0.22,
            "final_english": live_text,
        })

    if should_use_shape_kernel(prompt, live_domain):
        shape_text = str(render_via_shape_kernel(prompt) or "").strip()
        if shape_text:
            candidates.append({
                "id": "shape_shadow",
                "source": "shape_shadow",
                "domain": "emotional_depth",
                "score": 0.78,
                "confidence": 0.75,
                "coherence": 0.79,
                "cost": 0.14,
                "novelty": 0.31,
                "final_english": shape_text,
            })

    conceptual_domain = promoted_conceptual_domain(prompt, "basic_query")
    if conceptual_domain != "basic_query":
        route = SimpleNamespace(domain=conceptual_domain)
        conceptual_text = str(
            render_from_route(prompt, route, shape="", anchors=[], domain_frequency=0) or ""
        ).strip()
        if conceptual_text:
            candidates.append({
                "id": f"conceptual_{conceptual_domain}",
                "source": "conceptual_shadow",
                "domain": conceptual_domain,
                "score": 0.76,
                "confidence": 0.74,
                "coherence": 0.82,
                "cost": 0.13,
                "novelty": 0.20,
                "final_english": conceptual_text,
            })

    return _dedupe_candidates(candidates)

def run_profile(profile: str, prompt: str, payload: dict) -> dict:
    profile = (profile or "full").strip().lower()

    live_out, live_lp = _run_live_prompt(prompt)
    live_domain = str(live_lp.get("domain", "") or "")
    live_final = str(live_out.get("final_english", "") or "")

    route_candidates, route_meta = payload.get("route_candidates"), None
    if not route_candidates:
        route_candidates, route_meta = _build_competitive_route_candidates_from_live(prompt, live_out, live_lp)

    hotspot_trace = payload.get("hotspot_trace") or _default_hotspot_trace(prompt, live_domain=live_domain)
    draft_output = payload.get("draft_output") or live_final or _default_draft_output(prompt)

    out = {
        "profile": profile,
        "prompt": prompt,
        "live": {
            "domain": live_domain,
            "rendered_english": str(live_lp.get("rendered_english", "") or ""),
            "final_english": live_final,
        },
        "artifacts": {},
    }

    if route_meta is not None:
        out["route_meta"] = route_meta

    if profile in {"route_only", "full"}:
        out["artifacts"]["route_compare"] = compare_routes(prompt, route_candidates)

    if profile in {"memory_only", "full"}:
        out["artifacts"]["memory_pressure"] = simulate_memory_pressure(prompt)

    if profile in {"hotspot_only", "full"}:
        out["artifacts"]["hotspot_map"] = map_hotspot_transitions(hotspot_trace)

    if profile in {"critique_only", "full"}:
        draft_output = (
            payload.get("draft_output")
            or _winner_final_english(out)
            or live_final
            or _default_draft_output(prompt)
        )
        out["artifacts"]["self_critique"] = run_self_critique(draft_output)

    if "route_compare" in out.get("artifacts", {}):
        out["winner_rationale"] = _build_winner_rationale(out)
        out["selection_output"] = _build_selection_output(out)

    return out


def main() -> int:
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "usage: python -m runtime.run_analysis_profile <full|route_only|memory_only|hotspot_only|critique_only> <input.json>"
        }, ensure_ascii=False))
        return 2

    profile = str(sys.argv[1]).strip()
    input_path = Path(sys.argv[2])

    if not input_path.exists():
        print(json.dumps({"error": f"input file not found: {input_path}"}, ensure_ascii=False))
        return 2

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    prompt = str(payload.get("prompt", "") or "")

    result = run_profile(profile, prompt, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

