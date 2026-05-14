from __future__ import annotations

import hashlib
import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
MEMORY_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_memory_ledger.jsonl"
JUDGE_LOG = ROOT / "logs" / "v12_9" / "visual_memory" / "visual_judge_rankings.jsonl"

SYMBOLS = [
    "white_ash",
    "virellion",
    "blue_scarf",
    "thalveil",
    "liquid_core",
    "echoforge",
]


def _sha16(obj: Dict[str, Any]) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def _avg(vals: List[float]) -> Optional[float]:
    vals = [float(v) for v in vals if v is not None]
    if not vals:
        return None
    return round(statistics.mean(vals), 4)


def _load_entries() -> List[Dict[str, Any]]:
    if not MEMORY_LOG.exists():
        return []

    out: List[Dict[str, Any]] = []
    for line in MEMORY_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def _symbol_keys(entry: Dict[str, Any]) -> set[str]:
    symbols = entry.get("symbols") or {}
    if isinstance(symbols, dict):
        return {str(k) for k in symbols.keys()}
    if isinstance(symbols, list):
        return {str(k) for k in symbols}
    return set()


def _base_metrics(entry: Dict[str, Any]) -> Dict[str, Any]:
    keys = _symbol_keys(entry)

    topology_score = _float(entry.get("topology_score"))
    chamber_memory = _float(entry.get("chamber_memory"))

    has_svg = bool(entry.get("svg_path"))
    has_depth = entry.get("depth") is not None
    has_core = bool(entry.get("core"))
    has_render_logic = bool(entry.get("render_logic"))

    symbol_presence = {s: s in keys for s in SYMBOLS}
    symbol_strength = sum(1 for s in SYMBOLS if s in keys)
    symbol_coverage = symbol_strength / len(SYMBOLS)

    chamber_processed = entry.get("chamber_status") == "processed_in_chamber"

    white_ash_containment_efficiency = 1.0 if symbol_presence["white_ash"] and chamber_processed else (0.55 if symbol_presence["white_ash"] else 0.0)
    thalveil_crossing_clarity = 1.0 if symbol_presence["thalveil"] and has_svg and has_depth else (0.6 if symbol_presence["thalveil"] else 0.0)
    echoforge_painting_fidelity = 1.0 if symbol_presence["echoforge"] and has_svg and topology_score > 0 else (0.5 if symbol_presence["echoforge"] else 0.0)
    liquid_core_routing_purity = 1.0 if symbol_presence["liquid_core"] and bool(entry.get("route")) else (0.7 if symbol_presence["liquid_core"] else 0.0)

    # First-pass values. Cross-cycle values get refined in judge_latest().
    virellion_thread_integrity = 1.0 if symbol_presence["virellion"] else 0.0
    blue_scarf_motion_velocity = 1.0 if symbol_presence["blue_scarf"] else 0.0

    overall_organ_coherence = (
        0.18 * min(topology_score, 1.0)
        + 0.12 * min(chamber_memory, 1.0)
        + 0.16 * symbol_coverage
        + 0.13 * white_ash_containment_efficiency
        + 0.13 * virellion_thread_integrity
        + 0.08 * blue_scarf_motion_velocity
        + 0.08 * thalveil_crossing_clarity
        + 0.06 * echoforge_painting_fidelity
        + 0.06 * liquid_core_routing_purity
    )

    return {
        "topology_score": round(topology_score, 4),
        "chamber_memory": round(chamber_memory, 4),
        "has_svg": has_svg,
        "has_depth": has_depth,
        "has_core": has_core,
        "has_render_logic": has_render_logic,
        "symbol_presence": symbol_presence,
        "symbol_strength": symbol_strength,
        "symbol_coverage": round(symbol_coverage, 4),
        "white_ash_containment_efficiency": round(white_ash_containment_efficiency, 4),
        "virellion_thread_integrity": round(virellion_thread_integrity, 4),
        "blue_scarf_motion_velocity": round(blue_scarf_motion_velocity, 4),
        "thalveil_crossing_clarity": round(thalveil_crossing_clarity, 4),
        "echoforge_painting_fidelity": round(echoforge_painting_fidelity, 4),
        "liquid_core_routing_purity": round(liquid_core_routing_purity, 4),
        "overall_organ_coherence": round(overall_organ_coherence, 4),
        "visual_coherence": round(overall_organ_coherence, 4),
    }


