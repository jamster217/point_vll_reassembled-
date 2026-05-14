from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _safe_lower(s: str) -> str:
    return (s or "").strip().lower()


def extract_semantic_anchors(text: str, min_len: int = 4) -> List[str]:
    import re
    text = _safe_lower(text)
    toks = re.findall(r"[a-z][a-z']+", text)
    STOP = {
        "the","and","that","this","with","from","into","over","under","about","does","what","when","where","why","how","should","should","your","you","are","is","was","were","be","been","being","to","of","in","on","at","as","it","its","for","or","but","not","we","our","they","their","i","me","my","mine","a","an","often"
    }
    KEEP_SHORT = {
        "dad","mom","mike","john","love","grief","pain","hurt","fear","hope","time","key","ui","ai"
    }
    anchors = [t for t in toks if ((len(t) >= min_len) or (t in KEEP_SHORT)) and t not in STOP]
    seen = set()
    out = []
    for a in anchors:
        if a not in seen:
            seen.add(a)
            out.append(a)
    return out


@dataclass
class GoldStandard:
    timestamp: str
    chosen_output: str
    anchors: List[str]
    directness_score: float
    meta: Dict


class ResonanceBuffer:
    def __init__(
        self,
        path: str = "runtime/gold_standards.jsonl",
        min_directness: float = 0.40,
        overlap_required: int = 3,
        boost: float = 0.07,
        boost_cap: float = 0.10,
        max_items: int = 400,
    ) -> None:
        self.path = path
        self.min_directness = float(min_directness)
        self.overlap_required = int(overlap_required)
        self.boost = float(boost)
        self.boost_cap = float(boost_cap)
        self.max_items = int(max_items)

    def add_if_gold(self, chosen_output: str, directness_score: float, meta: Optional[Dict] = None) -> bool:
        if float(directness_score) < self.min_directness:
            return False

        anchors = extract_semantic_anchors(chosen_output)
        gs = GoldStandard(
            timestamp=_now_iso(),
            chosen_output=chosen_output,
            anchors=anchors,
            directness_score=float(directness_score),
            meta=meta or {},
        )
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
                # DEDUPE: skip if last stored item matches same chosen_output
        if os.path.exists(self.path):
            try:
                with open(self.path, "rb") as rf:
                    rf.seek(0, os.SEEK_END)
                    size = rf.tell()
                    rf.seek(max(0, size - 2048), os.SEEK_SET)
                    tail = rf.read().decode("utf-8", "ignore").strip().splitlines()
                    if tail:
                        last = json.loads(tail[-1])
                        if last.get("chosen_output") == gs.chosen_output:
                            return False
            except Exception:
                pass

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(gs.__dict__, ensure_ascii=False) + "\n")

        self._truncate_if_needed()
        return True

    def score_boost(self, candidate_text: str, prompt_anchors: Optional[List[str]] = None) -> Tuple[float, Dict]:
        cand_anchors = set(extract_semantic_anchors(candidate_text))
        p_anchors = set(prompt_anchors or [])

        best_overlap = 0
        best_ts = None

        for gs in self._iter_gold():
            overlap = len(cand_anchors.intersection(set(gs.anchors)))
            if overlap > best_overlap:
                best_overlap = overlap
                best_ts = gs.timestamp

        granted = (best_overlap >= self.overlap_required)
        prompt_overlap = len(cand_anchors.intersection(p_anchors)) if p_anchors else 0

        raw_boost = self.boost if granted else 0.0
        final_boost = min(raw_boost, self.boost_cap)

        debug = {
            "gold_best_overlap": best_overlap,
            "gold_best_timestamp": best_ts,
            "prompt_overlap": prompt_overlap,
            "granted": granted,
            "boost": final_boost,
        }
        return final_boost, debug

    def _iter_gold(self) -> List[GoldStandard]:
        if not os.path.exists(self.path):
            return []
        out: List[GoldStandard] = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                out.append(
                    GoldStandard(
                        timestamp=obj.get("timestamp", ""),
                        chosen_output=obj.get("chosen_output", ""),
                        anchors=obj.get("anchors", []) or [],
                        directness_score=float(obj.get("directness_score", 0.0)),
                        meta=obj.get("meta", {}) or {},
                    )
                )
        return out

    def _truncate_if_needed(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) <= self.max_items:
            return
        lines = lines[-self.max_items :]
        with open(self.path, "w", encoding="utf-8") as f:
            f.writelines(lines)

