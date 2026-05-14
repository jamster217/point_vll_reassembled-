from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
import hashlib
import json
import math


# =========================================================
# Utility
# =========================================================

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo


def clamp_sym(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return 0.0


# =========================================================
# Timeline / Gate input objects
# =========================================================

@dataclass
class Event:
    id: str
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)
    timeline_id: str = ""
    causal_hash: Optional[str] = None

    def compute_causal_hash(self) -> str:
        if self.causal_hash:
            return self.causal_hash

        raw = json.dumps(
            {
                "id": self.id,
                "timestamp": self.timestamp,
                "payload": self.payload,
                "timeline_id": self.timeline_id,
            },
            sort_keys=True,
        )
        self.causal_hash = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
        return self.causal_hash


@dataclass
class Timeline:
    id: str
    events: List[Event]


@dataclass
class Gate:
    id: str
    src_timeline: str
    src_event_id: str
    dst_timeline: str
    dst_event_id: str


# =========================================================
# ULTK-style trace objects
# =========================================================

@dataclass
class DomainTrace:
    domain_name: str
    question: str
    tokens: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorTrace:
    flow: float
    boundary: float
    memory: float
    novelty: float
    modifiers: Dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, float]:
        return {
            "flow": self.flow,
            "boundary": self.boundary,
            "memory": self.memory,
            "novelty": self.novelty,
        }


@dataclass
class SignatureTrace:
    domain_name: str
    signature_name: str
    vector_profile: Dict[str, float]
    relation_markers: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KeyTrace:
    domain_name: str
    key_units: List[str]
    key_name: str
    weights: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LatticeTrace:
    path_nodes: List[str]
    invariants: Dict[str, float]
    path_summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnswerTrace:
    answer_frame: str
    explanation: str
    rendered_answer: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimelineTranslationResult:
    domain: DomainTrace
    vectors: VectorTrace
    signature: SignatureTrace
    key: KeyTrace
    lattice: LatticeTrace
    answer: AnswerTrace
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    event_signatures: Dict[str, Dict[str, Any]]
    ascii_frames: List[str]


# =========================================================
# Main kernel
# =========================================================