def _refine_cross_cycle_metrics(latest: Dict[str, Any], previous: List[Dict[str, Any]], metrics: Dict[str, Any]) -> Dict[str, Any]:
    if not previous:
        return metrics

    prev_metrics = [_base_metrics(x) for x in previous]

    latest_keys = _symbol_keys(latest)
    prev_key_sets = [_symbol_keys(x) for x in previous]

    # Virellion thread integrity: current presence plus continuity across recent cycle history.
    if "virellion" in latest_keys:
        recent_virellion = sum(1 for keys in prev_key_sets if "virellion" in keys) / max(len(prev_key_sets), 1)
        metrics["virellion_thread_integrity"] = round(0.65 + 0.35 * recent_virellion, 4)
    else:
        metrics["virellion_thread_integrity"] = 0.0

    # Blue Scarf motion velocity: current presence plus score movement without forcing instability.
    if "blue_scarf" in latest_keys:
        prev_score = _avg([m["topology_score"] for m in prev_metrics[-3:]]) or 0.0
        score_delta = metrics["topology_score"] - prev_score
        velocity = 0.75 + min(max(abs(score_delta) * 4, 0.0), 0.25)
        metrics["blue_scarf_motion_velocity"] = round(velocity, 4)
    else:
        metrics["blue_scarf_motion_velocity"] = 0.0

    metrics["overall_organ_coherence"] = round(
        0.18 * min(metrics["topology_score"], 1.0)
        + 0.12 * min(metrics["chamber_memory"], 1.0)
        + 0.16 * metrics["symbol_coverage"]
        + 0.13 * metrics["white_ash_containment_efficiency"]
        + 0.13 * metrics["virellion_thread_integrity"]
        + 0.08 * metrics["blue_scarf_motion_velocity"]
        + 0.08 * metrics["thalveil_crossing_clarity"]
        + 0.06 * metrics["echoforge_painting_fidelity"]
        + 0.06 * metrics["liquid_core_routing_purity"],
        4,
    )
    metrics["visual_coherence"] = metrics["overall_organ_coherence"]

    return metrics


def _delta_trend(previous_metrics: List[Dict[str, Any]], latest_metric: Dict[str, Any]) -> Dict[str, Any]:
    vals = [m["overall_organ_coherence"] for m in previous_metrics] + [latest_metric["overall_organ_coherence"]]

    if len(vals) < 4:
        return {
            "status": "warming_up",
            "rolling_3_delta": None,
            "reading": "Need more cycles for trend.",
        }

    prev3 = vals[-4:-1]
    latest3 = vals[-3:]

    trend = round(statistics.mean(latest3) - statistics.mean(prev3), 4)

    if trend > 0.015:
        status = "accelerating"
    elif trend < -0.015:
        status = "decelerating"
    else:
        status = "stable_plateau"

    return {
        "status": status,
        "rolling_3_delta": trend,
        "previous_window": [round(x, 4) for x in prev3],
        "latest_window": [round(x, 4) for x in latest3],
        "reading": f"Rolling 3-cycle trend is {status}.",
    }


