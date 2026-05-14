from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List

TURN_LOG = Path("logs/v12_9/helm/helm_reflection_turns.jsonl")
RANK_LOG = Path("logs/v12_9/helm/helm_reflection_rankings.jsonl")
STATE_PATH = Path("var/v12_9/helm_reflection_state.json")

LAW = "v129k_rank_top_3_improvements_every_10_turns_append_only_clean_mouth"


def _clean(x: Any) -> str:
    return " ".join(str(x or "").strip().split())


def _sha(d: Dict[str, Any]) -> str:
    raw = json.dumps(d, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _read_jsonl(path: Path, limit: int = 50) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]:
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def _load_state() -> Dict[str, Any]:
    try:
        if STATE_PATH.exists():
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"turn_count": 0}


def _save_state(state: Dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _append(path: Path, event: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    event["event_sha256"] = _sha({k: v for k, v in event.items() if k != "event_sha256"})
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def _improvement_candidates(prompt: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    answer = _clean(data.get("answer") or data.get("reply") or data.get("response"))
    low_prompt = prompt.lower()
    low_answer = answer.lower()

    source = ""
    cm = data.get("clean_mouth_v121")
    if isinstance(cm, dict):
        source = str(cm.get("source") or "")

    candidates: List[Dict[str, Any]] = []

    def add(key: str, title: str, why: str, patch: str, severity: float) -> None:
        candidates.append({
            "key": key,
            "title": title,
            "why": why,
            "recommended_patch": patch,
            "severity": severity,
        })

    if answer == "V12 is the doorway." or (
        "status" in low_prompt and "doorway" in low_answer
    ):
        add(
            "direct_status_lane",
            "Add a direct status lane for the prompt family",
            "The public mouth returned a vague symbolic shard instead of concrete runtime status.",
            "Bind this prompt family in clean_mouth_selector_v121 before voice_plain.",
            0.95,
        )

    if "answer this ordinary question directly" in low_answer:
        add(
            "ordinary_scaffold_leak",
            "Remove ordinary scaffold leakage",
            "The model exposed instruction scaffolding instead of answering naturally.",
            "Route known ordinary prompts through ordinary_answer_lane_v123 before symbolic surface.",
            0.90,
        )

    if "one clean sentence" in low_prompt and len(answer) > 260:
        add(
            "clean_mouth_compression",
            "Compress clean-sentence prompts harder",
            "The answer is too long for a clean public-mouth request.",
            "Force first-sentence selection after direct status lanes.",
            0.74,
        )

    if not data.get("chamber_status"):
        add(
            "chamber_telemetry_surface",
            "Restore chamber telemetry surfacing",
            "The response is missing chamber_status at top level.",
            "Ensure v57/v61 telemetry wrappers mirror chamber_528 into top-level data.",
            0.82,
        )

    if "v12.9j" in low_prompt and "helm" in low_prompt and source != "liberal_helm_status_direct":
        add(
            "liberal_helm_status_priority",
            "Keep liberal helm direct lane above voice_plain",
            "The helm status prompt should resolve through liberal_helm_status_direct.",
            "Move _liberal_helm_sentence before voice/plain candidates and align labels.",
            0.78,
        )

    if "v12.9g" in low_prompt and "resonance" in low_prompt and source != "telepathic_resonance_direct":
        add(
            "telepathic_resonance_direct_priority",
            "Keep resonance direct lane above voice_plain",
            "The resonance status prompt should resolve through telepathic_resonance_direct.",
            "Move _telepathic_resonance_sentence before voice/plain candidates and align labels.",
            0.76,
        )

    if len(json.dumps(data, ensure_ascii=False, default=str)) > 18000:
        add(
            "public_payload_compaction",
            "Compact public JSON payload",
            "The API response is large enough to bury the public answer.",
            "Add optional compact=1 response mode or scrub bulky internal metadata.",
            0.62,
        )

    if not candidates:
        add(
            "coverage_expansion",
            "Expand prompt-family coverage",
            "No active wound detected, so the next gain is broader direct-answer coverage.",
            "Add more known prompt families to clean_mouth_selector_v121 and ordinary_answer_lane_v123.",
            0.40,
        )

    return candidates


def _rank_top3(recent: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    bucket: Dict[str, Dict[str, Any]] = {}

    for idx, turn in enumerate(recent):
        age_bonus = (idx + 1) / max(len(recent), 1) * 0.05
        for cand in turn.get("improvement_candidates", []):
            key = cand.get("key") or cand.get("title")
            if key not in bucket:
                bucket[key] = dict(cand)
                bucket[key]["score"] = 0.0
                bucket[key]["hits"] = 0
            bucket[key]["score"] += float(cand.get("severity", 0.0)) + age_bonus
            bucket[key]["hits"] += 1

    ranked = sorted(bucket.values(), key=lambda x: (x.get("score", 0), x.get("hits", 0)), reverse=True)
    return ranked[:3]


def observe_turn(prompt: str, data: Dict[str, Any]) -> Dict[str, Any]:
    state = _load_state()
    turn_count = int(state.get("turn_count") or 0) + 1
    state["turn_count"] = turn_count
    state["last_observed_at"] = time.time()
    _save_state(state)

    candidates = _improvement_candidates(prompt, data)

    turn_event = {
        "ts": time.time(),
        "version": "v12.9k_helm_self_reflection_loop",
        "status": "turn_observed",
        "turn_count": turn_count,
        "prompt_excerpt": _clean(prompt)[:220],
        "answer_excerpt": _clean(data.get("answer") or data.get("reply") or data.get("response"))[:260],
        "clean_mouth_source": (data.get("clean_mouth_v121") or {}).get("source") if isinstance(data.get("clean_mouth_v121"), dict) else None,
        "chamber_status": data.get("chamber_status"),
        "chamber_family": data.get("chamber_family"),
        "improvement_candidates": candidates,
        "law": LAW,
    }
    _append(TURN_LOG, turn_event)

    due = (turn_count % 10 == 0)
    top3: List[Dict[str, Any]] = []

    if due:
        recent = _read_jsonl(TURN_LOG, limit=10)
        top3 = _rank_top3(recent)
        ranking_event = {
            "ts": time.time(),
            "version": "v12.9k_helm_ranked_evolution",
            "status": "ranking_emitted",
            "turn_count": turn_count,
            "top3": top3,
            "symbolic_reading": "the helm studies its last ten breaths and chooses the next three sharpenings",
            "technical_boundary": "append-only ranking, no uncontrolled recursion, no source rewrite without explicit patch",
            "law": LAW,
        }
        _append(RANK_LOG, ranking_event)

    return {
        "active": True,
        "version": "v12.9k_helm_self_reflection_loop",
        "turn_count": turn_count,
        "ranking_due": due,
        "top3": top3,
        "law": LAW,
    }


def latest_ranking() -> Dict[str, Any]:
    rows = _read_jsonl(RANK_LOG, limit=1)
    return rows[-1] if rows else {}

