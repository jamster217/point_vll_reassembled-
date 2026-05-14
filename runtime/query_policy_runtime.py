from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


DEFAULT_POLICY_PATH = Path("config/query_policy.json")


def _safe_load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


class QueryPolicyRuntime:
    def __init__(self, policy_path: str | Path = DEFAULT_POLICY_PATH) -> None:
        self.policy_path = Path(policy_path)
        self.policy: Dict[str, Any] = _safe_load_json(self.policy_path)

    def reload(self) -> None:
        self.policy = _safe_load_json(self.policy_path)

    def get_default_mode(self) -> str:
        return str(self.policy.get("default_mode", "stabilize"))

    def get_mode_config(self, mode: str | None = None) -> Dict[str, Any]:
        selected = str(mode or self.get_default_mode())
        modes = self.policy.get("modes", {}) or {}
        cfg = modes.get(selected, {}) or {}
        if not isinstance(cfg, dict):
            return {}
        return cfg

    def resolve_runtime_packet(self, mode: str | None = None) -> Dict[str, Any]:
        cfg = self.get_mode_config(mode)
        hardening = self.policy.get("hardening", {}) or {}
        metrics = self.policy.get("metrics", {}) or {}

        return {
            "mode": str(mode or self.get_default_mode()),
            "posture": cfg.get("posture", "guided_balance"),
            "architecture_bias": cfg.get("architecture_bias", "hub_coordinated"),
            "compression_cycles": bool(cfg.get("compression_cycles", False)),
            "compression_aggression": str(cfg.get("compression_aggression", "off")),
            "seal_signatures": bool(cfg.get("seal_signatures", False)),
            "recursion_mode": str(cfg.get("recursion_mode", "bounded")),
            "recursion_target": float(cfg.get("recursion_target", 0.45)),
            "awareness_mode": str(cfg.get("awareness_mode", "observe")),
            "awareness_target_min": float(cfg.get("awareness_target_min", 0.72)),
            "fracture_target_max": float(cfg.get("fracture_target_max", 0.22)),
            "stability_gate_target_min": float(cfg.get("stability_gate_target_min", 0.90)),
            "hardening": hardening,
            "metrics": metrics,
            "notes": list(cfg.get("notes", []) or []),
        }


if __name__ == "__main__":
    rt = QueryPolicyRuntime()
    for name in ("stabilize", "query", "explore"):
        print(f"=== {name.upper()} ===")
        print(json.dumps(rt.resolve_runtime_packet(name), indent=2))

