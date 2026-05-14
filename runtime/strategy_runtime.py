#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


# =========================================================
# DATA MODELS
# =========================================================

@dataclass
class StrategyDirective:
    area: str
    action: str
    priority: str
    rationale: str


@dataclass
class StrategyPlan:
    strategy_version: int
    strategic_posture: str
    exploration_mode: str
    consolidation_mode: str
    architecture_bias: str
    cycle_intent: str
    confidence: float
    directives: List[StrategyDirective]
    preferred_node_roles: List[str]
    discouraged_node_roles: List[str]
    simulator_bias: Dict[str, Any]
    synthesis_bias: Dict[str, Any]
    governance_echo: List[str]
    observatory_echo: List[str]


# =========================================================
# HELPERS
# =========================================================

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def load_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_strategy_plan(raw: Dict[str, Any]) -> StrategyPlan:
    directives = [
        StrategyDirective(
            area=d["area"],
            action=d["action"],
            priority=d["priority"],
            rationale=d["rationale"],
        )
        for d in raw.get("directives", [])
    ]

    return StrategyPlan(
        strategy_version=int(raw["strategy_version"]),
        strategic_posture=raw["strategic_posture"],
        exploration_mode=raw["exploration_mode"],
        consolidation_mode=raw["consolidation_mode"],
        architecture_bias=raw["architecture_bias"],
        cycle_intent=raw["cycle_intent"],
        confidence=float(raw["confidence"]),
        directives=directives,
        preferred_node_roles=list(raw.get("preferred_node_roles", [])),
        discouraged_node_roles=list(raw.get("discouraged_node_roles", [])),
        simulator_bias=dict(raw.get("simulator_bias", {})),
        synthesis_bias=dict(raw.get("synthesis_bias", {})),
        governance_echo=list(raw.get("governance_echo", [])),
        observatory_echo=list(raw.get("observatory_echo", [])),
    )


def load_strategy_plan(path: str | Path = "strategy_plan.json") -> Optional[StrategyPlan]:
    p = Path(path)
    if not p.exists():
        return None
    try:
        raw = load_json(p)
        return parse_strategy_plan(raw)
    except Exception:
        return None


# =========================================================
# SIMULATOR BRIDGE
# =========================================================

