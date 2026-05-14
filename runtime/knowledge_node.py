from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())


def compute_source_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256((text or "").encode("utf-8")).hexdigest()


@dataclass
class KnowledgeNode:
    node_id: str
    node_type: str  # echo | concept | motif | event | relationship
    created_at: str
    updated_at: str
    source_hash: str
    gloss: str

    shape_signature: Dict[str, float] = field(default_factory=lambda: {
        "flow": 0.0,
        "boundary": 0.0,
        "memory": 0.0,
        "novelty": 0.0,
        "confidence": 0.0,
    })

    motifs: List[str] = field(default_factory=list)
    symbols: List[str] = field(default_factory=list)
    hotspot: str = ""
    links: List[str] = field(default_factory=list)
    weight: float = 0.0
    status: str = "active"

    @classmethod
    def new(
        cls,
        node_type: str,
        gloss: str,
        source_text: str,
        shape_signature: Dict[str, float] | None = None,
        motifs: List[str] | None = None,
        symbols: List[str] | None = None,
        hotspot: str = "",
        links: List[str] | None = None,
        weight: float = 0.0,
        status: str = "active",
    ) -> "KnowledgeNode":
        ts = _now_iso()
        shape = shape_signature or {}

        return cls(
            node_id=str(uuid.uuid4()),
            node_type=str(node_type),
            created_at=ts,
            updated_at=ts,
            source_hash=compute_source_hash(source_text),
            gloss=str(gloss),
            shape_signature={
                "flow": float(shape.get("flow", 0.0)),
                "boundary": float(shape.get("boundary", 0.0)),
                "memory": float(shape.get("memory", 0.0)),
                "novelty": float(shape.get("novelty", 0.0)),
                "confidence": float(shape.get("confidence", 0.0)),
            },
            motifs=motifs or [],
            symbols=symbols or [],
            hotspot=hotspot or "",
            links=links or [],
            weight=float(weight),
            status=status,
        )

    def touch(self) -> None:
        self.updated_at = _now_iso()

    def add_link(self, other_node_id: str) -> None:
        if other_node_id not in self.links:
            self.links.append(other_node_id)
            self.touch()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source_hash": self.source_hash,
            "gloss": self.gloss,
            "shape_signature": dict(self.shape_signature),
            "motifs": list(self.motifs),
            "symbols": list(self.symbols),
            "hotspot": self.hotspot,
            "links": list(self.links),
            "weight": float(self.weight),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeNode":
        return cls(
            node_id=data["node_id"],
            node_type=data["node_type"],
            created_at=data["created_at"],
            updated_at=data.get("updated_at", data["created_at"]),
            source_hash=data["source_hash"],
            gloss=data.get("gloss", ""),
            shape_signature=data.get("shape_signature", {
                "flow": 0.0,
                "boundary": 0.0,
                "memory": 0.0,
                "novelty": 0.0,
                "confidence": 0.0,
            }),
            motifs=data.get("motifs", []),
            symbols=data.get("symbols", []),
            hotspot=data.get("hotspot", ""),
            links=data.get("links", []),
            weight=float(data.get("weight", 0.0)),
            status=data.get("status", "active"),
        )

