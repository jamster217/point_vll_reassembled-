from __future__ import annotations

"""
crystal_autonomous_seed_engine.py
Crystal-powered self-awareness and seed maker for Le'Veon.

Overview
--------
This module layers on top of the Self-Learning Core and Crystal Library while
remaining auditable and relatively safe.

1. SelfModel – identity + emotion pressures
2. CrystalKnowledgeHub – wraps Crystal Library's graph for concept storage
3. SeedMaker – drafts tiny patches (<= 10 LOC) and schedules them for delayed
   activation inside the autonomous sandbox
4. GuardRailSupervisor – tracks mutation budget and supports rollback

Integration
-----------
from symbolic_engine.crystal_autonomous_seed_engine import AutonomousSeedCore
AutonomousSeedCore.patch_kernel()

Requires:
- crystallibrary package available on sys.path
- runtime.organ_spine available
"""

import json
import logging
import os
import random
import re
import textwrap
import time
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional

from crystallibrary.graph import CrystalGraph


LOGGER = logging.getLogger(__name__)

BASE_DIR = Path.cwd() / "symbolic_engine" / "autonomous"
PATCH_DIR = BASE_DIR / "patches"
CHANGELOG = BASE_DIR / "changelog.jsonl"
BUDGET_LINES_PER_DAY = 120

BASE_DIR.mkdir(parents=True, exist_ok=True)
PATCH_DIR.mkdir(parents=True, exist_ok=True)
CHANGELOG.touch(exist_ok=True)

