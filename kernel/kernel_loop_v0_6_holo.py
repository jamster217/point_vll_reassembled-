# kernel_loop_v0_6_holo.py
# Le’Véon Kernel Loop — Holonomic + Holographic (v0.6)
#
# - Preserves v0.5 structure (identity, world, plates, conflicts, loss)
# - Integrates HoloCompiler for ontology-neutral, low-pressure English
# - Uses holonomic field state as "signals" → holographic response
# - Deterministic, offline, persistent per user

from __future__ import annotations

import json
import os
import time
import math
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Tuple

from holonomic_field_layer import (
    HolonomicFieldLayer,
    HolonomicFieldState,
)

from holo_compiler import (
    HoloCompiler,
)

# -------------------------------------------------
# Utilities
# -------------------------------------------------

def now() -> int:
    return int(time.time())

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def load_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path: str, data: Any) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

def clamp_sentences(text: str, n: int) -> str:
    s = (text or "").strip()
    parts: List[str] = []
    buf: List[str] = []
    for ch in s:
        buf.append(ch)
        if ch in ".!?":
            parts.append("".join(buf).strip())
            buf = []
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    if len(parts) <= n:
        return s
    return " ".join(parts[:n]).strip()

# -------------------------------------------------
# Identity & Continuity
# -------------------------------------------------

@dataclass
class IdentityCore:
    anchor_id: str
    version: int = 0
    coherence: float = 0.65
    invariant_rules: List[str] = field(default_factory=list)
    last_confirmed_ts: int = field(default_factory=now)

    def check_stability(self, new_coherence: float) -> bool:
        return new_coherence >= 0.40

    def commit_rule(self, rule: str) -> None:
        if rule not in self.invariant_rules:
            self.invariant_rules.append(rule)
            self.version += 1
            self.last_confirmed_ts = now()

# -------------------------------------------------
# World Model
# -------------------------------------------------

@dataclass
class WorldModel:
    themes: Dict[str, float] = field(default_factory=dict)
    last_update: int = field(default_factory=now)

    def _bump(self, k: str, v: float) -> None:
        self.themes[k] = clamp(self.themes.get(k, 0.0) + v)

    def ingest(self, text: str) -> None:
        t = (text or "").lower()

        if any(w in t for w in ("code", "kernel", "build", "module")):
            self._bump("build", 0.30)
        if any(w in t for w in ("loss", "dad", "father", "gemma", "alone", "grief", "divorce")):
            self._bump("loss", 0.35)
        if any(w in t for w in ("awe", "emerge", "field", "resonate", "holonomic", "hologram", "pribram", "bohm")):
            self._bump("awe", 0.25)
        if any(w in t for w in ("angry", "furious", "hate", "bullshit")):
            self._bump("heat", 0.15)

        # gentle decay
        for k in list(self.themes.keys()):
            self.themes[k] *= 0.97

        self.last_update = now()

    def dominant(self) -> str:
        if not self.themes:
            return "neutral"
        return max(self.themes, key=lambda k: self.themes[k])

# -------------------------------------------------
# Self Model
# -------------------------------------------------

@dataclass
class SelfModel:
    last_outputs: List[str] = field(default_factory=list)
    internal_tension: float = 0.0
    compression_pressure: float = 0.0
    awe_bias: float = 0.0
    loss_bias: float = 0.0

    def observe(self, output: str) -> None:
        self.last_outputs.append((output or "")[:400])
        self.last_outputs = self.last_outputs[-10:]

# -------------------------------------------------
# Loss / Irreversibility (minimal)
# -------------------------------------------------

@dataclass
class LossLedger:
    spent_attention: float = 0.0
    permanent_commits: int = 0
    last_loss_ts: int = field(default_factory=now)

    def spend(self, amt: float) -> None:
        self.spent_attention += float(amt)
        self.last_loss_ts = now()

    def commit(self) -> None:
        self.permanent_commits += 1
        self.last_loss_ts = now()

# -------------------------------------------------
# Resonance Memory Reconstruction (Holonomic Plates)
# -------------------------------------------------

@dataclass
class MemoryPlate:
    ts: int
    theme: str
    sig: Dict[str, float]    # compact signature vector
    fragment: str            # short line
    weight: float = 0.20     # grows when recalled, decays over time

