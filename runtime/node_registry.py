from __future__ import annotations
from typing import Any, Dict, Optional

from .node_44_preset import enter_node_44
from .node_45_preset import enter_node_45
from .node_50_preset import enter_node_50
from .node_528_preset import enter_node_528


NODE_MAP = {
    44: enter_node_44,
    45: enter_node_45,
    50: enter_node_50,
    528: enter_node_528,
}


def activate_node(runtime: Any, node_id: int, override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    fn = NODE_MAP.get(node_id)
    if fn is None:
        raise ValueError(f"Unknown node {node_id}")
    return fn(runtime, override=override)