class StrategyRuntimeBridge:
    """
    Shared adapter that lets simulator + synthesizer obey strategy_plan.json.
    """

    def __init__(self, strategy: Optional[StrategyPlan]) -> None:
        self.strategy = strategy

    # ----------------------------
    # simulator knobs
    # ----------------------------

    def simulator_novelty_weight(self, default: float) -> float:
        if not self.strategy:
            return default
        return float(self.strategy.simulator_bias.get("novelty_weight", default))

    def simulator_compression_weight(self, default: float) -> float:
        if not self.strategy:
            return default
        return float(self.strategy.simulator_bias.get("compression_weight", default))

    def simulator_tail_pruning_pressure(self, default: str = "normal") -> str:
        if not self.strategy:
            return default
        return str(self.strategy.simulator_bias.get("tail_pruning_pressure", default))

    def simulator_seed_diversity_mode(self, default: str = "balanced") -> str:
        if not self.strategy:
            return default
        return str(self.strategy.simulator_bias.get("seed_diversity_mode", default))

    def simulator_replacement_trial_bias(self, default: str = "normal") -> str:
        if not self.strategy:
            return default
        return str(self.strategy.simulator_bias.get("replacement_trial_bias", default))

    def simulator_promotion_threshold_hint(self, default: Optional[float] = None) -> Optional[float]:
        if not self.strategy:
            return default
        value = self.strategy.simulator_bias.get("promotion_threshold_hint", default)
        return None if value is None else float(value)

    def apply_seed_score_bias(
        self,
        base_score: float,
        label: str,
        node_role: str,
    ) -> float:
        if not self.strategy:
            return round(clamp(base_score, 0.0, 1.0), 3)

        score = base_score
        label_l = label.lower()

        posture = self.strategy.strategic_posture
        preferred = set(self.strategy.preferred_node_roles)
        discouraged = set(self.strategy.discouraged_node_roles)

        if node_role in preferred:
            score += 0.06
        if node_role in discouraged:
            score -= 0.10

        if posture == "stabilize_and_compress":
            if node_role in {"schema", "policy", "registry"}:
                score += 0.05
            if "tail" in label_l or "echo" in label_l:
                score -= 0.12

        elif posture == "refine_and_expand":
            if "hub" in label_l or "routing" in label_l or "archetype" in label_l:
                score += 0.05
            if node_role == "module":
                score += 0.03

        elif posture == "guided_balance":
            if node_role in {"policy", "schema"}:
                score += 0.03

        return round(clamp(score, 0.0, 1.0), 3)

    def apply_tail_pruning_rule(
        self,
        label: str,
        node_type: str,
        weight: int,
        age: int,
        default_should_prune: bool,
    ) -> bool:
        if not self.strategy:
            return default_should_prune

        pressure = self.simulator_tail_pruning_pressure("normal")
        label_l = label.lower()

        if pressure == "high":
            if node_type in {"echo", "tail_concept"} and weight <= 2 and age > 80:
                return True
            if ("concept_" in label_l or "low_weight" in label_l) and weight <= 2 and age > 120:
                return True

        if pressure == "normal":
            if node_type == "echo" and weight <= 1 and age > 120:
                return True

        return default_should_prune

    # ----------------------------
    # synthesizer knobs
    # ----------------------------

    def synthesizer_prefers_modules(self, default: bool = True) -> bool:
        if not self.strategy:
            return default
        return bool(self.strategy.synthesis_bias.get("prefer_modules", default))

    def synthesizer_prefers_policies(self, default: bool = True) -> bool:
        if not self.strategy:
            return default
        return bool(self.strategy.synthesis_bias.get("prefer_policies", default))

    def synthesizer_prefers_schemas(self, default: bool = True) -> bool:
        if not self.strategy:
            return default
        return bool(self.strategy.synthesis_bias.get("prefer_schemas", default))

    def synthesizer_prefers_registries(self, default: bool = True) -> bool:
        if not self.strategy:
            return default
        return bool(self.strategy.synthesis_bias.get("prefer_registries", default))

    def synthesizer_replacement_aggression(self, default: str = "moderate") -> str:
        if not self.strategy:
            return default
        return str(self.strategy.synthesis_bias.get("replacement_aggression", default))

    def synthesizer_overlay_bias(self, default: str = "moderate") -> str:
        if not self.strategy:
            return default
        return str(self.strategy.synthesis_bias.get("overlay_bias", default))

    def synthesizer_schema_hardening(self, default: str = "moderate") -> str:
        if not self.strategy:
            return default
        return str(self.strategy.synthesis_bias.get("schema_hardening", default))

    def override_role(self, label: str, current_role: str) -> str:
        if not self.strategy:
            return current_role

        label_l = label.lower()
        posture = self.strategy.strategic_posture
        bias = self.strategy.architecture_bias

        if posture == "stabilize_and_compress":
            if "schema" in label_l or "gate" in label_l or "stability" in label_l:
                return "schema"
            if current_role == "module":
                return "policy"

        if bias == "policy_hardened":
            if current_role == "module":
                return "policy"

        if bias == "hub_coordinated":
            if "hub" in label_l or "routing" in label_l or "archetype" in label_l:
                return "module"

        return current_role

    def allow_synthesis(self, label: str, node_type: str, role: str, default: bool = True) -> bool:
        if not self.strategy:
            return default

        label_l = label.lower()
        discouraged = set(self.strategy.discouraged_node_roles)

        if node_type in {"echo", "tail_concept"}:
            return False

        if role in discouraged:
            return False

        if "replacement_heavy_module" in discouraged and role == "module" and (
            "hub" in label_l or "routing" in label_l
        ):
            return False

        return default

    def build_cycle_echo(self) -> Dict[str, Any]:
        if not self.strategy:
            return {
                "strategy_loaded": False,
                "strategic_posture": "none",
                "cycle_intent": "none",
            }

        return {
            "strategy_loaded": True,
            "strategic_posture": self.strategy.strategic_posture,
            "architecture_bias": self.strategy.architecture_bias,
            "cycle_intent": self.strategy.cycle_intent,
            "confidence": self.strategy.confidence,
        }


# =========================================================
# CLI
# =========================================================

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Load and inspect strategy plan runtime bridge."
    )
    parser.add_argument(
        "--strategy-input",
        default="strategy_plan.json",
        help="Path to strategy_plan.json",
    )
    args = parser.parse_args()

    strategy = load_strategy_plan(args.strategy_input)
    bridge = StrategyRuntimeBridge(strategy)

    print(json.dumps({
        "loaded": strategy is not None,
        "cycle_echo": bridge.build_cycle_echo(),
        "novelty_weight": bridge.simulator_novelty_weight(0.18),
        "compression_weight": bridge.simulator_compression_weight(0.62),
        "tail_pruning_pressure": bridge.simulator_tail_pruning_pressure(),
        "replacement_trial_bias": bridge.simulator_replacement_trial_bias(),
        "schema_hardening": bridge.synthesizer_schema_hardening(),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

