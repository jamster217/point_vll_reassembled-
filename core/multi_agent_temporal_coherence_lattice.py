# core/multi_agent_temporal_coherence_lattice.py

from __future__ import annotations

"""
Multi-Agent Temporal Coherence Lattice (MATCL)

A safe "time-machine-like" simulator in software:

- No real time travel
- Builds a lattice of timeline branches
- Uses multiple agents to evaluate future coherence of decisions
- Selects the decision that yields the highest consensus coherence,
  with conflict detection and stability penalties
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import hashlib
import math
import time


AgentFn = Callable[[str, Dict[str, Any]], Tuple[float, List[str]]]
SimulateMap = Dict[str, AgentFn]


@dataclass
class AgentEvaluation:
    agent: str
    score: float
    notes: List[str] = field(default_factory=list)


@dataclass
class TemporalNode:
    node_id: str
    parent_id: Optional[str]
    decision: str
    timestamp: float
    evaluations: List[AgentEvaluation] = field(default_factory=list)
    consensus: float = 0.0
    conflict: float = 0.0
    stability: float = 0.0
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionReport:
    decision: str
    consensus: float
    conflict: float
    stability: float
    per_agent: Dict[str, float]
    notes: Dict[str, List[str]]


@dataclass
class LatticeSelection:
    chosen_decision: str
    chosen_node_id: str
    ranked: List[DecisionReport]
    policy: str
    timestamp: float = field(default_factory=time.time)


def _h(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs: List[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return math.sqrt(var)


def _median(xs: List[float]) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 == 1 else 0.5 * (s[mid - 1] + s[mid])


def _softmax(xs: List[float], temp: float = 1.0) -> List[float]:
    if not xs:
        return []
    m = max(xs)
    exps = [math.exp((x - m) / max(1e-6, temp)) for x in xs]
    s = sum(exps)
    return [e / s for e in exps] if s > 0 else [1.0 / len(xs)] * len(xs)


class MultiAgentTemporalCoherenceLattice:
    """
    Maintains a lattice of temporal nodes.

    Policies:
    - mean_penalized
    - median_penalized
    - minimax
    - soft_consensus
    """

    def __init__(
        self,
        *,
        policy: str = "mean_penalized",
        conflict_alpha: float = 0.6,
        depth_beta: float = 0.03,
        recency_gamma: float = 0.0,
        softmax_temp: float = 0.7,
        max_nodes: int = 10_000,
    ) -> None:
        self.policy = policy
        self.conflict_alpha = conflict_alpha
        self.depth_beta = depth_beta
        self.recency_gamma = recency_gamma
        self.softmax_temp = softmax_temp
        self.max_nodes = max_nodes

        self.nodes: Dict[str, TemporalNode] = {}
        self.root_id = self._ensure_root()

    def select_decision(
        self,
        *,
        current_node_id: Optional[str],
        candidate_decisions: List[str],
        simulate_map: SimulateMap,
        context: Optional[Dict[str, Any]] = None,
        depth: int = 2,
        branch_factor: int = 1,
    ) -> LatticeSelection:
        context = context or {}
        parent = current_node_id or self.root_id

        reports: List[DecisionReport] = []
        created_node_ids: Dict[str, str] = {}

        for dec in candidate_decisions:
            node = self._evaluate_decision(
                parent_id=parent,
                decision=dec,
                simulate_map=simulate_map,
                context=context,
            )

            if depth > 0:
                node = self._apply_future_echo(
                    node,
                    simulate_map,
                    context,
                    depth=depth,
                )

            self.nodes[node.node_id] = node
            created_node_ids[dec] = node.node_id

            reports.append(
                DecisionReport(
                    decision=dec,
                    consensus=node.consensus,
                    conflict=node.conflict,
                    stability=node.stability,
                    per_agent={ev.agent: ev.score for ev in node.evaluations},
                    notes={ev.agent: ev.notes for ev in node.evaluations},
                )
            )

        reports.sort(key=lambda r: (r.stability, r.consensus), reverse=True)

        chosen = reports[0]
        chosen_id = created_node_ids.get(chosen.decision, self.root_id)

        return LatticeSelection(
            chosen_decision=chosen.decision,
            chosen_node_id=chosen_id,
            ranked=reports,
            policy=self.policy,
        )

    def get_node(self, node_id: str) -> Optional[TemporalNode]:
        return self.nodes.get(node_id)

    def path_to_root(self, node_id: str, limit: int = 50) -> List[TemporalNode]:
        path: List[TemporalNode] = []
        cur = self.nodes.get(node_id)

        while cur and len(path) < limit:
            path.append(cur)
            if not cur.parent_id:
                break
            cur = self.nodes.get(cur.parent_id)

        return path

    def _ensure_root(self) -> str:
        rid = _h("root", "0")
        if rid not in self.nodes:
            self.nodes[rid] = TemporalNode(
                node_id=rid,
                parent_id=None,
                decision="ROOT",
                timestamp=time.time(),
                evaluations=[],
                consensus=0.5,
                conflict=0.0,
                stability=0.5,
                meta={"root": True},
            )
        return rid

    def _evaluate_decision(
        self,
        *,
        parent_id: str,
        decision: str,
        simulate_map: SimulateMap,
        context: Dict[str, Any],
    ) -> TemporalNode:
        node_id = _h(parent_id, decision, str(time.time()))
        evals: List[AgentEvaluation] = []

        for agent, fn in simulate_map.items():
            try:
                score, notes = fn(decision, context)
                s = float(score)
                if 0.0 <= s <= 1.0:
                    s_clamped = s
                else:
                    s_clamped = _clamp01(0.5 + 0.5 * math.tanh(s))

                evals.append(
                    AgentEvaluation(
                        agent=agent,
                        score=s_clamped,
                        notes=list(notes or []),
                    )
                )
            except Exception as e:
                evals.append(
                    AgentEvaluation(
                        agent=agent,
                        score=0.0,
                        notes=[f"error:{type(e).__name__}"],
                    )
                )

        scores = [e.score for e in evals]
        consensus, conflict = self._aggregate(scores)

        depth = self._depth(parent_id)
        depth_pen = self.depth_beta * depth
        recency_pen = self.recency_gamma * 0.0
        stability = consensus - depth_pen - recency_pen

        node = TemporalNode(
            node_id=node_id,
            parent_id=parent_id,
            decision=decision,
            timestamp=time.time(),
            evaluations=evals,
            consensus=consensus,
            conflict=conflict,
            stability=stability,
            meta={
                "depth": depth,
                "depth_penalty": depth_pen,
                "recency_penalty": recency_pen,
            },
        )

        if len(self.nodes) > self.max_nodes:
            self._prune_oldest(keep=int(self.max_nodes * 0.85))

        return node

    def _apply_future_echo(
        self,
        node: TemporalNode,
        simulate_map: SimulateMap,
        context: Dict[str, Any],
        *,
        depth: int,
    ) -> TemporalNode:
        depth = max(0, int(depth))
        if depth <= 0:
            return node

        future_context = dict(context)
        future_context["_future_echo"] = future_context.get("_future_echo", 0) + 1
        future_context["_echo_of"] = node.decision

        now_cons = node.consensus
        now_conf = node.conflict

        cons_vals = [now_cons]
        conf_vals = [now_conf]

        parent_id = node.node_id
        dec = node.decision

        for _ in range(depth):
            echo_node = self._evaluate_decision(
                parent_id=parent_id,
                decision=dec,
                simulate_map=simulate_map,
                context=future_context,
            )

            # Store the future echo as an actual temporal bead in the lattice.
            # Without this, the echo only affects scoring and disappears.
            echo_node.meta["future_echo_node"] = True
            echo_node.meta["echo_depth_index"] = future_context["_future_echo"]
            echo_node.meta["echo_of_root_decision"] = node.decision
            self.nodes[echo_node.node_id] = echo_node

            cons_vals.append(echo_node.consensus)
            conf_vals.append(echo_node.conflict)
            parent_id = echo_node.node_id
            future_context["_future_echo"] += 1

        echo_cons = _mean(cons_vals[1:]) if len(cons_vals) > 1 else now_cons
        echo_conf = _mean(conf_vals[1:]) if len(conf_vals) > 1 else now_conf

        blended_cons = 0.72 * now_cons + 0.28 * echo_cons
        blended_conf = 0.72 * now_conf + 0.28 * echo_conf

        depth_pen = node.meta.get("depth_penalty", 0.0)
        recency_pen = node.meta.get("recency_penalty", 0.0)
        blended_stability = blended_cons - depth_pen - recency_pen

        node.consensus = blended_cons
        node.conflict = blended_conf
        node.stability = blended_stability
        node.meta["future_echo_depth"] = depth
        node.meta["echo_consensus"] = echo_cons
        node.meta["echo_conflict"] = echo_conf

        return node

    def _aggregate(self, scores: List[float]) -> Tuple[float, float]:
        if not scores:
            return 0.0, 1.0

        conflict = _std(scores)

        if self.policy == "minimax":
            base = min(scores)
        elif self.policy == "median_penalized":
            base = _median(scores)
        elif self.policy == "soft_consensus":
            w = _softmax(scores, temp=self.softmax_temp)
            base = sum(s * wi for s, wi in zip(scores, w))
        else:
            base = _mean(scores)

        consensus = base - self.conflict_alpha * conflict
        return _clamp01(consensus), _clamp01(conflict)

    def _depth(self, node_id: str) -> int:
        if node_id == self.root_id:
            return 0

        depth = 0
        cur = self.nodes.get(node_id)
        while cur and cur.parent_id and depth < 200:
            depth += 1
            cur = self.nodes.get(cur.parent_id)
        return depth

    def _prune_oldest(self, keep: int = 5000) -> None:
        if keep < 100:
            keep = 100

        items = [n for n in self.nodes.values() if not n.meta.get("root")]
        items.sort(key=lambda n: n.timestamp)

        to_remove = max(0, len(items) - keep)
        for i in range(to_remove):
            self.nodes.pop(items[i].node_id, None)


def default_agents(identity: Optional[Dict[str, Any]] = None) -> SimulateMap:
    """
    Returns multi-agent simulate functions.

    Each agent answers:
    'If we choose this decision, how coherent is the future?'
    """
    identity = identity or {}
    stance = identity.get("stance", "coherent")
    restraint = float(identity.get("restraint", 0.8))
    novelty_bias = float(identity.get("novelty_bias", 0.35))

    def _agent_engineering(decision: str, ctx: Dict[str, Any]) -> Tuple[float, List[str]]:
        low = decision.lower()
        score = 0.55
        notes: List[str] = []

        if any(k in low for k in ("test", "rollback", "fail-open", "deterministic", "invariant")):
            score += 0.25
            notes.append("safety:+")
        if any(k in low for k in ("rewrite everything", "delete", "wipe")):
            score -= 0.25
            notes.append("risk:-")

        return _clamp01(score), notes

    def _agent_identity(decision: str, ctx: Dict[str, Any]) -> Tuple[float, List[str]]:
        low = decision.lower()
        score = 0.55
        notes: List[str] = []

        if stance == "cautious" and ("careful" in low or "grounded" in low):
            score += 0.20
            notes.append("stance_match:+")
        if stance == "decisive" and ("commit" in low or "lock" in low):
            score += 0.15
            notes.append("decisive:+")
        if restraint > 0.85 and any(k in low for k in ("ultimate", "perfect", "infinite", "perpetual")):
            score -= 0.30
            notes.append("dehype:-")

        return _clamp01(score), notes

    def _agent_novelty(decision: str, ctx: Dict[str, Any]) -> Tuple[float, List[str]]:
        risk = float(ctx.get("risk", 0.0))
        low = decision.lower()
        score = 0.50 + 0.15 * novelty_bias
        notes: List[str] = []

        if risk < 0.2 and any(k in low for k in ("new", "novel", "evolve", "lattice", "simulate")):
            score += 0.20
            notes.append("novelty:+")
        if risk > 0.4:
            score -= 0.15
            notes.append("risk_damp:-")

        return _clamp01(score), notes

    def _agent_pragmatic(decision: str, ctx: Dict[str, Any]) -> Tuple[float, List[str]]:
        low = decision.lower()
        score = 0.60
        notes: List[str] = []

        if len(decision) < 30:
            score -= 0.10
            notes.append("too_vague:-")
        if any(k in low for k in ("step", "wire", "add", "implement", "create")):
            score += 0.15
            notes.append("actionable:+")

        return _clamp01(score), notes

    return {
        "engineering": _agent_engineering,
        "identity": _agent_identity,
        "novelty": _agent_novelty,
        "pragmatic": _agent_pragmatic,
    }