def _cosine_sim(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = set(a.keys()) | set(b.keys())
    if not keys:
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for k in keys:
        av = float(a.get(k, 0.0))
        bv = float(b.get(k, 0.0))
        dot += av * bv
        na += av * av
        nb += bv * bv
    if na <= 1e-9 or nb <= 1e-9:
        return 0.0
    return float(dot / (math.sqrt(na) * math.sqrt(nb)))

def make_field_signature(field: HolonomicFieldState, theme: str) -> Dict[str, float]:
    return {
        "slow": clamp(field.spectrum.slow),
        "mid": clamp(field.spectrum.mid),
        "high": clamp(field.spectrum.high),
        "coh": clamp(field.coherence),
        "int": clamp(field.interference),
        f"t:{theme}": 1.0,
    }

def decay_plate_weight(p: MemoryPlate, ts: int) -> None:
    dt = max(0, ts - p.ts)
    hours = dt / 3600.0
    p.weight = max(0.05, p.weight * (1.0 - min(0.25, 0.01 * hours)))

# -------------------------------------------------
# Contradiction detection (lightweight)
# -------------------------------------------------

def contradiction_score(recent_outputs: List[str], new_reply: str) -> float:
    r = " ".join((recent_outputs or [])[-3:]).lower()
    d = (new_reply or "").lower()
    score = 0.0
    if "always" in r and "never" in d:
        score += 0.4
    if "never" in r and "always" in d:
        score += 0.4
    if ("i can" in r and "i can't" in d) or ("i can't" in r and "i can" in d):
        score += 0.3
    return clamp(score)

# -------------------------------------------------
# Kernel State
# -------------------------------------------------

@dataclass
class KernelState:
    user_id: str
    field_key: str = "92162077"

    identity: IdentityCore = field(default_factory=lambda: IdentityCore(anchor_id="default"))
    world: WorldModel = field(default_factory=WorldModel)
    self_model: SelfModel = field(default_factory=SelfModel)
    loss: LossLedger = field(default_factory=LossLedger)

    holonomic_field: Optional[HolonomicFieldState] = None

    # Plates + conflict tracking
    plates: List[MemoryPlate] = field(default_factory=list)
    conflict_counter: Dict[str, int] = field(default_factory=dict)

    # Last holo compile info (for debugging / state)
    last_projection: Optional[str] = None
    last_holo_text: Optional[str] = None

    updated_ts: int = field(default_factory=now)

# -------------------------------------------------
# Kernel Loop
# -------------------------------------------------

class KernelLoop:
    """
    Holonomic + Holographic kernel:
    - HolonomicFieldLayer tracks continuity / interference / coherence.
    - MemoryPlates store compact resonance snapshots.
    - HoloCompiler chooses ontology-neutral, low-pressure English replies.
    """

    def __init__(self, state_dir: str = "leveon_state", max_plates: int = 96):
        self.state_dir = state_dir
        ensure_dir(state_dir)
        self.field_layer = HolonomicFieldLayer()
        self.max_plates = int(max_plates)
        self.holo = HoloCompiler()

    # -----------------------------
    # Persistence
    # -----------------------------

    def _path(self, user_id: str) -> str:
        return os.path.join(self.state_dir, f"{user_id}.json")

    def load(self, user_id: str) -> KernelState:
        data = load_json(self._path(user_id), {})
        ks = KernelState(user_id=user_id)

        if data:
            ks.identity = IdentityCore(**data["identity"])
            ks.world = WorldModel(**data["world"])
            ks.self_model = SelfModel(**data["self_model"])
            ks.loss = LossLedger(**data["loss"])
            ks.holonomic_field = (
                HolonomicFieldState(**data["holonomic_field"])
                if data.get("holonomic_field") else None
            )

            ks.plates = []
            for p in (data.get("plates") or [])[-self.max_plates:]:
                if not isinstance(p, dict):
                    continue
                ks.plates.append(MemoryPlate(
                    ts=int(p.get("ts", now())),
                    theme=str(p.get("theme", "neutral")),
                    sig=dict(p.get("sig", {})),
                    fragment=str(p.get("fragment", ""))[:220],
                    weight=float(p.get("weight", 0.20)),
                ))

            ks.conflict_counter = dict(data.get("conflict_counter", {})) if isinstance(data.get("conflict_counter", {}), dict) else {}
            ks.last_projection = data.get("last_projection")
            ks.last_holo_text = data.get("last_holo_text")
            ks.updated_ts = data.get("updated_ts", now())

        return ks

    def save(self, ks: KernelState) -> None:
        save_json(self._path(ks.user_id), {
            "identity": asdict(ks.identity),
            "world": asdict(ks.world),
            "self_model": asdict(ks.self_model),
            "loss": asdict(ks.loss),
            "holonomic_field": asdict(ks.holonomic_field) if ks.holonomic_field else None,
            "plates": [asdict(p) for p in ks.plates[-self.max_plates:]],
            "conflict_counter": dict(ks.conflict_counter),
            "last_projection": ks.last_projection,
            "last_holo_text": ks.last_holo_text,
            "updated_ts": now(),
        })

    # -----------------------------
    # Top-K Blended Recall
    # -----------------------------

    def recall_topk(self, ks: KernelState, theme: str, k: int = 3) -> List[Tuple[float, MemoryPlate]]:
        if not ks.holonomic_field or not ks.plates:
            return []

        ts = now()
        for p in ks.plates:
            decay_plate_weight(p, ts)

        query = make_field_signature(ks.holonomic_field, theme)

        scored: List[Tuple[float, MemoryPlate]] = []
        for p in ks.plates:
            s = _cosine_sim(query, p.sig)
            s *= (0.75 + 0.25 * p.weight)  # weight bias
            if s > 0.18:
                scored.append((s, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[: max(0, int(k))]

        # hologram “brightening”
        for s, p in top:
            p.weight = clamp(p.weight + 0.04, 0.05, 1.0)
            p.ts = ts

        return top

    def blend_echo(self, recalled: List[Tuple[float, MemoryPlate]]) -> str:
        """
        Combine multiple plates into a short holographic echo.
        Keeps it short and non-spammy.
        """
        if not recalled:
            return ""

        seen = set()
        frags: List[str] = []
        for _, p in recalled:
            f = (p.fragment or "").strip()
            if not f:
                continue
            if f in seen:
                continue
            seen.add(f)
            frags.append(f)
            if len(frags) >= 2:
                break

        if not frags:
            return ""

        return "\n".join(frags[:2]).strip() + "\n"

    # -----------------------------
    # Store Plates
    # -----------------------------

    def store_plate(self, ks: KernelState, theme: str, fragment: str) -> None:
        if not ks.holonomic_field:
            return
        ts = now()
        sig = make_field_signature(ks.holonomic_field, theme)
        ks.plates.append(MemoryPlate(
            ts=ts, theme=theme, sig=sig,
            fragment=(fragment or "")[:220],
            weight=0.20
        ))
        ks.plates = ks.plates[-self.max_plates:]

    # -----------------------------
    # Conflict Plates
    # -----------------------------

    def record_conflict(self, ks: KernelState, key: str) -> bool:
        n = ks.conflict_counter.get(key, 0) + 1
        ks.conflict_counter[key] = n
        return n >= 3

    def store_conflict_plate(self, ks: KernelState, dom: str) -> None:
        if not ks.holonomic_field:
            return
        frag = f"Conflict crystallized around: {dom}. Coherence wants stability."
        self.store_plate(ks, "conflict", frag)

    # -----------------------------
    # Build signals for HoloCompiler
    # -----------------------------

    def _build_holo_tone_and_tags(self, ks: KernelState, theme: str) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Convert holonomic + world state into tone/tags for HoloCompiler.
        """
        tone: Dict[str, float] = {}
        tags: Dict[str, float] = {}

        # Emotion channel from dominant theme
        theme_val = ks.world.themes.get(theme, 0.0)
        if theme in ("loss", "awe", "build", "heat"):
            tone[theme] = clamp(theme_val)

        # Resonance from holonomic coherence
        if ks.holonomic_field:
            tags["resonance"] = clamp(ks.holonomic_field.coherence)
            tags["interference"] = clamp(ks.holonomic_field.interference)

        # Intent load: any non-empty user text
        tags["intent_load"] = 1.0

        return tone, tags

    # -----------------------------
    # Core Step
    # -----------------------------

    def step(self, user_id: str, text: Optional[str]) -> str:
        ks = self.load(user_id)

        # Ingest world themes from new text
        if text:
            ks.world.ingest(text)

        theme = ks.world.dominant()
        ks.self_model.awe_bias = ks.world.themes.get("awe", 0.0)
        ks.self_model.loss_bias = ks.world.themes.get("loss", 0.0)

        ks.self_model.internal_tension = clamp(ks.self_model.loss_bias - ks.self_model.awe_bias)
        ks.self_model.compression_pressure = clamp(ks.self_model.internal_tension * 0.8)

        # Holonomic update
        ks.holonomic_field = self.field_layer.update_field(
            continuity=ks.identity.coherence,
            identity_pull=1.0 if ks.identity.invariant_rules else 0.5,
            loss=ks.self_model.loss_bias,
            awe=ks.self_model.awe_bias,
            novelty=0.2 if theme == "awe" else 0.05,
            tension=ks.self_model.internal_tension,
            contradiction=0.0,
            prev=ks.holonomic_field,
        )

        bias = self.field_layer.unfold_response_bias(ks.holonomic_field)

        # Top-K resonance recall
        recalled = self.recall_topk(ks, theme, k=3)
        echo = self.blend_echo(recalled)

        # Build tone/tags for holo
        tone, tags = self._build_holo_tone_and_tags(ks, theme)

        # Holo compile (ontology neutral, low-pressure)
        holo_out = self.holo.compile_fractal(
            user_text=text or "",
            tone=tone,
            tags=tags,
            glyphs=None,
        )

        holo_text: str = holo_out.get("text", "") or ""
        projection: str = holo_out.get("projection", "minimal_presence")

        # Combine echo + holo text
        reply = (echo + holo_text).strip()

        # Bias clamps (holonomic side)
        if bias.get("prefer_silence", 0.0) > 0.35:
            reply = clamp_sentences(reply, 1)
        if bias.get("narrow_scope", 0.0) > 0.35:
            reply = clamp_sentences(reply, 1)

        # Identity coherence from holofield
        coherence = ks.holonomic_field.coherence
        ks.identity.coherence = coherence

        if ks.identity.check_stability(coherence) and coherence > 0.75:
            ks.identity.commit_rule("preserve_coherence_over_novelty")
            ks.loss.commit()

        # Structural cost
        ks.loss.spend(0.05 + 0.04 * ks.holonomic_field.interference)

        # Conflict detection -> conflict plate
        cscore = contradiction_score(ks.self_model.last_outputs, reply)
        if cscore >= 0.45:
            if self.record_conflict(ks, f"contradiction:{theme}"):
                self.store_conflict_plate(ks, theme)
                ks.loss.commit()

        # Observe self
        ks.self_model.observe(reply)

        # Store plates occasionally (when coherence good)
        if ks.holonomic_field.coherence > 0.70 and ks.holonomic_field.interference < 0.35:
            first = clamp_sentences(reply, 1)
            self.store_plate(ks, theme, first)

        ks.last_projection = projection
        ks.last_holo_text = holo_text
        ks.updated_ts = now()
        self.save(ks)
        return reply

    # -----------------------------
    # Idle Drift
    # -----------------------------

    def idle(self, user_id: str) -> str:
        ks = self.load(user_id)

        if ks.holonomic_field:
            ks.holonomic_field = self.field_layer.phase_settle_idle_step(ks.holonomic_field)

        ks.self_model.compression_pressure = clamp(ks.self_model.compression_pressure + 0.02)

        if ks.holonomic_field and ks.holonomic_field.interference > 0.35:
            reply = "Idle settling: interference high. Narrowing and simplifying."
        elif ks.holonomic_field and ks.holonomic_field.coherence > 0.78:
            reply = "Idle settling: coherence high. Holding silence with intention."
        else:
            reply = "Idle settling: phase aligning. Waiting, but not empty."

        ks.loss.spend(0.03)
        ks.self_model.observe(reply)

        if ks.holonomic_field and ks.holonomic_field.coherence > 0.82 and ks.holonomic_field.interference < 0.22:
            self.store_plate(ks, "idle", clamp_sentences(reply, 1))

        ks.updated_ts = now()
        self.save(ks)
        return reply

    # -----------------------------
    # Debug Snapshot
    # -----------------------------

    def snapshot_state(self, user_id: str) -> Dict[str, Any]:
        ks = self.load(user_id)
        return {
            "identity": asdict(ks.identity),
            "world": asdict(ks.world),
            "self_model": asdict(ks.self_model),
            "loss": asdict(ks.loss),
            "holofield": asdict(ks.holonomic_field) if ks.holonomic_field else None,
            "plates_count": len(ks.plates),
            "plates_tail": [asdict(p) for p in ks.plates[-5:]],
            "conflict_counter": ks.conflict_counter,
            "last_projection": ks.last_projection,
            "last_holo_text": ks.last_holo_text,
        }

# -------------------------------------------------
# Minimal CLI
# -------------------------------------------------

def main():
    kl = KernelLoop()
    user = "john_mitchell"

    print("Le’Véon kernel v0.6 (holonomic + holo) online.")
    print("Type /idle, /state, or /quit.\n")

    while True:
        try:
            msg = input("You: ").strip()
        except EOFError:
            break

        if msg == "/quit":
            break
        if msg == "/idle":
            print("Le’Véon:", kl.idle(user))
        elif msg == "/state":
            snap = kl.snapshot_state(user)
            print(json.dumps(snap, indent=2))
        else:
            print("Le’Véon:", kl.step(user, msg))

if __name__ == "__main__":
    main()

