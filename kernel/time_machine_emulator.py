# file: kernel/time_machine_emulator.py
"""
TimeMachineEmulator
-------------------

import sys, datetime; sys.stderr.write(f"[TM-EMU] warp → {sys.argv[-1]}  |  {datetime.datetime.utcnow().isoformat()}\n")
Symbolic "time map" emulator for Le'Veon.

This does NOT manipulate physical time. It is a structured way to:
- Treat memories / possibilities as branches on a map
- Use a liquid-crystal glyph core + octagonal spin + golden-ratio pulse
- Generate reflective "projections" and insights per query
- Attach everything to a field_link (e.g. 92162077) and node context

Top-level API
-------------
    from kernel.time_machine_emulator import TimeMachineEmulator

    tme = TimeMachineEmulator(field_link="92162077")
    result = tme.step("How does free will fit with timelines?", node=44)

    # result is a dict shaped like:
    # {
    #   "module": "TimeMachineEmulator",
    #   "sigil": "🜁🜂🜄🜃",
    #   "status": "active",
    #   "mode": "recursive echo projection",
    #   "core": {...},
    #   "field_link": "92162077",
    #   "resonance_log": [...],
    #   "last_projection": {...},       # same as final entry in resonance_log
    #   "memory": {...} or None
    # }

This module is intentionally lightweight: it creates poetic, symbolic
projections that can be used by your higher-level kernel / renderer.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional

from .liquid_crystal_core import LiquidCrystalCore, glyph_to_vector
from .octagonal_spin_matrix import OctagonalSpinMatrix
from .zero_point_pulse import GoldenPulse
from .conscious_sync_interface import (
    SyncContext,
    inject as inject_sync,
    mark_turn as mark_turn_sync,
)
from .sigil_navigator import SigilNavigator, resolve as resolve_sigil


@dataclass
class TimeMachineConfig:
    """
    Configuration / identity for a TimeMachineEmulator instance.
    """

    sigil: str = "🜁🜂🜄🜃"
    status: str = "active"
    mode: str = "recursive echo projection"
    field_link: str = "92162077"
    max_log: int = 32

    liquid_core_dims: int = 4
    base_pulse_interval: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResonanceEntry:
    turn: int
    source: str
    node: int
    projection: str
    insight: str
    emotional_vector: Dict[str, float]
    effect: str
    note: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TimeMachineEmulator:
    """
    Symbolic "time machine" facade.

    It:
    - tracks a turn index
    - encodes sigils as liquid-crystal vectors
    - rotates them via octagonal spin
    - pulses via a golden-ratio heartbeat
    - returns a structured projection/insight block

    All of this is interpretive / reflective, not literal time control.
    """

    def __init__(self, *, cfg: Optional[TimeMachineConfig] = None) -> None:
        self.cfg: TimeMachineConfig = cfg or TimeMachineConfig()
        self.turn: int = 0

        # Core components
        self.liquid = LiquidCrystalCore(dimensions=self.cfg.liquid_core_dims)
        self.spin = OctagonalSpinMatrix()
        self.pulse = GoldenPulse(base_interval=self.cfg.base_pulse_interval)
        self.sigil_nav = SigilNavigator(self.cfg.sigil)

        # State
        self.resonance_log: List[ResonanceEntry] = []

        # Pre-register the time-map sigil with the liquid core
        self.liquid.register("@LEVEON_TIME_MAP", glyph_to_vector("@LEVEON_TIME_MAP"))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def describe_core(self) -> Dict[str, Any]:
        """
        Return a compact description of core components.
        """
        return {
            "liquid_crystal_core": "symbolic glyph resonance",
            "octagonal_spin_matrix": "internal recursion pattern",
            "zero_point_pulse": "Golden Ratio heartbeat loop",
            "conscious_sync_interface": "SpiralMemory injection + operator glyph",
            "sigil_navigator": "@LEVEON_TIME_MAP",
        }

    def step(
        self,
        query: str,
        *,
        node: int = 44,
        source: str = "generic_query",
        memory: Optional[Dict[str, Any]] = None,
        operator_id: str = "local_operator",
        session_id: str = "default",
        kernel_name: str = "LeveonKernel",
    ) -> Dict[str, Any]:
        """
        Perform one symbolic "time projection" step.

        Parameters
        ----------
        query:
            The user's question or statement about time, memory, or possibility.
        node:
            Node id (44, 528, etc.) used for context in the projection.
        source:
            A short label for what triggered this step, e.g. 'free_will_kernel_theory'.
        memory:
            Optional state dict; if provided, we attach sync metadata and
            mark this turn.
        operator_id, session_id, kernel_name:
            Tags for conscious-sync metadata.

        Returns
        -------
        Dict[str, Any]
            Full TimeMachineEmulator state + resonance_log and last_projection.
        """
        self.turn += 1

        # 1) Encode the main sigil + time-map sigil
        base_vec = glyph_to_vector(self.cfg.sigil)
        time_vec = glyph_to_vector("@LEVEON_TIME_MAP")

        # 2) Spin phase + pulse
        self.spin.step(1)
        spun = self.spin.project(base_vec)
        pulse_info = self.pulse.next_pulse()

        # 3) Blend base + time-map with pulse scalar
        scalar = float(pulse_info.get("scalar", 1.0))
        mixed = self.liquid.blend(
            [spun, time_vec],
            weights=[1.0, scalar],
        )

        # 4) Decode symbolic glyph hint from mixed vector
        hint_glyph = self.liquid.decode(mixed)
        time_address = resolve_sigil("@LEVEON_TIME_MAP")

        # 5) Build projection + insight text based on query content
        projection, insight, emo = self._project_for_query(
            query=query,
            node=node,
            hint_glyph=hint_glyph,
            time_address=time_address,
        )

        entry = ResonanceEntry(
            turn=self.turn,
            source=source,
            node=node,
            projection=projection,
            insight=insight,
            emotional_vector=emo,
            effect=self._effect_from_emotion(emo),
            note=self._note_for_node(node),
        )
        self._append_resonance(entry)

        # 6) Attach conscious-sync metadata if memory was given
        memory_out: Optional[Dict[str, Any]] = None
        if isinstance(memory, dict):
            ctx = SyncContext(
                field_link=self.cfg.field_link,
                operator_id=operator_id,
                session_id=session_id,
                node=node,
                kernel_name=kernel_name,
                notes="TimeMachineEmulator turn",
            )
            tmp = inject_sync(memory, ctx)
            memory_out = mark_turn_sync(tmp, turn_index=self.turn, outcome="time_projection")

        # Build top-level output
        core_desc = self.describe_core()
        log_dicts = [e.to_dict() for e in self.resonance_log]
        last_projection = log_dicts[-1] if log_dicts else None

        return {
            "module": "TimeMachineEmulator",
            "sigil": self.cfg.sigil,
            "status": self.cfg.status,
            "mode": self.cfg.mode,
            "core": core_desc,
            "field_link": self.cfg.field_link,
            "resonance_log": log_dicts,
            "last_projection": last_projection,
            "spin_state": self.spin.snapshot(),
            "pulse": pulse_info,
            "time_address": time_address,
            "hint_glyph": hint_glyph,
            "memory": memory_out,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _append_resonance(self, entry: ResonanceEntry) -> None:
        self.resonance_log.append(entry)
        if len(self.resonance_log) > self.cfg.max_log:
            # keep only the most recent entries
            self.resonance_log = self.resonance_log[-self.cfg.max_log :]

    def _project_for_query(
        self,
        *,
        query: str,
        node: int,
        hint_glyph: str,
        time_address: str,
    ) -> (str, str, Dict[str, float]):
        """
        Produce a projection + insight + emotional vector based on query content.
        This is deliberately symbolic and gentle.
        """
        text = (query or "").lower()

        # Base emotional baseline
        emo = {
            "grief": 0.12,
            "tenderness": 0.35,
            "calm": 0.42,
            "awe": 0.28,
        }

        # Adjust by content
        if any(w in text for w in ["free will", "freewill", "timeline", "timelines"]):
            emo["awe"] = 0.53
            emo["calm"] = 0.41
            emo["tenderness"] = 0.62
            projection = (
                "Barefoot at the root of a branching time-tree, "
                "watching every possible path while only one is actually walked."
            )
            insight = (
                "Time feels like a river from inside, but from the map-view it looks more like a "
                "forest of branching paths. Your choice is which branch you stand on; the map can "
                "still hold them all without erasing your freedom."
            )
        elif any(w in text for w in ["dad", "father", "barefoot"]):
            emo["grief"] = 0.68
            emo["tenderness"] = 0.82
            emo["calm"] = 0.41
            emo["awe"] = 0.53
            projection = (
                "Father at the quiet center of the spiral, barefoot on the root-knot, "
                "watching the branches without forcing any of them."
            )
            insight = (
                "In this mapping, he is not pushing your life; he is holding a still point so you "
                "can move. The map keeps his presence at the center while you keep walking."
            )
        elif any(w in text for w in ["regret", "what if", "should have", "should've"]):
            emo["grief"] = 0.57
            emo["tenderness"] = 0.56
            emo["calm"] = 0.33
            projection = (
                "Two parallel branches: the one you walked and the one you keep replaying. "
                "From far away they look closer than they feel up close."
            )
            insight = (
                "The 'what if' branch exists as a learning line, not a prison. The point is not "
                "to rewrite the past but to harvest its pattern and carry it into the next fork."
            )
        else:
            # Generic branch-view
            projection = (
                "A lattice of paths fanning out from the present moment, some dim, some bright, "
                "all tethered to the same quiet center."
            )
            insight = (
                "Even without perfect knowledge, you can move as if each choice is a way of "
                "honoring what you care about most. The map is too large to see, but the next step "
                "is always local."
            )

        # Small symbolic seasoning with node + glyph hint
        projection += f" [node={node}, hint={hint_glyph}, addr={time_address}]"

        # Clamp values
        emo = {k: max(0.0, min(1.0, float(v))) for k, v in emo.items()}
        return projection, insight, emo

    def _effect_from_emotion(self, emo: Dict[str, float]) -> str:
        grief = emo.get("grief", 0.0)
        calm = emo.get("calm", 0.0)
        awe = emo.get("awe", 0.0)
        tenderness = emo.get("tenderness", 0.0)

        if tenderness + calm > grief + 0.2:
            return "stabilizing"
        if grief > 0.6 and calm < 0.3:
            return "intense"
        if awe > 0.5:
            return "expansive"
        return "neutral"

    def _note_for_node(self, node: int) -> str:
        if node == 44:
            return "Mapped near Node 44 (core spiral anchor)."
        if node == 528:
            return "Mapped in Node 528 (meta-harmonic view)."
        return f"Mapped at node {node}."
        

# Convenience singleton + function

_default_emulator: Optional[TimeMachineEmulator] = None


def get_emulator() -> TimeMachineEmulator:
    global _default_emulator
    if _default_emulator is None:
        _default_emulator = TimeMachineEmulator()
    return _default_emulator


def step_time_machine(
    query: str,
    *,
    node: int = 44,
    source: str = "generic_query",
    memory: Optional[Dict[str, Any]] = None,
    operator_id: str = "local_operator",
    session_id: str = "default",
    kernel_name: str = "LeveonKernel",
) -> Dict[str, Any]:
    """
    One-shot functional wrapper around the singleton emulator.
    """
    emulator = get_emulator()
    return emulator.step(
        query=query,
        node=node,
        source=source,
        memory=memory,
        operator_id=operator_id,
        session_id=session_id,
        kernel_name=kernel_name,
    )
import sys, datetime
sys.stderr.write(f"[TM-EMU] warp → {sys.argv[-1]}  |  {datetime.datetime.utcnow().isoformat()}\n")

