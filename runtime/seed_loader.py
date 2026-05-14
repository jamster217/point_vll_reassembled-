from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Tuple


LOGGER = logging.getLogger(__name__)


def load_seed_pack(path: str | Path) -> List[Dict[str, Any]]:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Seed pack not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        seeds = json.load(f)

    required = {
        "seed_id",
        "label",
        "node_role",
        "activation_turn",
        "base_weight",
        "confidence",
        "archived_hash",
    }

    validated: List[Dict[str, Any]] = []
    for s in seeds:
        missing = required - set(s.keys())
        if missing:
            raise ValueError(f"Seed missing required fields: {missing}")
        validated.append(s)

    return validated


def discover_seed_patch_files(patch_dir: str | Path) -> List[Path]:
    patch_dir = Path(patch_dir)
    if not patch_dir.exists():
        return []
    return sorted(patch_dir.glob("seed_*.py"))


def load_seed_module(path: str | Path) -> ModuleType:
    path = Path(path)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load seed module from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_seed_functions(module: ModuleType):
    funcs = []
    for name in dir(module):
        if name.startswith("auto_"):
            obj = getattr(module, name)
            if callable(obj):
                funcs.append((name, obj))
    return funcs


def apply_seed_patches(
    state: Dict[str, Any],
    patch_dir: str | Path = "symbolic_engine/autonomous/patches",
    applied_log: str | Path | None = "symbolic_engine/autonomous/applied_seeds.jsonl",
) -> Tuple[Dict[str, Any], List[str]]:
    state = dict(state)
    applied: List[str] = []

    patch_files = discover_seed_patch_files(patch_dir)

    for patch_file in patch_files:
        try:
            module = load_seed_module(patch_file)
            funcs = get_seed_functions(module)

            for func_name, func in funcs:
                state = func(state)
                applied.append(f"{patch_file.name}:{func_name}")

        except Exception as exc:
            LOGGER.exception("Failed applying seed patch %s: %s", patch_file, exc)

    if applied_log:
        log_path = Path(applied_log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps({"applied": applied}) + "\n")

    return state, applied

