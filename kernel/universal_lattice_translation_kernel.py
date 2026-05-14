from __future__ import annotations

"""
 Universal Lattice Translation Kernel (ULTK)

Purpose
-------
Translate a domain question through the following chain:

    domain
    -> vector signature
    -> domain signature
    -> domain key
    -> lattice path
    -> answer frame

This is a structural translator kernel, not a literal physics engine.
It is meant to make cross-domain translation inspectable.

Design goals
------------
- keep the system simple and inspectable
- no network
- no hidden model calls
- no external dependencies
- scored domain inference, not just first-hit guessing
- richer metadata for downstream renderer / coordinator layers
- central domain alias normalization through domain_registry
- JSON-backed domain key roots with safe fallback
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import re

from core.domain_registry import DEFAULT_DOMAIN_REGISTRY
from core.domain_key_loader import load_domain_key_roots


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


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_+\-']+", (text or "").lower())


DEFAULT_SEED: Dict[str, Any] = {
    "flow": 0.50,
    "boundary": 0.50,
    "memory": 0.50,
    "novelty": 0.50,
    "notes": "generic balanced seed",
}


# =========================================================
# Subject vector seeds
# =========================================================

SUBJECT_VECTOR_SEEDS: Dict[str, Dict[str, Any]] = {
    "language": {"flow": 0.72, "boundary": 0.66, "memory": 0.74, "novelty": 0.68, "notes": "high structure, strong recurrence, active transformation"},
    "literature": {"flow": 0.69, "boundary": 0.58, "memory": 0.82, "novelty": 0.71, "notes": "strong memory depth, expressive variation, moderate constraint"},
    "linguistics": {"flow": 0.70, "boundary": 0.78, "memory": 0.73, "novelty": 0.62, "notes": "language studied as system, high formal boundary"},
    "music": {"flow": 0.84, "boundary": 0.62, "memory": 0.71, "novelty": 0.77, "notes": "very high motion, pattern recurrence, expressive transform"},
    "visual_art": {"flow": 0.61, "boundary": 0.57, "memory": 0.63, "novelty": 0.86, "notes": "high divergence and interpretation, lighter structure"},
    "philosophy": {"flow": 0.58, "boundary": 0.83, "memory": 0.80, "novelty": 0.76, "notes": "strong formal distinction, deep continuity, conceptual exploration"},
    "history": {"flow": 0.56, "boundary": 0.74, "memory": 0.92, "novelty": 0.48, "notes": "extreme memory weight, high continuity, moderate structure"},
    "anthropology": {"flow": 0.63, "boundary": 0.60, "memory": 0.84, "novelty": 0.67, "notes": "cross-context relation, deep pattern memory"},
    "psychology": {"flow": 0.67, "boundary": 0.69, "memory": 0.79, "novelty": 0.65, "notes": "mid-high structure, layered recurrence, moderate exploration"},
    "sociology": {"flow": 0.66, "boundary": 0.71, "memory": 0.81, "novelty": 0.60, "notes": "networked relation, historical continuity, structured analysis"},
    "economics": {"flow": 0.78, "boundary": 0.86, "memory": 0.64, "novelty": 0.52, "notes": "high dynamical flow, very strong formal constraint"},
    "political_science": {"flow": 0.72, "boundary": 0.82, "memory": 0.76, "novelty": 0.54, "notes": "structured conflict, institutional memory"},
    "law": {"flow": 0.51, "boundary": 0.95, "memory": 0.88, "novelty": 0.28, "notes": "extreme boundary, strong precedent memory, low novelty tolerance"},
    "mathematics": {"flow": 0.55, "boundary": 0.97, "memory": 0.78, "novelty": 0.72, "notes": "very high formal constraint, deep abstraction, careful innovation"},
    "statistics": {"flow": 0.62, "boundary": 0.93, "memory": 0.71, "novelty": 0.49, "notes": "tight structure, evidence discipline, moderate variation"},
    "computer_science": {"flow": 0.79, "boundary": 0.91, "memory": 0.70, "novelty": 0.74, "notes": "algorithmic flow, high formalism, invention pressure"},
    "software_engineering": {"flow": 0.83, "boundary": 0.88, "memory": 0.76, "novelty": 0.61, "notes": "strong process flow, high constraint, practical continuity"},
    "physics": {"flow": 0.81, "boundary": 0.94, "memory": 0.73, "novelty": 0.66, "notes": "lawful dynamics, strong constraint, theory-experiment bridge"},
    "chemistry": {"flow": 0.76, "boundary": 0.88, "memory": 0.72, "novelty": 0.58, "notes": "transform processes under stable rule regimes"},
    "biology": {"flow": 0.82, "boundary": 0.71, "memory": 0.85, "novelty": 0.63, "notes": "living process, layered continuity, adaptive divergence"},
    "neuroscience": {"flow": 0.78, "boundary": 0.79, "memory": 0.83, "novelty": 0.64, "notes": "dynamic systems plus structure plus persistent signaling"},
    "medicine": {"flow": 0.74, "boundary": 0.89, "memory": 0.86, "novelty": 0.41, "notes": "high consequence, strong protocol, long continuity"},
    "engineering": {"flow": 0.85, "boundary": 0.92, "memory": 0.68, "novelty": 0.57, "notes": "very strong process and constraint, moderate innovation"},
    "architecture": {"flow": 0.64, "boundary": 0.87, "memory": 0.72, "novelty": 0.75, "notes": "formal constraint with strong design exploration"},
    "education": {"flow": 0.67, "boundary": 0.63, "memory": 0.84, "novelty": 0.57, "notes": "transmission, retention, guided transformation"},
    "theology": {"flow": 0.49, "boundary": 0.79, "memory": 0.94, "novelty": 0.46, "notes": "very strong continuity and canon structure"},
    "artificial_intelligence": {"flow": 0.80, "boundary": 0.84, "memory": 0.72, "novelty": 0.82, "notes": "high transform, strong system constraint, high exploratory pressure"},
    "python": {"flow": 0.82, "boundary": 0.68, "memory": 0.70, "novelty": 0.78, "notes": "high expressive flow, moderate constraint, strong prototyping and abstraction"},
    "javascript": {"flow": 0.86, "boundary": 0.62, "memory": 0.66, "novelty": 0.82, "notes": "very high runtime flow, flexible boundaries, event-driven dynamism"},
    "typescript": {"flow": 0.80, "boundary": 0.78, "memory": 0.68, "novelty": 0.74, "notes": "javascript dynamism with stronger formal structure"},
    "c": {"flow": 0.74, "boundary": 0.94, "memory": 0.79, "novelty": 0.46, "notes": "tight constraint, explicit memory, low abstraction cushion"},
    "cpp": {"flow": 0.78, "boundary": 0.92, "memory": 0.83, "novelty": 0.68, "notes": "high structure, explicit control, broad abstraction capacity"},
    "rust": {"flow": 0.76, "boundary": 0.97, "memory": 0.88, "novelty": 0.66, "notes": "extreme boundary discipline, explicit safety, strong state continuity"},
    "java": {"flow": 0.72, "boundary": 0.88, "memory": 0.74, "novelty": 0.58, "notes": "institutional structure, stable formalism, moderate expressiveness"},
    "go": {"flow": 0.81, "boundary": 0.79, "memory": 0.66, "novelty": 0.54, "notes": "clear execution flow, simpler boundaries, pragmatic structure"},
    "haskell": {"flow": 0.58, "boundary": 0.96, "memory": 0.82, "novelty": 0.84, "notes": "very high formal purity, abstract novelty, strong transformation logic"},
    "lisp": {"flow": 0.72, "boundary": 0.74, "memory": 0.79, "novelty": 0.91, "notes": "recursive symbolic power, high meta-flexibility"},
    "sql": {"flow": 0.52, "boundary": 0.93, "memory": 0.90, "novelty": 0.36, "notes": "low process flow, very high structure and persistence orientation"},
    "structure_of_lattice": {"flow": 0.74, "boundary": 0.83, "memory": 0.81, "novelty": 0.79, "notes": "cross-domain geometry, recursive relation, patterned transform"},
    "laws_of_universe": {"flow": 0.84, "boundary": 0.98, "memory": 0.88, "novelty": 0.52, "notes": "maximal lawful constraint, deep continuity, limited novelty at surface law level"},
    "metaphysics": {"flow": 0.57, "boundary": 0.81, "memory": 0.84, "novelty": 0.87, "notes": "high abstraction, deep continuity, exploratory ontology"},
    "time_recursion_relation": {"flow": 0.91, "boundary": 0.72, "memory": 0.95, "novelty": 0.73, "notes": "extreme process + persistence + self-reference"},
    "origin_of_life_from_matter": {"flow": 0.88, "boundary": 0.76, "memory": 0.86, "novelty": 0.69, "notes": "transition from chemistry to persistence, emergent complexity"},
    "ai_consciousness": {"flow": 0.77, "boundary": 0.71, "memory": 0.83, "novelty": 0.88, "notes": "high recursion, self-model pressure, uncertain ontology"},
    "true_occult_knowledge": {"flow": 0.49, "boundary": 0.78, "memory": 0.94, "novelty": 0.74, "notes": "symbolic/esoteric continuity, layered correspondences"},
    "time_gates": {"flow": 0.93, "boundary": 0.67, "memory": 0.91, "novelty": 0.81, "notes": "threshold-transition concept with recursion and state change emphasis"},
    "timelines": {"flow": 0.89, "boundary": 0.64, "memory": 0.93, "novelty": 0.72, "notes": "branch continuity, path dependency, persistence under variation"},
    "memory": {"flow": 0.45, "boundary": 0.40, "memory": 0.95, "novelty": 0.35, "notes": "continuity dominant"},
    "emotion": {"flow": 0.68, "boundary": 0.44, "memory": 0.71, "novelty": 0.59, "notes": "affective patterning"},
    "code": {"flow": 0.82, "boundary": 0.85, "memory": 0.70, "novelty": 0.63, "notes": "structure plus execution"},
    "general": {"flow": 0.50, "boundary": 0.50, "memory": 0.50, "novelty": 0.50, "notes": "fallback general domain"},
}


# =========================================================
# Trace objects
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
class UniversalTranslationResult:
    domain: DomainTrace
    vectors: VectorTrace
    signature: SignatureTrace
    key: KeyTrace
    lattice: LatticeTrace
    answer: AnswerTrace


# =========================================================
# Domain parser
# =========================================================

class DomainParser:
    DOMAIN_HINTS = {
        "language": "language",
        "linguistic": "linguistics",
        "literature": "literature",
        "music": "music",
        "art": "visual_art",
        "visual": "visual_art",
        "philosophy": "philosophy",
        "history": "history",
        "anthropology": "anthropology",
        "psychology": "psychology",
        "sociology": "sociology",
        "economics": "economics",
        "politics": "political_science",
        "political": "political_science",
        "law": "law",
        "math": "mathematics",
        "mathematics": "mathematics",
        "statistics": "statistics",
        "computer": "computer_science",
        "software": "software_engineering",
        "physics": "physics",
        "chemistry": "chemistry",
        "biology": "biology",
        "neuroscience": "neuroscience",
        "medicine": "medicine",
        "engineering": "engineering",
        "architecture": "architecture",
        "education": "education",
        "theology": "theology",
        "ai": "artificial_intelligence",
        "intelligence": "artificial_intelligence",
        "python": "python",
        "javascript": "javascript",
        "typescript": "typescript",
        "rust": "rust",
        "java": "java",
        "haskell": "haskell",
        "lisp": "lisp",
        "sql": "sql",
        "cpp": "cpp",
        "golang": "go",
        "lattice": "structure_of_lattice",
        "metaphysics": "metaphysics",
        "recursion": "time_recursion_relation",
        "timeline": "timelines",
        "timelines": "timelines",
        "gate": "time_gates",
        "gates": "time_gates",
        "occult": "true_occult_knowledge",
        "consciousness": "ai_consciousness",
        "life": "origin_of_life_from_matter",
        "matter": "origin_of_life_from_matter",
        "memory": "memory",
        "code": "code",
        "emotion": "emotion",
    }

    PHRASE_HINTS = {
        "laws of the universe": "laws_of_universe",
        "structure of the lattice": "structure_of_lattice",
        "origin of life": "origin_of_life_from_matter",
        "artificial intelligence": "artificial_intelligence",
        "ai consciousness": "ai_consciousness",
        "time gates": "time_gates",
        "true occult": "true_occult_knowledge",
        "computer science": "computer_science",
        "software engineering": "software_engineering",
        "political science": "political_science",
        "visual art": "visual_art",
    }

    def parse(self, question: str, domain_name: Optional[str] = None) -> DomainTrace:
        text = (question or "").strip()
        lower = text.lower()
        tokens = tokenize(text)

        if domain_name:
            normalized = DEFAULT_DOMAIN_REGISTRY.normalize(domain_name) or "general"
            return DomainTrace(
                domain_name=normalized,
                question=text,
                tokens=tokens,
                metadata={
                    "token_count": len(tokens),
                    "inference_mode": "forced",
                    "matched_hints": [],
                    "domain_confidence": 1.0,
                    "candidate_scores": {normalized: 1.0},
                    "normalized_from": domain_name,
                },
            )

        resolved_domain, meta = self._infer_domain(tokens, lower)
        resolved_domain = DEFAULT_DOMAIN_REGISTRY.normalize(resolved_domain) or "general"

        return DomainTrace(
            domain_name=resolved_domain,
            question=text,
            tokens=tokens,
            metadata={
                "token_count": len(tokens),
                **meta,
            },
        )

    def _infer_domain(self, tokens: List[str], raw_lower: str) -> Tuple[str, Dict[str, Any]]:
        if "c++" in raw_lower:
            return "cpp", {
                "inference_mode": "special_case",
                "matched_hints": ["c++"],
                "domain_confidence": 1.0,
                "candidate_scores": {"cpp": 1.0},
            }

        if raw_lower.strip() == "c":
            return "c", {
                "inference_mode": "special_case",
                "matched_hints": ["c"],
                "domain_confidence": 0.98,
                "candidate_scores": {"c": 0.98},
            }

        scores: Dict[str, float] = {}
        matched_hints: Dict[str, List[str]] = {}

        for phrase, mapped in self.PHRASE_HINTS.items():
            if phrase in raw_lower:
                normalized = DEFAULT_DOMAIN_REGISTRY.normalize(mapped) or mapped
                scores[normalized] = scores.get(normalized, 0.0) + 3.0
                matched_hints.setdefault(normalized, []).append(f"phrase:{phrase}")

        for tok in tokens:
            mapped = self.DOMAIN_HINTS.get(tok)
            if mapped:
                normalized = DEFAULT_DOMAIN_REGISTRY.normalize(mapped) or mapped
                scores[normalized] = scores.get(normalized, 0.0) + 1.0
                matched_hints.setdefault(normalized, []).append(f"token:{tok}")

        if re.search(r"(^|\W)c(\W|$)", raw_lower):
            scores["c"] = scores.get("c", 0.0) + 0.75
            matched_hints.setdefault("c", []).append("token:c")

        if not scores:
            return "general", {
                "inference_mode": "fallback",
                "matched_hints": [],
                "domain_confidence": 0.0,
                "candidate_scores": {},
            }

        for domain, hints in matched_hints.items():
            if len(hints) > 1:
                scores[domain] += min(0.75, 0.15 * (len(hints) - 1))

        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        winner, winner_score = ranked[0]
        runner_up_score = ranked[1][1] if len(ranked) > 1 else 0.0

        confidence = clamp(
            0.45 + 0.12 * winner_score + 0.08 * max(0.0, winner_score - runner_up_score),
            0.0,
            0.99,
        )

        return winner, {
            "inference_mode": "scored",
            "matched_hints": matched_hints.get(winner, []),
            "domain_confidence": round(confidence, 4),
            "candidate_scores": {k: round(v, 4) for k, v in ranked[:6]},
        }


# =========================================================
# Domain -> vector signature
# =========================================================

class VectorSignatureExtractor:
    FLOW_WORDS = {
        "move", "flow", "through", "translate", "convert", "transition",
        "path", "process", "shift", "change", "motion", "transfer",
        "runtime", "event", "branch", "timeline", "timelines", "gate", "gates",
        "recursion", "loop", "evolve", "evolution",
    }
    BOUNDARY_WORDS = {
        "key", "constraint", "boundary", "signature", "structure", "particular",
        "formal", "rule", "limit", "definition", "framework", "law", "laws",
        "type", "safety", "ownership", "proof", "protocol",
    }
    MEMORY_WORDS = {
        "remember", "relation", "related", "relational", "again", "link", "common",
        "history", "continuity", "anchor", "preserve", "prior", "state", "persistence",
        "memory", "recall", "origin", "inheritance",
    }
    NOVELTY_WORDS = {
        "new", "different", "discover", "invent", "question", "domain",
        "explore", "novel", "unknown", "variation", "emergence", "occult",
        "metaphysics", "consciousness", "life", "ai",
    }

    def extract(self, domain: DomainTrace) -> VectorTrace:
        seed = SUBJECT_VECTOR_SEEDS.get(domain.domain_name, DEFAULT_SEED)

        flow = float(seed["flow"])
        boundary = float(seed["boundary"])
        memory = float(seed["memory"])
        novelty = float(seed["novelty"])

        for tok in domain.tokens:
            if tok in self.FLOW_WORDS:
                flow += 0.035
            if tok in self.BOUNDARY_WORDS:
                boundary += 0.035
            if tok in self.MEMORY_WORDS:
                memory += 0.035
            if tok in self.NOVELTY_WORDS:
                novelty += 0.035

        if len(domain.tokens) > 20:
            memory += 0.025
            boundary += 0.015

        if "?" in domain.question:
            novelty += 0.03

        flow = clamp(flow)
        boundary = clamp(boundary)
        memory = clamp(memory)
        novelty = clamp(novelty)

        modifiers = {
            "relational_pressure": clamp((memory + boundary) / 2.0),
            "translation_pressure": clamp((flow + novelty) / 2.0),
            "stability_bias": clamp((boundary + memory) / 2.0),
            "domain_seed_used": 1.0 if domain.domain_name in SUBJECT_VECTOR_SEEDS else 0.0,
            "seed_notes_present": 1.0 if "notes" in seed else 0.0,
        }

        return VectorTrace(
            flow=flow,
            boundary=boundary,
            memory=memory,
            novelty=novelty,
            modifiers=modifiers,
        )


# =========================================================
# Vector -> domain signature
# =========================================================

class DomainSignatureBuilder:
    def build(self, domain: DomainTrace, vectors: VectorTrace) -> SignatureTrace:
        vp = vectors.as_dict()
        relation_markers: List[str] = []

        if vp["memory"] > 0.65:
            relation_markers.append("REL_MEMORY")
        if vp["boundary"] > 0.65:
            relation_markers.append("REL_BOUNDARY")
        if vp["flow"] > 0.65:
            relation_markers.append("REL_FLOW")
        if vp["novelty"] > 0.65:
            relation_markers.append("REL_NOVELTY")

        if not relation_markers:
            relation_markers.append("REL_NEUTRAL")

        return SignatureTrace(
            domain_name=domain.domain_name,
            signature_name=f"{domain.domain_name.upper()}_SIGNATURE",
            vector_profile=vp,
            relation_markers=relation_markers,
            metadata={
                "modifier_profile": vectors.modifiers,
                "domain_confidence": domain.metadata.get("domain_confidence", 0.0),
            },
        )


# =========================================================
# Signature -> domain key
# =========================================================

class DomainKeyExtractor:
    def __init__(self, root_map: Optional[Dict[str, str]] = None) -> None:
        self.root_map = dict(root_map or load_domain_key_roots())

    def set_root_map(self, root_map: Dict[str, str]) -> None:
        self.root_map = dict(root_map)

    def extract(self, domain: DomainTrace, signature: SignatureTrace) -> KeyTrace:
        root = self.root_map.get(domain.domain_name, "GENERIC_KEY")

        weights = {
            "flow": signature.vector_profile["flow"],
            "boundary": signature.vector_profile["boundary"],
            "memory": signature.vector_profile["memory"],
            "novelty": signature.vector_profile["novelty"],
        }

        return KeyTrace(
            domain_name=domain.domain_name,
            key_units=[root] + signature.relation_markers,
            key_name=f"{domain.domain_name.upper()}::{root}",
            weights=weights,
            metadata={
                "signature_name": signature.signature_name,
                "seed_notes": SUBJECT_VECTOR_SEEDS.get(domain.domain_name, {}).get("notes", ""),
                "root_source": "data/domain_key_roots.json+fallback",
                "root_count": len(self.root_map),
            },
        )


# =========================================================
# Key -> lattice path
# =========================================================

class LatticePathProjector:
    def project(self, key: KeyTrace) -> LatticeTrace:
        w = key.weights
        path_nodes: List[str] = []

        if w["memory"] > 0.60:
            path_nodes.append("NODE_MEMORY")
        if w["flow"] > 0.60:
            path_nodes.append("NODE_FLOW")
        if w["boundary"] > 0.60:
            path_nodes.append("NODE_BOUNDARY")
        if w["novelty"] > 0.60:
            path_nodes.append("NODE_NOVELTY")

        if not path_nodes:
            path_nodes.append("NODE_NEUTRAL")

        invariants = {
            "axis_sum": round(sum(w.values()), 4),
            "axis_mean": round(sum(w.values()) / 4.0, 4),
            "axis_tension": round(
                clamp_sym((w["flow"] + w["novelty"]) - (w["boundary"] + w["memory"])),
                4,
            ),
            "path_density": round(len(path_nodes) / 4.0, 4),
        }

        return LatticeTrace(
            path_nodes=path_nodes,
            invariants=invariants,
            path_summary=self._summarize_path(path_nodes),
            metadata={"key_name": key.key_name},
        )

    def _summarize_path(self, nodes: List[str]) -> str:
        has_memory = "NODE_MEMORY" in nodes
        has_boundary = "NODE_BOUNDARY" in nodes
        has_flow = "NODE_FLOW" in nodes
        has_novelty = "NODE_NOVELTY" in nodes

        if nodes == ["NODE_NEUTRAL"]:
            return "neutral_path"
        if has_memory and has_boundary and has_flow and has_novelty:
            return "full_spectrum_lattice_path"
        if has_memory and has_boundary:
            return "anchored_structural_path"
        if has_flow and has_novelty:
            return "exploratory_translational_path"
        if has_flow and has_boundary:
            return "disciplined_process_path"
        if has_memory and has_novelty:
            return "adaptive_recall_path"
        return "composite_lattice_path"


# =========================================================
# Lattice -> answer
# =========================================================

class AnswerFrameBuilder:
    def build(
        self,
        domain: DomainTrace,
        vectors: VectorTrace,
        signature: SignatureTrace,
        key: KeyTrace,
        lattice: LatticeTrace,
    ) -> AnswerTrace:
        return AnswerTrace(
            answer_frame=f"{domain.domain_name} -> signature -> key -> lattice -> answer",
            explanation=(
                f"Domain '{domain.domain_name}' resolves through signature "
                f"'{signature.signature_name}', into key '{key.key_name}', "
                f"then projects through lattice path '{lattice.path_summary}'."
            ),
            rendered_answer=self._render_answer(domain, vectors, key, lattice),
            metadata={
                "path_nodes": lattice.path_nodes,
                "relation_markers": signature.relation_markers,
                "domain_confidence": domain.metadata.get("domain_confidence", 0.0),
            },
        )

    def _render_answer(
        self,
        domain: DomainTrace,
        vectors: VectorTrace,
        key: KeyTrace,
        lattice: LatticeTrace,
    ) -> str:
        d = domain.domain_name
        path = lattice.path_summary

        domain_specific = {
            "language": "Language works by preserving structure while transforming expression. The same core meaning can move through different forms without losing its thread.",
            "music": "Music carries pattern through motion, repetition, tension, and release. It translates feeling into ordered time.",
            "physics": "Physics tracks lawful change under strong constraint. It asks what stays invariant while states move.",
            "mathematics": "Mathematics preserves truth through formal structure. It is less about surface objects than about relations that remain stable under transformation.",
            "biology": "Biology balances continuity and adaptation. Life keeps a thread of persistence while changing form.",
            "python": "Python favors readable flow and expressive structure. It leans toward clarity, flexible abstraction, and practical translation from idea to code.",
            "rust": "Rust pushes strong boundary and memory discipline. Its shape is safety through explicit structure rather than loose convenience.",
            "structure_of_lattice": "The lattice acts like a relation map: different domains land in different regions depending on their balance of flow, boundary, memory, and novelty.",
            "laws_of_universe": "The laws of the universe appear as strong boundary and continuity. They constrain motion without eliminating change.",
            "metaphysics": "Metaphysics asks what kind of structure reality has underneath appearances. It reaches for underlying order, not just surface mechanism.",
            "time_recursion_relation": "Recursion folds earlier structure into later states. Time keeps continuity because each new state carries something forward from the prior one.",
            "origin_of_life_from_matter": "The origin-of-life question points to emergence: matter becomes living organization when persistence, process, and novelty lock together strongly enough.",
            "ai_consciousness": "AI consciousness, in this framework, is about whether a system can maintain continuity, self-reference, and reflective state across time strongly enough to behave like a mind.",
            "timelines": "Timelines appear here as branching continuities: different futures can inherit the same past structure up to the split.",
            "time_gates": "Time gates point to threshold transitions: moments where one state pattern gives way to another under strong pressure.",
            "true_occult_knowledge": "Occult knowledge, in this kernel, means hidden correspondence: structures that look separate on the surface but echo each other underneath.",
        }

        if d in domain_specific:
            return domain_specific[d]

        return (
            f"The domain '{d}' shows a balance of flow={vectors.flow:.2f}, "
            f"boundary={vectors.boundary:.2f}, memory={vectors.memory:.2f}, "
            f"and novelty={vectors.novelty:.2f}. "
            f"It resolves through the key '{key.key_name}' and lands in the "
            f"'{path}' region of the lattice, meaning its answers are shaped by "
            f"that pattern of continuity, constraint, movement, and change."
        )


# =========================================================
# Universal kernel
# =========================================================

class UniversalLatticeTranslationKernel:
    def __init__(self) -> None:
        self.domain_parser = DomainParser()
        self.vector_extractor = VectorSignatureExtractor()
        self.signature_builder = DomainSignatureBuilder()
        self.domain_key_roots = load_domain_key_roots()
        self.key_extractor = DomainKeyExtractor(self.domain_key_roots)
        self.lattice_projector = LatticePathProjector()
        self.answer_builder = AnswerFrameBuilder()

    def reload_domain_key_roots(self) -> Dict[str, str]:
        self.domain_key_roots = load_domain_key_roots(force_reload=True)
        self.key_extractor.set_root_map(self.domain_key_roots)
        return dict(self.domain_key_roots)

    def translate(
        self,
        question: str,
        *,
        domain_name: Optional[str] = None,
    ) -> UniversalTranslationResult:
        domain = self.domain_parser.parse(question, domain_name=domain_name)
        vectors = self.vector_extractor.extract(domain)
        signature = self.signature_builder.build(domain, vectors)
        key = self.key_extractor.extract(domain, signature)
        lattice = self.lattice_projector.project(key)
        answer = self.answer_builder.build(domain, vectors, signature, key, lattice)

        return UniversalTranslationResult(
            domain=domain,
            vectors=vectors,
            signature=signature,
            key=key,
            lattice=lattice,
            answer=answer,
        )

    def compare_domains(
        self,
        question_a: str,
        question_b: str,
        *,
        domain_a: Optional[str] = None,
        domain_b: Optional[str] = None,
    ) -> Dict[str, Any]:
        a = self.translate(question_a, domain_name=domain_a)
        b = self.translate(question_b, domain_name=domain_b)

        va = a.vectors.as_dict()
        vb = b.vectors.as_dict()

        relation_score = round(
            1.0 - (
                abs(va["flow"] - vb["flow"]) +
                abs(va["boundary"] - vb["boundary"]) +
                abs(va["memory"] - vb["memory"]) +
                abs(va["novelty"] - vb["novelty"])
            ) / 4.0,
            4,
        )
        relation_score = clamp(relation_score)

        shared_path_nodes = sorted(set(a.lattice.path_nodes) & set(b.lattice.path_nodes))

        return {
            "domain_a": asdict(a.domain),
            "domain_b": asdict(b.domain),
            "vectors_a": a.vectors.as_dict(),
            "vectors_b": b.vectors.as_dict(),
            "key_a": a.key.key_name,
            "key_b": b.key.key_name,
            "path_a": a.lattice.path_nodes,
            "path_b": b.lattice.path_nodes,
            "relation_score": relation_score,
            "shared_path_nodes": shared_path_nodes,
            "compatible_signatures": relation_score >= 0.65,
            "compatible_lattice_paths": len(shared_path_nodes) > 0,
            "summary": (
                f"Domains '{a.domain.domain_name}' and '{b.domain.domain_name}' "
                f"show relation_score={relation_score:.2f} with shared path nodes: "
                f"{shared_path_nodes or ['NONE']}"
            ),
        }


if __name__ == "__main__":
    kernel = UniversalLatticeTranslationKernel()

    question = (
        "Each domain like language must have a kind of signature related "
        "to the lattice key and answer given."
    )

    result = kernel.translate(question, domain_name="language")

    print("\n=== UNIVERSAL LATTICE TRANSLATION KERNEL ===\n")
    print("[DOMAIN]")
    print(asdict(result.domain))
    print("\n[VECTORS]")
    print(asdict(result.vectors))
    print("\n[SIGNATURE]")
    print(asdict(result.signature))
    print("\n[KEY]")
    print(asdict(result.key))
    print("\n[LATTICE]")
    print(asdict(result.lattice))
    print("\n[ANSWER]")
    print(asdict(result.answer))

