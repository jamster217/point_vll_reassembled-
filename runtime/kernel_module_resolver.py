#!/usr/bin/env python3
"""
Kernel module resolver.
Finds kernels by import path first, then by filename stem.
"""

import sys
import importlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SKIP_PARTS = {
    ".git", "__pycache__", ".venv", "venv", "env",
    "site-packages", ".mypy_cache", ".pytest_cache"
}


def _safe_python_files():
    for path in ROOT.rglob("*.py"):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        yield path


def import_first(label, import_candidates=None, file_stems=None):
    import_candidates = import_candidates or []
    file_stems = file_stems or []

    last_error = None

    for module_name in import_candidates:
        try:
            mod = importlib.import_module(module_name)
            return {
                "label": label,
                "status": "active",
                "method": "import",
                "module": module_name,
                "path": getattr(mod, "__file__", None),
            }
        except Exception as e:
            last_error = str(e)

    for stem in file_stems:
        for path in _safe_python_files():
            if path.stem == stem:
                try:
                    unique_name = "leveon_dynamic_" + "_".join(path.relative_to(ROOT).with_suffix("").parts)
                    spec = importlib.util.spec_from_file_location(unique_name, path)
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[unique_name] = mod
                    spec.loader.exec_module(mod)
                    return {
                        "label": label,
                        "status": "active",
                        "method": "file",
                        "module": unique_name,
                        "path": str(path),
                    }
                except Exception as e:
                    last_error = f"{path}: {e}"

    return {
        "label": label,
        "status": "unavailable",
        "method": None,
        "module": None,
        "path": None,
        "error": last_error or "not found",
    }

