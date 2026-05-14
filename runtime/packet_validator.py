from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _req(packet: Dict[str, Any], keys: List[str], path: str) -> List[str]:
    return [f"{path}: missing '{k}'" for k in keys if k not in packet]


def validate_intake_packet(packet: Dict[str, Any]) -> List[str]:
    return _req(
        packet,
        ["source", "raw_text", "clean_text", "tokens", "input_hash"],
        "intake_packet",
    )


def validate_symbolic_packet(packet: Dict[str, Any]) -> List[str]:
    return _req(
        packet,
        [
            "motifs",
            "symbols",
            "hotspot",
            "threshold_triggered",
            "threshold_reasons",
            "threshold_score",
            "glyph_density",
            "recursion_density",
            "repeat_density",
            "instability_score",
            "emotional_bias",
            "severity",
        ],
        "symbolic_packet",
    )


def validate_memory_packet(packet: Dict[str, Any]) -> List[str]:
    errors: List[str] = _req(
        packet,
        ["shape_signature", "memory_compound_id", "knowledge_node_ids"],
        "memory_packet",
    )

    if "shape_signature" in packet and isinstance(packet["shape_signature"], dict):
        errors += _req(
            packet["shape_signature"],
            ["flow", "boundary", "memory", "novelty", "confidence"],
            "memory_packet.shape_signature",
        )

    return errors


def validate_kernel_packet(packet: Dict[str, Any]) -> List[str]:
    return _req(
        packet,
        ["decision_mode", "governor_flags", "arc_modulation"],
        "kernel_packet",
    )


def validate_holonomy_packet(packet: Dict[str, Any]) -> List[str]:
    errors: List[str] = _req(
        packet,
        ["shape_signature", "derived_metrics", "coherence_field", "ulat_projection"],
        "holonomy_packet",
    )

    if "shape_signature" in packet and isinstance(packet["shape_signature"], dict):
        errors += _req(
            packet["shape_signature"],
            ["flow", "boundary", "memory", "novelty", "confidence"],
            "holonomy_packet.shape_signature",
        )

    if "derived_metrics" in packet and isinstance(packet["derived_metrics"], dict):
        errors += _req(
            packet["derived_metrics"],
            ["coherence", "fracture", "recursion", "tempo", "risk"],
            "holonomy_packet.derived_metrics",
        )

    if "coherence_field" in packet and isinstance(packet["coherence_field"], dict):
        errors += _req(
            packet["coherence_field"],
            ["field_level", "state_tag", "lattice_stability", "harmonic_528", "stability_gate"],
            "holonomy_packet.coherence_field",
        )

    if "ulat_projection" in packet and isinstance(packet["ulat_projection"], dict):
        errors += _req(
            packet["ulat_projection"],
            ["awareness_level", "network_phase", "mode"],
            "holonomy_packet.ulat_projection",
        )

    return errors


def validate_voice_packet(packet: Dict[str, Any]) -> List[str]:
    return _req(
        packet,
        ["final_text", "turn_echo"],
        "voice_packet",
    )


def validate_master_packet(master_packet: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if "intake" in master_packet:
        errors += validate_intake_packet(master_packet["intake"])
    else:
        errors.append("master_packet: missing 'intake'")

    if "symbolic" in master_packet:
        errors += validate_symbolic_packet(master_packet["symbolic"])
    else:
        errors.append("master_packet: missing 'symbolic'")

    if "memory" in master_packet:
        errors += validate_memory_packet(master_packet["memory"])
    else:
        errors.append("master_packet: missing 'memory'")

    if "kernel" in master_packet:
        errors += validate_kernel_packet(master_packet["kernel"])
    else:
        errors.append("master_packet: missing 'kernel'")

    if "holonomy" in master_packet:
        errors += validate_holonomy_packet(master_packet["holonomy"])
    else:
        errors.append("master_packet: missing 'holonomy'")

    if "voice" in master_packet:
        errors += validate_voice_packet(master_packet["voice"])
    else:
        errors.append("master_packet: missing 'voice'")

    return (len(errors) == 0, errors)

