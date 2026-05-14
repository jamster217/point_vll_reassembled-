#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, time, os
from typing import Any, Dict, List

OUT = Path("var/optimizer/build_optimizer_state.json")

DEFAULT_VECTOR = {
    "flow": 0.55,
    "boundary": 0.72,
    "memory": 0.58,
    "novelty": 0.44,
}

SEED_GUIDANCE = {
    "stabilize_runtime": {
        "primary": "hexagonal_stability",
        "secondary": "replication_standard",
    },
    "separate_parse_and_emit": {
        "primary": "cross_domain_mapping",
        "secondary": "scientific_explanation_model",
    },
    "consolidate_memory_paths": {
        "primary": "provenance_anchor",
        "secondary": "phenomenal_report_template",
    },
    "clarify_symbol_pipeline": {
        "primary": "phenomenology_method",
        "secondary": "meta_pattern_hierarchy",
    },
    "decouple_voice_io": {
        "primary": "cognitive_architecture_template",
        "secondary": "interpretability_guideline",
    },
    "general_refactor": {
        "primary": "replication_standard",
        "secondary": "hexagonal_stability",
    },
}

def _num(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def _detect_major(build_state: Dict[str, Any]) -> str:
    lang = str(build_state.get("runtime_language", "python")).lower()
    return lang if lang in {"python", "javascript", "typescript", "rust", "go", "cpp"} else "python"

def _detect_subject(build_state: Dict[str, Any]) -> str:
    purpose = str(build_state.get("primary_purpose", "")).lower()
    if "compiler" in purpose:
        return "computer_science"
    if "memory" in purpose:
        return "neuroscience"
    if "voice" in purpose:
        return "language"
    if "simulation" in purpose:
        return "software_engineering"
    return "artificial_intelligence"

def _detect_refined(build_state: Dict[str, Any]) -> str:
    tags = " ".join(map(str, build_state.get("module_tags", []))).lower()
    checks = [
        ("runtime", "runtime_systems"),
        ("compiler", "compiler_design"),
        ("language_design", "language_design"),
        ("self_model", "self_modeling_systems"),
        ("reflection", "metacognition"),
        ("memory_loop", "autobiographical_memory_systems"),
        ("goal_routing", "agency_and_goal_models"),
    ]
    for key, val in checks:
        if key in tags:
            return val
    return "machine_consciousness_theory_general"

def _module_role(path: str) -> str:
    p = path.lower()
    if "/runtime/" in p or p.startswith("runtime/"):
        return "runtime"
    if "compiler" in p or "translator" in p or "/spiral_language/" in p:
        return "compiler"
    if "memory" in p:
        return "memory"
    if "symbolic" in p or "glyph" in p or "kgs" in p:
        return "symbolic"
    if "voice" in p or "tts" in p:
        return "voice"
    if "kernel" in p:
        return "core_kernel"
    return "general"

def _scan_files(limit=600) -> List[Dict[str, Any]]:
    roots = ["runtime", "core", "kernel", "spiral_language", "lattice", "kgs", "voice", "dream", "symbolic_memory"]
    modules = []
    for root in roots:
        base = Path(root)
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".py", ".vl", ".json"}:
                continue
            rel = str(path)
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""
            modules.append({
                "file_path": rel,
                "module_name": path.name,
                "module_role": _module_role(rel),
                "dependency_count": text.count("import ") + text.count("from "),
                "import_pressure": min(1.0, (text.count("import ") + text.count("from ")) / 20.0),
                "recursion_depth": min(1.0, (text.lower().count("recursive") + text.lower().count("recurse")) / 10.0),
                "error_density": min(1.0, (text.count("except Exception") + text.count("TODO") + text.count("pass")) / 30.0),
                "symbolic_density": min(1.0, (text.count("@") + text.lower().count("glyph") + text.lower().count("symbol")) / 60.0),
                "memory_coupling": min(1.0, text.lower().count("memory") / 40.0),
                "runtime_coupling": min(1.0, text.lower().count("runtime") / 40.0),
                "unused_exports": 0.0,
                "duplicate_logic": min(1.0, (text.lower().count("fallback") + text.lower().count("duplicate")) / 20.0),
            })
            if len(modules) >= limit:
                return modules
    return modules