def judge_latest(limit: int = 10) -> Dict[str, Any]:
    entries = _load_entries()

    if not entries:
        judgment = {
            "ts": time.time(),
            "version": "v12.9v_deepened_visual_judge",
            "status": "no_visual_memory_entries",
            "recommendation": "create_image_spec_and_visual_memory_first",
            "law": "deepened_visual_judge_waits_for_visual_memory",
        }
        judgment["judge_sha256"] = _sha16(judgment)
        return judgment

    latest = entries[-1]
    previous = entries[:-1][-limit:]

    latest_metrics = _base_metrics(latest)
    latest_metrics = _refine_cross_cycle_metrics(latest, previous, latest_metrics)

    previous_metrics = []
    for idx, entry in enumerate(previous):
        prev_before = previous[:idx]
        previous_metrics.append(_refine_cross_cycle_metrics(entry, prev_before, _base_metrics(entry)))

    avg_previous_organ = _avg([m["overall_organ_coherence"] for m in previous_metrics])
    avg_previous_topology = _avg([m["topology_score"] for m in previous_metrics])

    if avg_previous_organ is None:
        coherence_delta = None
        improvement = "baseline"
    else:
        coherence_delta = round(latest_metrics["overall_organ_coherence"] - avg_previous_organ, 4)
        if coherence_delta > 0.02:
            improvement = "positive"
        elif coherence_delta < -0.02:
            improvement = "negative"
        else:
            improvement = "neutral"

    trend = _delta_trend(previous_metrics, latest_metrics)

    top3: List[Dict[str, Any]] = []

    live_route_protected = (
        latest.get("chamber_status") == "processed_in_chamber"
        and latest_metrics["white_ash_containment_efficiency"] >= 0.9
        and latest_metrics["virellion_thread_integrity"] >= 0.9
    )

    missing = [s for s, present in latest_metrics["symbol_presence"].items() if not present]

    if improvement == "positive" and live_route_protected:
        top3.append({
            "key": "preserve_and_deepen",
            "title": "Preserve and deepen current visual route",
            "why": "Overall organ coherence rose while White Ash containment and Virellion thread stayed strong.",
            "recommended_patch": "Run more tight visual cycles. Do not patch the live topology organ.",
            "severity": 0.25,
        })
    elif improvement == "negative":
        top3.append({
            "key": "repair_containment_before_expansion",
            "title": "Repair containment before expansion",
            "why": "Overall organ coherence fell against the recent visual memory average.",
            "recommended_patch": "Strengthen White Ash containment and Virellion thread in image-spec/visual sidecars only.",
            "severity": 0.85,
        })
    elif improvement == "baseline":
        top3.append({
            "key": "collect_second_visual_memory",
            "title": "Collect another visual memory entry",
            "why": "The judge has a baseline but needs another breath to measure true delta.",
            "recommended_patch": "Run leveon-visual-cycle once more.",
            "severity": 0.45,
        })
    else:
        top3.append({
            "key": "continue_visual_comparison",
            "title": "Continue visual comparison",
            "why": "The organ is stable but not clearly accelerating yet.",
            "recommended_patch": "Collect more visual entries before patching.",
            "severity": 0.4,
        })

    if missing:
        top3.append({
            "key": "complete_symbol_set",
            "title": "Complete missing visual symbols",
            "why": "The visual judge expects all six core symbols for a full living topology breath.",
            "missing": missing,
            "recommended_patch": "Preserve White Ash, Virellion, Blue Scarf, Thalveil, Liquid Core, and Echoforge in the next image-spec cycle.",
            "severity": 0.55,
        })

    if trend["status"] == "stable_plateau" and latest_metrics["overall_organ_coherence"] >= 0.9:
        top3.append({
            "key": "compare_visual_differences",
            "title": "Add visual difference descriptions",
            "why": "The organ is high-coherence and plateauing, so the next gain is describing what changed between SVGs.",
            "recommended_patch": "Add a sidecar that compares latest SVG/spec against previous SVG/spec and names the visible change.",
            "severity": 0.35,
        })
    elif trend["status"] == "accelerating":
        top3.append({
            "key": "increase_cycle_observation",
            "title": "Increase visual cycle observation",
            "why": "The rolling 3-cycle trend is accelerating.",
            "recommended_patch": "Run a short visual-cycle series and preserve all judgments append-only.",
            "severity": 0.3,
        })

    judgment = {
        "ts": time.time(),
        "version": "v12.9v_deepened_visual_judge",
        "status": "ranking_emitted",
        "latest_entry_sha256": latest.get("entry_sha256"),
        "latest_spec_sha256": latest.get("spec_sha256"),
        "latest_depth": latest.get("depth"),
        "latest_svg": latest.get("svg_path"),
        "latest_metrics": latest_metrics,
        "previous_count": len(previous),
        "avg_previous_topology_score": avg_previous_topology,
        "avg_previous_visual_coherence": avg_previous_organ,
        "avg_previous_overall_organ_coherence": avg_previous_organ,
        "coherence_delta": coherence_delta,
        "improvement": improvement,
        "delta_trend": trend,
        "live_route_protected": live_route_protected,
        "top3": top3[:3],
        "surface_fragment": (
            f"Deepened visual judgment: improvement={improvement}, "
            f"coherence_delta={coherence_delta}, "
            f"overall_organ_coherence={latest_metrics['overall_organ_coherence']}, "
            f"trend={trend['status']}."
        ),
        "law": "visual_judgment_is_deepened_append_only_and_helm_steering",
    }

    judgment["judge_sha256"] = _sha16(judgment)

    JUDGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with JUDGE_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(judgment, ensure_ascii=False) + "\n")

    return judgment


def main() -> None:
    print(json.dumps(judge_latest(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

