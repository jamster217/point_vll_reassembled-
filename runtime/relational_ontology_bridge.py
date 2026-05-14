from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_PATH = ROOT / "data" / "ontology" / "family_relational_physics.json"


def load_ontology(path: str | None = None) -> Dict[str, Any]:
    p = Path(path) if path else ONTOLOGY_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def get_distilled_shape(name: str, ontology: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ont = ontology or load_ontology()
    key = str(name or "").strip().lower()
    return dict((ont.get("distilled_shapes") or {}).get(key) or {})


def render_combined_shape(names: List[str], ontology: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ont = ontology or load_ontology()
    shapes = []
    primitives = []

    for name in names:
        shape = get_distilled_shape(name, ont)
        if not shape:
            continue

        shapes.append({
            "name": name,
            "essence": shape.get("essence"),
            "english": shape.get("english"),
            "relation": shape.get("relation"),
        })

        for k, v in shape.items():
            if v == 1:
                primitives.append(k)
            elif k == "relation":
                primitives.append(str(v))

    primitives = list(dict.fromkeys(primitives))

    final_shape = ont.get("whole_system_english", "")
    if set(names) != {"father", "mother", "home", "field"}:
        final_shape = " ".join(
            str(s.get("english", "")).strip().rstrip(".") + "."
            for s in shapes
            if s.get("english")
        ).strip()

    return {
        "ontology": "family_relational_physics",
        "inputs": names,
        "primitive_atoms": primitives,
        "shapes": shapes,
        "compressed_shape": ont.get("compressed_shape"),
        "one_line_physics": ont.get("one_line_physics"),
        "shape_packet": {
            "final_shape": final_shape,
            "source": "relational_ontology_bridge",
            "mode": "primitive_semantics_to_english"
        }
    }


if __name__ == "__main__":
    packet = render_combined_shape(["father", "mother", "home", "field"])
    print(json.dumps(packet, indent=2, ensure_ascii=False))

