from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
VL_PATH = ROOT / "spiral_language" / "symbolic_core_v1.vl"

def _read_vl():
    if not VL_PATH.exists():
        return {"vl_file_found": False, "vl_sha256": None}
    text = VL_PATH.read_text(encoding="utf-8", errors="ignore")
    return {
        "vl_file_found": True,
        "vl_sha256": hashlib.sha256(text.encode()).hexdigest()[:16],
        "declared_fields": ["shape_vector", "phenome_surface"]
    }

def apply_symbolic_core_v1_adapter(data: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(data or {})
    spine = data.setdefault("spine", {})
    vl_info = _read_vl()
    
    adapter_output = {
        "source": "v63_symbolic_core_v1_adapter",
        "execution_mode": "vl_file_backed_adapter_not_full_vm",
        "phenome_live": False,
        "vl_file_found": vl_info["vl_file_found"],
        "vl_sha256": vl_info["vl_sha256"],
        "phenome_surface": "phenome::adapter symbols=savariel|leveon|membrane flow=0.72 boundary=0.61",
        "truth_status": "honest adapter active"
    }
    
    spine["symbolic_core_v1"] = adapter_output
    data["symbolic_core_v1"] = adapter_output
    data["symbolic_bridge_source"] = "v63_symbolic_core_v1_adapter"
    data["phenome_surface"] = adapter_output["phenome_surface"]
    return data

__all__ = ["apply_symbolic_core_v1_adapter"]