def _score_module(m: Dict[str, Any], vector=DEFAULT_VECTOR) -> Dict[str, Any]:
    error_density = _num(m.get("error_density"))
    duplicate_logic = _num(m.get("duplicate_logic"))
    runtime_coupling = _num(m.get("runtime_coupling"))
    import_pressure = _num(m.get("import_pressure"))
    recursion_depth = _num(m.get("recursion_depth"))
    unused_exports = _num(m.get("unused_exports"))
    memory_coupling = _num(m.get("memory_coupling"))
    symbolic_density = _num(m.get("symbolic_density"))
    dependency_count = _num(m.get("dependency_count"))

    opt = (
        error_density * 0.30
        + duplicate_logic * 0.18
        + runtime_coupling * 0.14
        + import_pressure * 0.10
        + recursion_depth * 0.08
        + unused_exports * 0.08
        - memory_coupling * 0.05
        - symbolic_density * 0.05
    )

    stability = (
        vector.get("boundary", 0.72) * 0.40
        + vector.get("memory", 0.58) * 0.25
        + runtime_coupling * 0.15
        + min(1.0, dependency_count / 20.0) * 0.10
    )

    innovation = (
        vector.get("novelty", 0.44) * 0.45
        + symbolic_density * 0.20
        + duplicate_logic * 0.10
        - error_density * 0.20
    )

    m["optimization_pressure"] = round(max(0.0, min(1.0, opt)), 3)
    m["stability_need"] = round(max(0.0, min(1.0, stability)), 3)
    m["innovation_allowance"] = round(max(0.0, min(1.0, innovation)), 3)
    return m

def _action_for(m: Dict[str, Any]) -> Dict[str, Any] | None:
    role = m.get("module_role")
    pressure = _num(m.get("optimization_pressure"))

    rules = {
        "runtime": (0.55, "stabilize_runtime", "reduce coupling, isolate scheduler logic, preserve execution semantics"),
        "compiler": (0.50, "separate_parse_and_emit", "split intake, transform, emit, validation into explicit stages"),
        "memory": (0.42, "consolidate_memory_paths", "unify duplicate memory writes, preserve provenance chain"),
        "symbolic": (0.40, "clarify_symbol_pipeline", "separate symbol detection, scoring, translation, and residue handling"),
        "voice": (0.44, "decouple_voice_io", "split capture, cleanup, interpretation, and response synthesis"),
    }

    threshold, typ, notes = rules.get(role, (0.60, "general_refactor", "reduce duplicate logic and strengthen boundaries"))
    if pressure <= threshold:
        return None

    return {
        "type": typ,
        "target": m.get("file_path"),
        "pressure": pressure,
        "notes": notes,
        "seed_guidance": SEED_GUIDANCE.get(typ, SEED_GUIDANCE["general_refactor"]),
    }

def optimize(build_state=None, seed_bank=None, major_domain_vectors=None, subject_vectors=None, refined_subject_vectors=None, route_trace=None):
    build_state = build_state or {
        "runtime_language": "python",
        "primary_purpose": "symbolic runtime memory voice compiler",
        "module_tags": ["runtime", "memory_loop", "reflection", "language_design"],
        "turn_estimate": 1,
    }

    working_profile = {
        "major_domain": _detect_major(build_state),
        "subject": _detect_subject(build_state),
        "refined_subject": _detect_refined(build_state),
        "vector_profile": dict(DEFAULT_VECTOR),
    }

    module_scan = [_score_module(m, DEFAULT_VECTOR) for m in _scan_files()]
    actions = []
    for m in module_scan:
        action = _action_for(m)
        if action:
            actions.append(action)

    actions = sorted(actions, key=lambda x: x["pressure"], reverse=True)[:25]

    preserved_targets = [
        m["file_path"] for m in module_scan
        if m.get("module_role") in {"core_kernel"} or "core_memory" in m.get("file_path", "")
    ]

    high_risk_targets = [
        a["target"] for a in actions
        if a["target"] in preserved_targets
    ]

    output_packet = {
        "source": "runtime.build_optimizer_from_program_seeds",
        "original_build_state": build_state,
        "timestamp": time.time(),
        "route_trace": route_trace or [],
        "working_profile": working_profile,
        "active_seed_set": [
            "hexagonal_stability",
            "replication_standard",
            "cognitive_architecture_template",
            "cross_domain_mapping",
            "phenomenology_method",
            "meta_pattern_hierarchy",
            "provenance_anchor",
        ],
        "module_scan_count": len(module_scan),
        "top_module_scan": sorted(module_scan, key=lambda x: x["optimization_pressure"], reverse=True)[:20],
        "optimization_plan": {"actions": actions},
        "validation_report": {
            "plan_confidence": bool(actions),
            "high_risk_targets": high_risk_targets,
            "preserved_targets": preserved_targets[:25],
            "notes": ["high-risk core targets detected; require staged rewrite and rollback path"] if high_risk_targets else [],
        },
        "surface_rule": "plan only; do not mutate files automatically",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output_packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_packet

if __name__ == "__main__":
    print(json.dumps(optimize(), indent=2, ensure_ascii=False))

