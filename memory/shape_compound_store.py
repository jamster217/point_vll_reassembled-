from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List
from pathlib import Path
import json
import time
import hashlib


STORE_PATH = Path("assets/memory/shape_compounds.json")


@dataclass
class ShapeCompound:
    compound_id: str
    source_kind: str
    english_gloss: str
    synthesis_summary: str
    logic_chain: List[str]
    flow: float
    boundary: float
    memory: float
    novelty: float
    meaning_tags: List[str]
    symbolic_trace: List[str]
    confidence: float
    revision_count: int
    created_at: float
    last_accessed: float


def _load_store() -> Dict:
    if not STORE_PATH.exists():
        return {"compounds": []}
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def _save_store(data: Dict) -> None:
    STORE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def make_compound(
    *,
    source_kind: str,
    english_gloss: str,
    synthesis_summary: str,
    logic_chain: List[str],
    meaning_tags: List[str],
    symbolic_trace: List[str],
    flow: float = 0.5,
    boundary: float = 0.5,
    memory: float = 0.5,
    novelty: float = 0.5,
    confidence: float = 0.75,
) -> Dict:
    now = time.time()
    raw = f"{source_kind}|{english_gloss}|{synthesis_summary}|{now}"
    compound_id = "cmp_" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]

    compound = ShapeCompound(
        compound_id=compound_id,
        source_kind=source_kind,
        english_gloss=english_gloss,
        synthesis_summary=synthesis_summary,
        logic_chain=logic_chain,
        flow=float(flow),
        boundary=float(boundary),
        memory=float(memory),
        novelty=float(novelty),
        meaning_tags=meaning_tags,
        symbolic_trace=symbolic_trace,
        confidence=float(confidence),
        revision_count=0,
        created_at=now,
        last_accessed=now,
    )
    return asdict(compound)


def append_compound(compound: Dict) -> Dict:
    store = _load_store()
    store.setdefault("compounds", []).append(compound)
    _save_store(store)
    return compound

