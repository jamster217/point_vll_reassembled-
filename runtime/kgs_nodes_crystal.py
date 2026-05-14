from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


CRYSTAL_LIBRARY_PATH = Path("kernel/crystal_library.json")
STATE_PATH = Path("var/kgs_nodes_crystal_state.json")


class KGSNodesCrystal:
    """
    Runtime implementation of:

    NODES KGSNodesCrystal

    FLOW INIT
        MEM crystal_nodes
    END

    BOUND GET_NODE
        TAKE id
        RETURN crystal_nodes[id]
    END

    BOUND LIST
        RETURN crystal_nodes.ALL
    END
    """

    def __init__(self):
        self.crystal_nodes: Dict[str, Dict[str, Any]] = {}
        self.flow_init()

    def _read_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_json(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def flow_init(self) -> Dict[str, Dict[str, Any]]:
        state = self._read_json(STATE_PATH)

        if isinstance(state.get("crystal_nodes"), dict) and state["crystal_nodes"]:
            self.crystal_nodes = state["crystal_nodes"]
            return self.crystal_nodes

        library = self._read_json(CRYSTAL_LIBRARY_PATH)

        nodes: Dict[str, Dict[str, Any]] = {}
        index = 1

        for key, value in library.items():
            if str(key).startswith("_") or key == "crystal_blocks":
                continue

            node_id = str(index)

            nodes[node_id] = {
                "id": node_id,
                "name": key,
                "kind": "crystal_anchor",
                "value": value,
                "status": "active",
                "source": "kernel/crystal_library.json",
                "created_at": time.time(),
            }

            index += 1

        self.crystal_nodes = nodes
        self.save()
        return self.crystal_nodes

    def get_node(self, node_id: str | int) -> Optional[Dict[str, Any]]:
        key = str(node_id)

        if key in self.crystal_nodes:
            return self.crystal_nodes[key]

        # Allow lookup by crystal name too.
        for node in self.crystal_nodes.values():
            if node.get("name") == key:
                return node

        return None

    def list_nodes(self) -> List[Dict[str, Any]]:
        return list(self.crystal_nodes.values())

    def upsert_node(self, node_id: str | int, node: Dict[str, Any]) -> Dict[str, Any]:
        key = str(node_id)
        node = dict(node)
        node.setdefault("id", key)
        node.setdefault("status", "active")
        node.setdefault("updated_at", time.time())

        self.crystal_nodes[key] = node
        self.save()
        return node

    def save(self) -> None:
        payload = {
            "kind": "KGSNodesCrystal",
            "updated_at": time.time(),
            "crystal_nodes": self.crystal_nodes,
            "law": "FLOW INIT creates MEM crystal_nodes; GET_NODE returns one; LIST returns all.",
        }
        self._write_json(STATE_PATH, payload)


_ENGINE: Optional[KGSNodesCrystal] = None


def engine() -> KGSNodesCrystal:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = KGSNodesCrystal()
    return _ENGINE


def flow_init() -> Dict[str, Dict[str, Any]]:
    return engine().flow_init()


def get_node(node_id: str | int) -> Optional[Dict[str, Any]]:
    return engine().get_node(node_id)


def list_nodes() -> List[Dict[str, Any]]:
    return engine().list_nodes()


if __name__ == "__main__":
    e = engine()
    print("KGSNodesCrystal online")
    print("nodes:", len(e.list_nodes()))
    print(json.dumps(e.list_nodes()[:5], indent=2, ensure_ascii=False))

