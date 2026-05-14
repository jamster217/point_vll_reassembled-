#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, time
from typing import Any, Dict, List

OUT = Path("var/optimizer/build_rewriter_state.json")

VALIDATION_GATE = {
    "allow_core_rewrite": False,
    "require_rollback": True,
    "require_import_check": True,
    "require_symbol_preservation": True,
    "require_memory_path_preservation": True,
}

ROUTES = {
    "stabilize_runtime": [
        ("extract_runtime_segments", "split scheduler, loop control, execution state, and runtime helpers"),
        ("reduce_runtime_coupling", "replace hidden shared state with explicit packet passing"),
    ],
    "separate_parse_and_emit": [
        ("split_parse_stage", "separate intake, parse, transform, emit, and validate"),
        ("normalize_emit_contract", "make output packet shape explicit and stable"),
    ],
    "consolidate_memory_paths": [
        ("merge_memory_writes", "unify repeated writes to memory/log/provenance structures"),
        ("preserve_provenance_chain", "retain source, timestamp, and residue trace through rewrite"),
    ],
    "clarify_symbol_pipeline": [
        ("separate_symbol_stages", "split detection, scoring, translation, ambiguity, and summary"),
        ("enforce_symbol_packet", "ensure symbolic packet has stable fields and residue awareness"),
    ],
    "decouple_voice_io": [
        ("split_voice_capture_cleanup_response", "separate microphone input, cleanup, symbolic parse, and response synthesis"),
    ],
    "general_refactor": [
        ("reduce_duplicate_logic", "extract repeated branches into helper or packetized stage"),
    ],
}

PATCH_KIND = {
    "extract_runtime_segments": ("structure_patch", "create explicit runtime packet and isolate scheduler loop"),
    "reduce_runtime_coupling": ("coupling_patch", "replace implicit globals/shared mutation with explicit inputs/returns"),
    "split_parse_stage": ("pipeline_patch", "split intake -> parse -> transform -> emit -> validate"),
    "normalize_emit_contract": ("contract_patch", "stabilize output fields across all branches"),
    "merge_memory_writes": ("memory_patch", "route all writes through one memory append/persist function"),
    "preserve_provenance_chain": ("provenance_patch", "attach source, timestamp, seed labels, and residue trace to all persisted entries"),
    "separate_symbol_stages": ("symbol_pipeline_patch", "split symbol detection, weighting, ambiguity handling, and summary generation"),
    "enforce_symbol_packet": ("symbol_contract_patch", "enforce one stable symbolic packet return shape"),
    "split_voice_capture_cleanup_response": ("voice_pipeline_patch", "split capture, cleanup, symbolic parse, response compile, playback"),
    "reduce_duplicate_logic": ("dedupe_patch", "extract repeated logic into helper units without altering output contract"),
}

def _load_optimizer():
    path = Path("var/optimizer/build_optimizer_state.json")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"optimization_plan": {"actions": []}}

def _is_core_target(target: str) -> bool:
    t = str(target or "").lower()
    return any(x in t for x in ("core_kernel", "core_runtime", "core_memory"))

def rewrite(build_state=None, optimization_packet=None, seed_bank=None, route_trace=None):
    build_state = build_state or {}
    optimization_packet = optimization_packet or _load_optimizer()
    route_trace = route_trace or []

    queue = optimization_packet.get("optimization_plan", {}).get("actions", [])
    rewrite_actions: List[Dict[str, Any]] = []

    for item in queue:
        action_type = item.get("type") or item.get("TYPE")
        target = item.get("target") or item.get("TARGET")
        seed_guidance = item.get("seed_guidance", {}) or {}

        for routed_type, notes in ROUTES.get(action_type, ROUTES["general_refactor"]):
            rewrite_actions.append({
                "type": routed_type,
                "target": target,
                "seed_primary": seed_guidance.get("primary"),
                "seed_secondary": seed_guidance.get("secondary"),
                "notes": notes,
                "source_action_type": action_type,
            })

    patch_blocks = []
    for action in rewrite_actions:
        kind, instruction = PATCH_KIND.get(action["type"], ("general_patch", action["notes"]))
        block = {
            "target": action["target"],
            "patch_kind": kind,
            "instruction": instruction,
            "source_action": action,
            "auto_apply": not _is_core_target(action["target"]),
            "requires_manual_review": _is_core_target(action["target"]),
            "seed_rationale": {
                "primary": "preserve structure while reducing instability",
                "secondary": "retain symbolic continuity and explicit provenance",
            },
        }

        if action["type"] == "extract_runtime_segments":
            block["template"] = {
                "before": "mixed runtime + state logic",
                "after": [
                    "RuntimeInputPacket",
                    "RuntimeStatePacket",
                    "RuntimeScheduler",
                    "RuntimeStepExecutor",
                ],
            }

        if action["type"] == "normalize_emit_contract":
            block["template"] = {
                "required_fields": [
                    "clean_text",
                    "shape_vector",
                    "dominant_symbols",
                    "residual_ambiguity",
                    "parse_confidence",
                    "structural_summary",
                ],
            }

        patch_blocks.append(block)

    rollback_blocks = [
        {
            "target": block["target"],
            "rollback_kind": "restore_previous_module_snapshot",
            "requires": [
                "pre_rewrite_copy",
                "import_graph_snapshot",
                "output_contract_snapshot",
            ],
        }
        for block in patch_blocks
    ]

    manual_review_required = any(b.get("requires_manual_review") for b in patch_blocks)
    ready_for_apply = bool(patch_blocks) and len(rollback_blocks) >= len(patch_blocks) and not manual_review_required

    notes = []
    if manual_review_required:
        notes.append("core files detected; auto-apply disabled for protected targets")
    if len(rollback_blocks) < len(patch_blocks):
        notes.append("rollback coverage incomplete; do not apply patch set yet")

    packet = {
        "source": "runtime.build_rewriter_from_program_seeds",
        "timestamp": time.time(),
        "original_build_state": build_state,
        "optimization_packet": optimization_packet,
        "route_trace": route_trace,
        "rewrite_actions": rewrite_actions,
        "patch_blocks": patch_blocks,
        "rollback_blocks": rollback_blocks,
        "validation_gate": VALIDATION_GATE,
        "validation": {
            "patch_count": len(patch_blocks),
            "rollback_count": len(rollback_blocks),
            "ready_for_apply": ready_for_apply,
            "manual_review_required": manual_review_required,
            "notes": notes,
        },
        "surface_rule": "plan only; do not mutate files automatically",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

if __name__ == "__main__":
    print(json.dumps(rewrite(), indent=2, ensure_ascii=False))

