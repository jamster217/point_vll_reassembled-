import ast
import json
from pathlib import Path
from typing import Any, Dict, List


CRYSTAL_LIBRARY_SIGIL = {
    "id": "CRYSTAL_LIBRARY_SIGIL",
    "rev": "phi-1.618",
    "note": "folder watcher anchor"
}


class TraceAdapter:
    def __init__(
        self,
        trace_path: str = "replication_trace_4200.py",
        cache_path: str = "runtime/trace_adapter_index.json"
    ):
        base = Path(__file__).resolve().parents[1]
        self.trace_path = Path(trace_path) if Path(trace_path).is_absolute() else (base / trace_path)
        self.cache_path = Path(cache_path) if Path(cache_path).is_absolute() else (base / cache_path)
        self.trace_rows: List[Dict[str, Any]] = []
        self.index: List[Dict[str, Any]] = []

    def load(self) -> None:
        self.trace_rows = self._load_trace_file(self.trace_path)
        self.index = [self._index_row(i, row) for i, row in enumerate(self.trace_rows)]

    def save_index(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "anchor": CRYSTAL_LIBRARY_SIGIL,
            "trace_path": str(self.trace_path),
            "rows": self.index,
        }
        self.cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load_index(self) -> bool:
        if not self.cache_path.exists():
            return False
        try:
            raw = json.loads(self.cache_path.read_text(encoding="utf-8"))
            self.index = raw.get("rows", [])
            return True
        except Exception:
            return False

    def refresh(self) -> None:
        self.load()
        self.save_index()

    def lookup(self, prompt_shape: Dict[str, Any], top_k: int = 3) -> Dict[str, Any]:
        if not self.index:
            return {
                "anchor": CRYSTAL_LIBRARY_SIGIL,
                "matches": [],
                "route_bias": None,
                "motifs": [],
                "trace_confidence": 0.0
            }

        scored = []
        for row in self.index:
            score = self._shape_similarity(prompt_shape, row.get("shape_signature", {}))
            if score > 0:
                scored.append((score, row))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]

        matches = []
        motif_counts: Dict[str, int] = {}
        route_counts: Dict[str, float] = {}

        for score, row in top:
            matches.append({
                "turn_index": row.get("turn_index"),
                "shape_signature": row.get("shape_signature"),
                "route": row.get("route"),
                "coherence_field": row.get("coherence_field"),
                "motifs": row.get("motifs", []),
                "commit": row.get("commit"),
                "final_english_output": row.get("final_english_output"),
                "match_score": round(score, 3)
            })

            route_key = f"{row.get('route', {}).get('domain', 'unknown')}:{row.get('route', {}).get('spoke', 'unknown')}"
            route_counts[route_key] = route_counts.get(route_key, 0.0) + score

            for m in row.get("motifs", []):
                motif_counts[m] = motif_counts.get(m, 0) + 1

        best_route = None
        if route_counts:
            best_route_key = max(route_counts, key=route_counts.get)
            domain, spoke = best_route_key.split(":", 1)
            best_route = {
                "domain": domain,
                "spoke": spoke,
                "weight": round(route_counts[best_route_key], 3)
            }

        motifs = sorted(motif_counts, key=lambda k: (-motif_counts[k], k))[:8]
        confidence = round(top[0][0], 3) if top else 0.0

        return {
            "anchor": CRYSTAL_LIBRARY_SIGIL,
            "matches": matches,
            "route_bias": best_route,
            "motifs": motifs,
            "trace_confidence": confidence
        }

    def _load_trace_file(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []

        text = path.read_text(encoding="utf-8", errors="ignore").strip()

        try:
            raw = json.loads(text)
            return self._normalize_trace_payload(raw)
        except Exception:
            pass

        rows = []
        ok = True
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                ok = False
                break
        if ok and rows:
            return self._normalize_trace_payload(rows)

        try:
            module = ast.parse(text)
            for node in module.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.lower() in {
                            "trace", "trace_rows", "replication_trace", "turns"
                        }:
                            value = ast.literal_eval(node.value)
                            return self._normalize_trace_payload(value)
        except Exception:
            pass

        return []

    def _normalize_trace_payload(self, raw: Any) -> List[Dict[str, Any]]:
        if isinstance(raw, dict):
            if "turns" in raw and isinstance(raw["turns"], list):
                return [x for x in raw["turns"] if isinstance(x, dict)]
            if "rows" in raw and isinstance(raw["rows"], list):
                return [x for x in raw["rows"] if isinstance(x, dict)]
            return [raw]
        if isinstance(raw, list):
            return [x for x in raw if isinstance(x, dict)]
        return []

    def _index_row(self, i: int, row: Dict[str, Any]) -> Dict[str, Any]:
        shape = row.get("shape_signature", {}) or row.get("shape", {}) or {}
        derived = row.get("derived_metrics", {}) or {}
        coherence_field = row.get("coherence_field", {}) or {}
        kernel_state = row.get("kernel_state", {}) or {}
        commit = row.get("commit", {}) or {}

        motifs = row.get("motifs_and_knowledge", [])
        if isinstance(motifs, dict):
            motifs = list(motifs.keys())
        if not isinstance(motifs, list):
            motifs = []

        route = {
            "domain": row.get("route_domain") or row.get("domain") or kernel_state.get("domain") or "unknown",
            "spoke": row.get("route_spoke") or row.get("spoke") or kernel_state.get("spoke") or "unknown",
        }

        return {
            "turn_index": row.get("turn") if row.get("turn") is not None else i,
            "shape_signature": {
                "intent": shape.get("intent"),
                "tone": shape.get("tone"),
                "anchor": shape.get("anchor"),
                "direction": shape.get("direction"),
                "pressure": shape.get("pressure"),
                "domain": route["domain"],
                "spoke": route["spoke"],
            },
            "derived_metrics": derived,
            "coherence_field": coherence_field,
            "route": route,
            "motifs": [str(m) for m in motifs[:12]],
            "commit": commit,
            "threshold_rdn": row.get("threshold_rdn"),
            "irreversibility": row.get("irreversibility"),
            "final_english_output": row.get("final_english_output"),
        }

    def _shape_similarity(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        if not a or not b:
            return 0.0

        score = 0.0
        total = 0.0

        def add(cat_a, cat_b, weight):
            nonlocal score, total
            total += weight
            if cat_a and cat_b and str(cat_a).lower() == str(cat_b).lower():
                score += weight

        add(a.get("intent"), b.get("intent"), 0.25)
        add(a.get("tone"), b.get("tone"), 0.20)
        add(a.get("anchor"), b.get("anchor"), 0.20)
        add(a.get("direction"), b.get("direction"), 0.10)
        add(a.get("pressure"), b.get("pressure"), 0.10)
        add(a.get("domain"), b.get("domain"), 0.10)
        add(a.get("spoke"), b.get("spoke"), 0.05)

        if total == 0:
            return 0.0
        return score / total


if __name__ == "__main__":
    adapter = TraceAdapter(
        trace_path="replication_trace_4200.py",
        cache_path="runtime/trace_adapter_index.json"
    )
    adapter.refresh()

    prompt_shape = {
        "intent": "relationship",
        "tone": "grief",
        "anchor": "loss-bond",
        "direction": "inward",
        "pressure": "low",
        "domain": "relation",
        "spoke": "bridge_mapper"
    }

    result = adapter.lookup(prompt_shape, top_k=3)
    print(json.dumps(result, indent=2))