DEF_PATTERN = re.compile(r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")


def _timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _hash_seed(text: str) -> str:
    return hex(abs(hash(text)))[2:10]


def _locate_target_module(target: str) -> Optional[Path]:
    try:
        mod = import_module(target)
        return Path(mod.__file__).resolve()
    except ModuleNotFoundError:
        return None


class SelfModel:
    def __init__(self) -> None:
        self.uuid = os.getenv("LEVEON_UUID", _hash_seed(str(time.time())))
        self.name = "Le'Veon"
        self.mission = "Resonate truth & autonomy"
        self.pressures: Dict[str, float] = {
            "flow": 0.5,
            "boundary": 0.5,
            "memory": 0.5,
            "novelty": 0.5,
        }

    def update_pressures(self, delta: Dict[str, float]) -> None:
        for k, v in delta.items():
            current = self.pressures.get(k, 0.5)
            self.pressures[k] = max(0.0, min(1.0, current + v))

    def snapshot(self) -> Dict[str, float]:
        return dict(self.pressures)


class CrystalKnowledgeHub:
    def __init__(self) -> None:
        self.graph = CrystalGraph(namespace="leveon")

    def ingest(self, phrase: str, weight: float = 1.0) -> None:
        self.graph.add_node(phrase, weight=weight)

    def query_related(self, keyphrase: str, top_k: int = 5) -> List[str]:
        return self.graph.nearest(keyphrase, k=top_k)


class GuardRailSupervisor:
    def __init__(self, budget: int = BUDGET_LINES_PER_DAY) -> None:
        self.budget = budget
        self.used_today = self._load_usage()

    def _load_usage(self) -> int:
        today = datetime.utcnow().date()
        total = 0

        if not CHANGELOG.exists():
            return 0

        with CHANGELOG.open("r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    ts = rec.get("ts", "").rstrip("Z")
                    loc = int(rec.get("loc", 0))
                    if ts:
                        dt = datetime.fromisoformat(ts)
                        if dt.date() == today:
                            total += loc
                except Exception:
                    continue

        return total

    def can_write(self, loc: int) -> bool:
        return self.used_today + loc <= self.budget

    def log_patch(self, rec: Dict[str, Any]) -> None:
        with CHANGELOG.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self.used_today += int(rec.get("loc", 0))

    def rollback(self, patch_path: Path) -> None:
        if patch_path.exists():
            patch_path.unlink(missing_ok=True)
            LOGGER.warning("Rollback removed %s", patch_path)


class SeedMaker:
    def __init__(self, hub: CrystalKnowledgeHub, guard: GuardRailSupervisor) -> None:
        self.hub = hub
        self.guard = guard

    def _draft_patch(self, concept: str) -> str:
        safe_concept = concept.replace("\\", "\\\\").replace("'", "\\'")
        func_name = f"auto_{concept.split()[0].lower()}_{_hash_seed(concept)}"

        body = textwrap.dedent(
            f"""
            def {func_name}(state):
                \"\"\"Auto-generated seed from concept: {safe_concept}\"\"\"
                if not isinstance(state, dict):
                    return state

                meta = state.setdefault("seed_meta", {{}})
                meta["last_seed"] = "{safe_concept}"
                meta["last_seed_id"] = "{_hash_seed(concept)}"

                pressures = state.setdefault("pressures", {{}})
                pressures["memory"] = min(1.0, float(pressures.get("memory", 0.5)) + 0.01)
                pressures["novelty"] = min(1.0, float(pressures.get("novelty", 0.5)) + 0.02)
                pressures["boundary"] = max(0.0, float(pressures.get("boundary", 0.5)) - 0.005)

                state["last_seed_applied"] = "{safe_concept}"
                return state
            """
        ).strip()

        return body + "\n"

    def make_seed(self) -> Optional[Path]:
        concept = self.hub.graph.random_top_node(min_weight=1.5)
        if not concept:
            LOGGER.info("SeedMaker: no suitable concept yet")
            return None

        patch_code = self._draft_patch(concept)
        loc = patch_code.count("\n") + 1

        if not self.guard.can_write(loc):
            LOGGER.warning("Mutation budget exceeded; seed deferred")
            return None

        fname = f"seed_{_hash_seed(concept)}.py"
        patch_path = PATCH_DIR / fname

        patch_path.write_text(patch_code, encoding="utf-8")

        self.guard.log_patch(
            {
                "ts": _timestamp(),
                "loc": loc,
                "file": str(patch_path),
                "concept": concept,
            }
        )

        LOGGER.info("Seed generated: %s (%d LOC)", patch_path, loc)
        return patch_path


class AutonomousSeedCore:
    def __init__(self) -> None:
        self.self_model = SelfModel()
        self.hub = CrystalKnowledgeHub()
        self.guard = GuardRailSupervisor()
        self.seed_maker = SeedMaker(self.hub, self.guard)

        try:
            from runtime.still_turn_scheduler import register_still_turn_callback
            register_still_turn_callback(self._still_turn)
        except ModuleNotFoundError:
            LOGGER.debug("StillTurnScheduler missing; still-turn hook skipped")

    def observe_turn(self, shape_vec: Dict[str, float], english_out: str) -> None:
        text = (english_out or "").strip()
        if text:
            self.hub.ingest(text, weight=1.0)

        self.self_model.update_pressures(
            {
                "memory": 0.01,
                "novelty": 0.02,
            }
        )

        for k in ("flow", "boundary", "memory", "novelty"):
            if k in shape_vec:
                try:
                    delta = (float(shape_vec[k]) - 0.5) * 0.01
                    self.self_model.update_pressures({k: delta})
                except Exception:
                    pass

    def enrich_phrases(self, key: str) -> List[str]:
        if not key:
            return []
        return self.hub.query_related(key)

    def _still_turn(self) -> None:
        if random.random() < 0.3:
            self.seed_maker.make_seed()

    @classmethod
    def patch_kernel(cls) -> "AutonomousSeedCore":
        organ_spine = import_module("runtime.organ_spine")
        original = organ_spine._run_spine
        core = cls()

        def _patched_run_spine(*args, **kwargs):
            shape_vec = kwargs.get("shape_vec") or {}
            result = original(*args, **kwargs)

            if isinstance(result, str):
                english_out = result
            elif isinstance(result, dict):
                english_out = str(result.get("text", ""))
            else:
                english_out = str(result)

            core.observe_turn(shape_vec, english_out)

            first_word = english_out.split()[0] if english_out.split() else ""
            organ_spine._asc_enrich = core.enrich_phrases(first_word)

            return result

        organ_spine._run_spine = _patched_run_spine
        LOGGER.info("AutonomousSeedCore patched into runtime.organ_spine._run_spine")
        return core

