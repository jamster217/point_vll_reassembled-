from __future__ import annotations

from typing import Any, Dict, List

from lattice.lattice_node_map import LatticeNodeMap


def infer_lattice_path(prompt: str) -> Dict[str, Any]:
    text = str(prompt or "").lower()
    lattice = LatticeNodeMap()

    start = "44"
    goal = None

    if any(x in text for x in ["dad", "father", "lineage", "ancestral", "grief", "goodbye"]):
        goal = "5218"
    elif any(x in text for x in ["crystal", "octagon", "528", "harmonic"]):
        goal = "528"
    elif any(x in text for x in ["mirror", "threshold", "paradox", "switch"]):
        goal = "161"

    if not goal:
        return {
            "active": False,
            "start": start,
            "goal": None,
            "path": [],
            "summary": "",
        }

    path = lattice.shortest_path(start, goal)
    packet: List[Dict[str, Any]] = [
        {
            "node_id": n.node_id,
            "label": n.label,
            "band": n.band,
            "weight": n.weight,
        }
        for n in path
    ]

    return {
        "active": bool(packet),
        "start": start,
        "goal": goal,
        "path": packet,
        "summary": " -> ".join(f"{n['node_id']}({n['label']})" for n in packet),
    }