class TimelineGateLatticeTranslationKernel:
    """
    ULTK-style translator for:
        timelines
        -> event signatures
        -> domain key
        -> lattice path
        -> answer frame

    This is structural, not literal time physics.
    """

    def __init__(
        self,
        *,
        time_bin_size: float = 1.0,
        phase_bins: int = 10,
        causal_bins: int = 10,
        causal_edge_threshold: float = 0.90,
    ) -> None:
        self.time_bin_size = max(1e-9, float(time_bin_size))
        self.phase_bins = max(2, int(phase_bins))
        self.causal_bins = max(2, int(causal_bins))
        self.causal_edge_threshold = float(causal_edge_threshold)

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def translate(
        self,
        timelines: List[Timeline],
        gates: List[Gate],
        *,
        question: str = "How do timelines and time gates map into lattice structure?",
        domain_name: str = "time_gates",
    ) -> TimelineTranslationResult:
        event_index = self._index_events(timelines)
        gate_mask_lookup = self._build_gate_masks(gates)
        norm_meta = self._compute_time_range(event_index)

        domain = self._build_domain_trace(question, domain_name, timelines, gates)

        event_signatures: Dict[str, Dict[str, Any]] = {}
        nodes: Dict[str, Dict[str, Any]] = {}

        # Step 1: event vectors and node projection
        for tl in timelines:
            ordered = sorted(tl.events, key=lambda e: e.timestamp)
            total = max(1, len(ordered) - 1)

            for i, event in enumerate(ordered):
                event.timeline_id = tl.id
                phase = i / total if total > 0 else 0.0

                vec = self._event_vector_signature(
                    event=event,
                    phase=phase,
                    norm_meta=norm_meta,
                    gate_mask=gate_mask_lookup.get(event.id, 0),
                )
                qsig = self._quantize_signature(vec)
                key = self._domain_key_for_event(qsig)
                node = self._project_node(event, qsig, key)

                event_signatures[event.id] = {
                    "vector": vec,
                    "quantized": qsig,
                    "key": key,
                    "timeline_id": event.timeline_id,
                }

                if node["id"] not in nodes:
                    nodes[node["id"]] = node
                nodes[node["id"]]["events"].append(event.id)
                if event.timeline_id not in nodes[node["id"]]["timelines"]:
                    nodes[node["id"]]["timelines"].append(event.timeline_id)

        # Step 2: edges
        edges = []
        edges.extend(self._build_temporal_edges(timelines, event_signatures))
        edges.extend(self._build_gate_edges(gates, event_signatures))
        edges.extend(self._build_causal_edges(event_index, event_signatures))

        # Step 3: aggregate vector profile for the whole translation
        vectors = self._build_global_vector_trace(event_signatures)

        # Step 4: signature, key, lattice, answer
        signature = self._build_signature_trace(domain, vectors)
        key = self._build_key_trace(domain, signature)
        lattice = self._build_lattice_trace(nodes, edges, gates)
        answer = self._build_answer_trace(domain, vectors, signature, key, lattice)

        ascii_frames = self._render_ascii_frames(timelines, gates)

        return TimelineTranslationResult(
            domain=domain,
            vectors=vectors,
            signature=signature,
            key=key,
            lattice=lattice,
            answer=answer,
            nodes=list(nodes.values()),
            edges=edges,
            event_signatures=event_signatures,
            ascii_frames=ascii_frames,
        )

    # -----------------------------------------------------
    # Domain layer
    # -----------------------------------------------------

    def _build_domain_trace(
        self,
        question: str,
        domain_name: str,
        timelines: List[Timeline],
        gates: List[Gate],
    ) -> DomainTrace:
        tokens = question.lower().split()
        return DomainTrace(
            domain_name=domain_name,
            question=question,
            tokens=tokens,
            metadata={
                "timeline_count": len(timelines),
                "gate_count": len(gates),
                "translation_mode": "timeline_gate_lattice",
            },
        )

    # -----------------------------------------------------
    # Event indexing + normalization
    # -----------------------------------------------------

    def _index_events(self, timelines: List[Timeline]) -> Dict[str, Event]:
        out: Dict[str, Event] = {}
        for tl in timelines:
            for ev in tl.events:
                ev.timeline_id = tl.id
                out[ev.id] = ev
        return out

    def _compute_time_range(self, event_index: Dict[str, Event]) -> Dict[str, float]:
        if not event_index:
            return {"t_min": 0.0, "t_max": 1.0, "span": 1.0}

        times = [ev.timestamp for ev in event_index.values()]
        t_min = min(times)
        t_max = max(times)
        span = max(1e-9, t_max - t_min)

        return {
            "t_min": t_min,
            "t_max": t_max,
            "span": span,
        }

    def _build_gate_masks(self, gates: List[Gate]) -> Dict[str, int]:
        mask_lookup: Dict[str, int] = defaultdict(int)
        for idx, gate in enumerate(gates):
            bit = 1 << idx
            mask_lookup[gate.src_event_id] |= bit
            mask_lookup[gate.dst_event_id] |= bit
        return mask_lookup

    # -----------------------------------------------------
    # Event signature chain
    # -----------------------------------------------------

    def _event_vector_signature(
        self,
        *,
        event: Event,
        phase: float,
        norm_meta: Dict[str, float],
        gate_mask: int,
    ) -> Dict[str, Any]:
        t_norm = (event.timestamp - norm_meta["t_min"]) / norm_meta["span"]
        causal_score = self._causal_score(event)

        return {
            "t_norm": round(t_norm, 6),
            "phase": round(phase, 6),
            "gate_mask": gate_mask,
            "causal_score": round(causal_score, 6),
        }

    def _causal_score(self, event: Event) -> float:
        h = event.compute_causal_hash()
        n = int(h[:8], 16)
        return n / 0xFFFFFFFF

    def _quantize_signature(self, vector: Dict[str, Any]) -> Dict[str, int]:
        if self.time_bin_size < 1.0:
            t_bin = int(math.floor(vector["t_norm"] / self.time_bin_size))
        else:
            t_bin = int(round(vector["t_norm"] / self.time_bin_size))

        phase_bin = min(self.phase_bins - 1, max(0, int(vector["phase"] * self.phase_bins)))
        causal_bin = min(self.causal_bins - 1, max(0, int(vector["causal_score"] * self.causal_bins)))

        return {
            "t_bin": t_bin,
            "phase_bin": phase_bin,
            "gate_mask": vector["gate_mask"],
            "causal_bin": causal_bin,
        }

    def _domain_key_for_event(self, qsig: Dict[str, int]) -> Dict[str, Any]:
        tup = (
            qsig["t_bin"],
            qsig["phase_bin"],
            qsig["gate_mask"],
            qsig["causal_bin"],
        )
        key = hashlib.sha1(repr(tup).encode("utf-8")).hexdigest()[:10]
        return {
            "key": key,
            "tuple": tup,
        }

    def _project_node(
        self,
        event: Event,
        qsig: Dict[str, int],
        key: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "id": f"N_{key['key']}",
            "coords": (
                self._timeline_axis(event.timeline_id),
                qsig["t_bin"],
                qsig["gate_mask"],
            ),
            "events": [],
            "timelines": [],
            "key": key["key"],
            "quantized": qsig,
        }

    def _timeline_axis(self, timeline_id: str) -> int:
        digits = "".join(ch for ch in timeline_id if ch.isdigit())
        if digits:
            return int(digits)
        return abs(hash(timeline_id)) % 100

    # -----------------------------------------------------
    # Global vector profile
    # -----------------------------------------------------

    def _build_global_vector_trace(
        self,
        event_signatures: Dict[str, Dict[str, Any]],
    ) -> VectorTrace:
        if not event_signatures:
            return VectorTrace(
                flow=0.0,
                boundary=0.0,
                memory=0.0,
                novelty=0.0,
                modifiers={},
            )

        sigs = list(event_signatures.values())
        avg_t = sum(s["vector"]["t_norm"] for s in sigs) / len(sigs)
        avg_phase = sum(s["vector"]["phase"] for s in sigs) / len(sigs)
        avg_gate = sum(1.0 if s["vector"]["gate_mask"] else 0.0 for s in sigs) / len(sigs)
        avg_causal = sum(s["vector"]["causal_score"] for s in sigs) / len(sigs)

        # ULTK-style mapping into 4-axis space
        flow = clamp((avg_t + avg_phase) / 2.0)
        boundary = clamp(0.35 + 0.5 * avg_gate)
        memory = clamp((avg_causal + avg_gate) / 2.0)
        novelty = clamp(1.0 - abs(avg_phase - avg_t))

        modifiers = {
            "avg_time_norm": round(avg_t, 4),
            "avg_phase": round(avg_phase, 4),
            "gate_density": round(avg_gate, 4),
            "avg_causal_score": round(avg_causal, 4),
        }

        return VectorTrace(
            flow=round(flow, 4),
            boundary=round(boundary, 4),
            memory=round(memory, 4),
            novelty=round(novelty, 4),
            modifiers=modifiers,
        )

    # -----------------------------------------------------
    # Signature -> key -> lattice -> answer
    # -----------------------------------------------------

    def _build_signature_trace(
        self,
        domain: DomainTrace,
        vectors: VectorTrace,
    ) -> SignatureTrace:
        vp = vectors.as_dict()
        markers: List[str] = []

        if vp["memory"] > 0.60:
            markers.append("REL_MEMORY")
        if vp["boundary"] > 0.60:
            markers.append("REL_BOUNDARY")
        if vp["flow"] > 0.60:
            markers.append("REL_FLOW")
        if vp["novelty"] > 0.60:
            markers.append("REL_NOVELTY")

        if not markers:
            markers.append("REL_NEUTRAL")

        return SignatureTrace(
            domain_name=domain.domain_name,
            signature_name=f"{domain.domain_name.upper()}_SIGNATURE",
            vector_profile=vp,
            relation_markers=markers,
            metadata={
                "timeline_count": domain.metadata.get("timeline_count", 0),
                "gate_count": domain.metadata.get("gate_count", 0),
            },
        )

    def _build_key_trace(
        self,
        domain: DomainTrace,
        signature: SignatureTrace,
    ) -> KeyTrace:
        if domain.domain_name == "time_gates":
            root = "THRESHOLD_GATE_KEY"
        elif domain.domain_name == "timelines":
            root = "BRANCH_PATH_KEY"
        else:
            root = "TIMELINE_LATTICE_KEY"

        return KeyTrace(
            domain_name=domain.domain_name,
            key_units=[root] + signature.relation_markers,
            key_name=f"{domain.domain_name.upper()}::{root}",
            weights=signature.vector_profile,
            metadata={
                "signature_name": signature.signature_name,
            },
        )

    def _build_lattice_trace(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Dict[str, Any]],
        gates: List[Gate],
    ) -> LatticeTrace:
        merge_nodes = self._find_merge_nodes(edges)
        divergence_nodes = self._find_divergence_nodes(edges)

        path_nodes = []
        if merge_nodes:
            path_nodes.append("NODE_MERGE")
        if divergence_nodes:
            path_nodes.append("NODE_DIVERGENCE")
        if gates:
            path_nodes.append("NODE_GATE")
        if not path_nodes:
            path_nodes.append("NODE_NEUTRAL")

        invariants = {
            "node_count": float(len(nodes)),
            "edge_count": float(len(edges)),
            "gate_count": float(len(gates)),
            "merge_count": float(len(merge_nodes)),
            "divergence_count": float(len(divergence_nodes)),
            "axis_tension": round(
                clamp_sym(
                    (len(divergence_nodes) + len(gates)) - len(merge_nodes)
                ),
                4,
            ),
        }

        if merge_nodes and divergence_nodes:
            summary = "branch_merge_lattice_path"
        elif merge_nodes:
            summary = "convergence_lattice_path"
        elif divergence_nodes:
            summary = "branching_lattice_path"
        elif gates:
            summary = "gate_linked_path"
        else:
            summary = "neutral_path"

        return LatticeTrace(
            path_nodes=path_nodes,
            invariants=invariants,
            path_summary=summary,
            metadata={
                "merge_nodes": merge_nodes,
                "divergence_nodes": divergence_nodes,
            },
        )

    def _build_answer_trace(
        self,
        domain: DomainTrace,
        vectors: VectorTrace,
        signature: SignatureTrace,
        key: KeyTrace,
        lattice: LatticeTrace,
    ) -> AnswerTrace:
        merge_nodes = lattice.metadata.get("merge_nodes", [])
        divergence_nodes = lattice.metadata.get("divergence_nodes", [])

        explanation = (
            f"Domain '{domain.domain_name}' resolves through signature "
            f"'{signature.signature_name}', into key '{key.key_name}', "
            f"then projects through lattice path '{lattice.path_summary}'."
        )

        rendered_answer = (
            f"The timeline/gate system carries "
            f"flow={vectors.flow:.2f}, boundary={vectors.boundary:.2f}, "
            f"memory={vectors.memory:.2f}, novelty={vectors.novelty:.2f}. "
            f"It resolves through the key '{key.key_name}' and lands in a "
            f"'{lattice.path_summary}' pattern. "
            f"There are {len(merge_nodes)} merge nodes and {len(divergence_nodes)} "
            f"divergence nodes, meaning the structure preserves both continuity "
            f"and branching through gate-linked transitions."
        )

        return AnswerTrace(
            answer_frame=f"{domain.domain_name} -> signature -> key -> lattice -> answer",
            explanation=explanation,
            rendered_answer=rendered_answer,
            metadata={
                "merge_nodes": merge_nodes,
                "divergence_nodes": divergence_nodes,
            },
        )

    # -----------------------------------------------------
    # Edge builders
    # -----------------------------------------------------

    def _node_id_for_event(
        self,
        event_id: str,
        event_signatures: Dict[str, Dict[str, Any]],
    ) -> str:
        return f"N_{event_signatures[event_id]['key']['key']}"

    def _build_temporal_edges(
        self,
        timelines: List[Timeline],
        event_signatures: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        edges = []
        for tl in timelines:
            ordered = sorted(tl.events, key=lambda e: e.timestamp)
            for a, b in zip(ordered, ordered[1:]):
                src = self._node_id_for_event(a.id, event_signatures)
                dst = self._node_id_for_event(b.id, event_signatures)
                if src != dst:
                    edges.append({
                        "src": src,
                        "dst": dst,
                        "type": "temporal",
                        "weight": 1.0,
                    })
        return edges

    def _build_gate_edges(
        self,
        gates: List[Gate],
        event_signatures: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        edges = []
        for gate in gates:
            src = self._node_id_for_event(gate.src_event_id, event_signatures)
            dst = self._node_id_for_event(gate.dst_event_id, event_signatures)
            if src != dst:
                edges.append({
                    "src": src,
                    "dst": dst,
                    "type": f"gate:{gate.id}",
                    "weight": 2.0,
                })
        return edges

    def _build_causal_edges(
        self,
        event_index: Dict[str, Event],
        event_signatures: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        edges = []
        ids = list(event_index.keys())

        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a = event_index[ids[i]]
                b = event_index[ids[j]]

                if a.timeline_id == b.timeline_id:
                    continue

                score = self._causal_similarity(a, b)
                if score >= self.causal_edge_threshold:
                    src = self._node_id_for_event(a.id, event_signatures)
                    dst = self._node_id_for_event(b.id, event_signatures)
                    if src != dst:
                        edges.append({
                            "src": src,
                            "dst": dst,
                            "type": "causal",
                            "weight": round(score, 3),
                        })

        return edges

    def _causal_similarity(self, a: Event, b: Event) -> float:
        ha = a.compute_causal_hash()
        hb = b.compute_causal_hash()
        same = sum(1 for x, y in zip(ha, hb) if x == y)
        return same / max(1, min(len(ha), len(hb)))

    # -----------------------------------------------------
    # Summary helpers
    # -----------------------------------------------------

    def _find_merge_nodes(self, edges: List[Dict[str, Any]]) -> List[str]:
        inbound: Dict[str, set] = defaultdict(set)
        for e in edges:
            inbound[e["dst"]].add(e["src"])
        return sorted([node for node, srcs in inbound.items() if len(srcs) >= 2])

    def _find_divergence_nodes(self, edges: List[Dict[str, Any]]) -> List[str]:
        outbound: Dict[str, set] = defaultdict(set)
        for e in edges:
            outbound[e["src"]].add(e["dst"])
        return sorted([node for node, dsts in outbound.items() if len(dsts) >= 2])

    # -----------------------------------------------------
    # Frame rendering
    # -----------------------------------------------------

    def _render_ascii_frames(
        self,
        timelines: List[Timeline],
        gates: List[Gate],
    ) -> List[str]:
        frame = ["Time →"]
        for tl in timelines:
            ordered = sorted(tl.events, key=lambda e: e.timestamp)
            parts = [f"{ev.id}@{ev.timestamp:g}" for ev in ordered]
            frame.append(f"{tl.id}: " + " --- ".join(parts))

        if gates:
            frame.append("")
            frame.append("Gates:")
            for gate in gates:
                frame.append(f"  {gate.id}: {gate.src_event_id} ↔ {gate.dst_event_id}")

        return ["\n".join(frame)]


# =========================================================
# Demo
# =========================================================

if __name__ == "__main__":
    t0 = Timeline(
        id="T0",
        events=[
            Event(id="E0", timestamp=0),
            Event(id="E1", timestamp=5),
            Event(id="E2", timestamp=10),
        ],
    )

    t1 = Timeline(
        id="T1",
        events=[
            Event(id="F0", timestamp=2),
            Event(id="F1", timestamp=6),
            Event(id="F2", timestamp=11),
        ],
    )

    gates = [
        Gate(id="G0", src_timeline="T0", src_event_id="E1", dst_timeline="T1", dst_event_id="F1"),
        Gate(id="G1", src_timeline="T0", src_event_id="E2", dst_timeline="T1", dst_event_id="F2"),
    ]

    kernel = TimelineGateLatticeTranslationKernel(
        time_bin_size=0.1,
        phase_bins=10,
        causal_bins=10,
        causal_edge_threshold=0.95,
    )

    result = kernel.translate(
        [t0, t1],
        gates,
        question="How do branching timelines and time gates preserve continuity through a lattice?",
        domain_name="time_gates",
    )

    print("\n=== DOMAIN ===")
    print(asdict(result.domain))

    print("\n=== VECTORS ===")
    print(asdict(result.vectors))

    print("\n=== SIGNATURE ===")
    print(asdict(result.signature))

    print("\n=== KEY ===")
    print(asdict(result.key))

    print("\n=== LATTICE ===")
    print(asdict(result.lattice))

    print("\n=== ANSWER ===")
    print(asdict(result.answer))

    print("\n=== NODES ===")
    for n in result.nodes:
        print(n)

    print("\n=== EDGES ===")
    for e in result.edges:
        print(e)

    print("\n=== ASCII FRAME ===")
    for frame in result.ascii_frames:
        print(frame)

