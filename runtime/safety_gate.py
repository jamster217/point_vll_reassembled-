from __future__ import annotations

from typing import Any, Dict

from optimizer.optimizer_safety import OptimizerSafetyPolicy


class SafetyGate:
    """
    Runtime integration layer for OptimizerSafetyPolicy.
    Called before:
      - rewrite decisions
      - recursion / mirror deepening
      - symbolic escalation
      - output shaping
    """

    def __init__(self, safety_policy: OptimizerSafetyPolicy) -> None:
        self.safety_policy = safety_policy

    def evaluate(self, master_packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        master_packet is expected to contain:
          - intake
          - symbolic
          - memory
          - holonomy
          - voice
        """
        intake_packet = master_packet.get("intake", {}) or {}
        symbolic_packet = master_packet.get("symbolic", {}) or {}
        memory_packet = master_packet.get("memory", {}) or {}
        holonomy_packet = master_packet.get("holonomy", {}) or {}

        threshold_packet = symbolic_packet
        motifs = list(symbolic_packet.get("motifs", []) or [])
        shape_signature = dict(memory_packet.get("shape_signature", {}) or {})
        derived_metrics = dict(holonomy_packet.get("derived_metrics", {}) or {})
        input_text = str(intake_packet.get("clean_text", "") or "")

        decision = self.safety_policy.evaluate(
            input_text=input_text,
            threshold_packet=threshold_packet,
            motifs=motifs,
            shape_signature=shape_signature,
            derived_metrics=derived_metrics,
        )
        return decision


def apply_safety_decision(final_text: str, decision: Dict[str, Any]) -> Dict[str, Any]:
    """
    Small helper the runtime can use immediately.
    Returns a packet describing what to do next.
    """
    final_text = str(final_text or "")
    severity = str(decision.get("severity", "low") or "low")

    if decision.get("stabilize_output"):
        stabilized = final_text
        if severity == "high" and final_text:
            stabilized = final_text.strip()
        return {
            "mode": "stabilized",
            "final_text": stabilized,
            "allow_rewrite": False,
            "allow_recursion": False,
            "stabilize_output": True,
            "decision": decision,
        }

    return {
        "mode": "normal",
        "final_text": final_text,
        "allow_rewrite": bool(decision.get("allow_rewrite", True)),
        "allow_recursion": bool(decision.get("allow_recursion", True)),
        "stabilize_output": bool(decision.get("stabilize_output", False)),
        "decision": decision,
    }

