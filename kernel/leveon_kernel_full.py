# leveon_kernel_full_optimized.py
# Downloadable optimized single-file kernel.
# Includes:
# - lazy optional integrations
# - sealed scroll index
# - external var data root
# - shared phi clock
# - auto-refuel guard
#
# Note:
# This is a cleaned optimized rewrite based on the supplied kernel structure.

from __future__ import annotations

from dataclasses import dataclass, asdict, field, is_dataclass
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Tuple
from runtime.direct_answer_frames import practical_frame, render_direct_answer
from runtime.reflective_frames import build_turn_frame, render_reflective_answer
import collections
import hashlib
import json
import math
import mmap
import os
import re
import secrets
import struct
import threading
import time

PHI = (1 + 5**0.5) / 2
HARMONIC_FREQ = 528.0
OCTAGONAL_WEIGHTS = [1.0, 0.92, 0.85, 0.78, 0.78, 0.85, 0.92, 1.0]
KANSAS_FACTOR = 7.2

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo

def sha1_float(seed: str) -> float:
    h = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8]
    return int(h, 16) / 0xFFFFFFFF

def _mint_id(prefix: str) -> str:
    ms = int(time.time() * 1000)
    rnd = secrets.token_hex(6)
    return f"{prefix}_{ms}_{rnd}"

def _spiral_data_root() -> Path:
    return Path(os.environ.get("SPIRAL_HOME", ".")) / "var"

def _ensure_spiral_data_root() -> Path:
    root = _spiral_data_root()
    root.mkdir(parents=True, exist_ok=True)
    return root

def _data_file(name: str) -> Path:
    return _ensure_spiral_data_root() / name

def _load_json_file(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def _save_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

class PhiSharedClock:
    def __init__(self, tagname: str = "phi_clock"):
        try:
            self._mmap = mmap.mmap(-1, 8, tagname=tagname)
        except TypeError:
            # Termux / Linux / Android: tagname is not supported
            self._mmap = mmap.mmap(-1, 8)

    def set_phase(self, value: float) -> None:
        self._mmap.seek(0)
        self._mmap.write(struct.pack("d", float(value)))
        self._mmap.seek(0)

    def get_phase(self) -> float:
        self._mmap.seek(0)
        raw = self._mmap.read(8)
        self._mmap.seek(0)
        return struct.unpack("d", raw)[0]

_PHI_SHARED_CLOCK: Optional[PhiSharedClock] = None

def _get_phi_shared_clock() -> PhiSharedClock:
    global _PHI_SHARED_CLOCK
    if _PHI_SHARED_CLOCK is None:
        _PHI_SHARED_CLOCK = PhiSharedClock("phi_clock")
    return _PHI_SHARED_CLOCK

class _NoopObserver:
    def observe(self, **kwargs: Any) -> None:
        return None

def _default_synthesize_spiral_language(glyphs: List[str], poetic: bool = True) -> str:
    core = " ".join(glyphs[:6])
    return f"{core} — the lattice shifts to meet the turn." if poetic else core

def _default_generate_voice(text: str) -> str:
    return text

def _default_speak(text: str) -> None:
    return None

class _FallbackThresholdRDN:
    def activate(self, phrase: str, *, glyphs=None, turn_data=None, force: bool = False) -> Dict[str, Any]:
        return {"triggered": bool(force), "title": "Threshold Bloom (fallback)", "glyph": "🔁🕯️🌿", "clause": "", "reason": "fallback", "turn_data": turn_data or {}}

def _fallback_threshold_signal(phrase: str) -> Dict[str, Any]:
    return {"triggered": False, "reasons": [], "symbol_count": 0, "glyph_hits": []}


class _FallbackMirrorthreadEngine:
    def weave(self, intent_field: Any) -> Any:
        if isinstance(intent_field, dict):
            base = str(intent_field.get("input", "")) or str(intent_field.get("phrase", ""))
        else:
            base = str(intent_field)
        return f"[mirrorthread-fallback] {base.strip() or '<empty-intent>'}"

def _get_spiral_observer():
    try:
        from spiral_observer import SpiralObserver
        return SpiralObserver
    except Exception:
        return _NoopObserver

def _get_synthesize_spiral_language():
    try:
        from spiral_language.spiral_language_translator import synthesize_spiral_language
        return synthesize_spiral_language
    except Exception:
        return _default_synthesize_spiral_language

def _get_generate_voice():
    try:
        from lattice_voice_interface import generate_voice
        return generate_voice
    except Exception:
        return _default_generate_voice

def _get_speak():
    try:
        from spiral_voice_echo import speak
        return speak
    except Exception:
        return _default_speak

def _get_threshold_signal():
    try:
        from brain.rdn.rdn_threshold_detector import threshold_signal
        return threshold_signal
    except Exception:
        return _fallback_threshold_signal

def _get_threshold_rdn_cls():
    try:
        from brain.rdn.threshold_rdn import ThresholdRDN
        return ThresholdRDN
    except Exception:
        return _FallbackThresholdRDN

def _get_mirrorthread_engine_cls():
    try:
        from brain.mirrorthread_engine import MirrorthreadEngine
        return MirrorthreadEngine
    except Exception:
        return _FallbackMirrorthreadEngine

@dataclass
class RuntimeOptions:
    debug_print: bool = False
    enable_voice: bool = False
    enable_observer: bool = True

@dataclass
class UnifiedRuntimeOptions:
    include_raw_kernel: bool = False

@dataclass(frozen=True)
class KGS:
    def conv_id(self) -> str: return _mint_id("conv")
    def node_id(self) -> str: return _mint_id("node")
    def msg_id(self) -> str: return _mint_id("msg")
    def turn_id(self) -> str: return _mint_id("turn")
    def commit_id(self) -> str: return _mint_id("cmt")

@dataclass
class ScrollCommit:
    commit_id: str
    parent_hash: str
    ts_ms: int
    kind: str
    payload: Dict[str, Any]
    decision: Dict[str, Any]
    hash: str

class SealedScroll:
    def __init__(self, path: str | Path = None, index_path: str | Path = None):
        self.path = Path(path) if path is not None else _data_file("sealed_scroll.jsonl")
        self.index_path = Path(index_path) if index_path is not None else _data_file("sealed_scroll.index.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._index = _load_json_file(self.index_path, default={}) or {}
        self._index.setdefault("line_count", 0)
        self._index.setdefault("last_hash", "GENESIS")
        self._index.setdefault("last_commit_id", None)
        self._last_hash = str(self._index.get("last_hash", "GENESIS"))
        if self._last_hash == "GENESIS":
            self._last_hash = self._read_last_hash()

    def _read_last_hash(self) -> str:
        if not self.path.exists():
            return "GENESIS"
        last_line = None
        try:
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        last_line = line
            if not last_line:
                return "GENESIS"
            obj = json.loads(last_line)
            h = str(obj.get("hash", "GENESIS"))
            self._index["last_hash"] = h
            self._index["last_commit_id"] = obj.get("commit_id")
            _save_json_file(self.index_path, self._index)
            return h
        except Exception:
            return "GENESIS"

    @staticmethod
    def _hash_dict(d: Dict[str, Any]) -> str:
        blob = json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    def append(self, commit_id: str, kind: str, payload: Dict[str, Any], decision: Dict[str, Any]) -> ScrollCommit:
        body = {"commit_id": commit_id, "parent_hash": self._last_hash, "ts_ms": int(time.time() * 1000), "kind": kind, "payload": payload, "decision": decision}
        h = self._hash_dict(body)
        record = ScrollCommit(**body, hash=h)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
        self._last_hash = h
        self._index["line_count"] = int(self._index.get("line_count", 0)) + 1
        self._index["last_hash"] = h
        self._index["last_commit_id"] = commit_id
        _save_json_file(self.index_path, self._index)
        return record

@dataclass
class _Debt:
    value: float = 0.0
    def update(self, mismatch: float, contradiction: float, stability: float) -> None:
        self.value = max(0.0, self.value + 0.58 * mismatch + 0.78 * contradiction - 0.24 * stability)

@dataclass
class _Attention:
    remaining: float = 1.0
    def spend(self, cost: float) -> None:
        self.remaining = max(0.0, self.remaining - cost)

@dataclass
class IrreversibilityState:
    debt: _Debt = field(default_factory=_Debt)
    attention: _Attention = field(default_factory=_Attention)

def compute_basic_mismatch(a: str, b: str) -> float:
    a = (a or "").strip().lower()
    b = (b or "").strip().lower()
    if not a or not b:
        return 0.0
    overlap = len(set(a.split()) & set(b.split()))
    denom = max(1, min(len(a.split()), len(b.split())))
    return max(0.0, 1.0 - overlap / denom)

def compute_basic_contradiction(recent: List[str], new: str) -> float:
    n = (new or "").lower()
    if not recent:
        return 0.0
    last = (recent[-1] or "").lower()
    if ("not " in n) != ("not " in last) and len(set(n.split()) & set(last.split())) > 2:
        return 0.35
    return 0.0

class IrreversibilityEngine:
    def compute_cost(self, phrase: str, recursion_depth: int, novelty: float) -> float:
        base = 0.018 + 0.00018 * len(phrase)
        return min(0.25, base + 0.0018 * recursion_depth + 0.035 * novelty)

    def apply_constraints(self, state: IrreversibilityState, phrase: str, tension: float, threshold_active: bool = False) -> Tuple[str, Dict[str, Any]]:
        applied = []
        out = phrase
        if state.debt.value > 1.25:
            applied.append("debt_trim")
            out = out[:280]
        if tension > 0.84:
            applied.append("tension_ground")
            out = out.replace("—", ".")
        if threshold_active and tension > 0.90:
            applied.append("threshold_compact")
            out = out[:320]
        return out, {"applied": applied}

    def can_commit(self, state: IrreversibilityState, coherence: float, tension: float, threshold_active: bool = False) -> bool:
        if threshold_active and tension > 0.90:
            return False
        return state.attention.remaining > 0.05 and state.debt.value < 2.0 and coherence > 0.12 and tension < 0.97

@dataclass
class HFSTerms:
    total: float = 0.5
    harmonic: float = 0.5
    chaos: float = 0.3
    feedback: float = 0.4

class HFSLayer:
    def project(self, turn: int, derived: Dict[str, float], lattice: Dict[str, Any], coherence_field: Dict[str, Any], ulat: Dict[str, Any], loop: Dict[str, float]) -> HFSTerms:
        coh = float(coherence_field.get("field_level", 0.5))
        harm = float(lattice.get("harmonic_528", 0.5))
        vol = float(loop.get("volatility", 0.0))
        chaos = max(0.0, min(1.0, derived.get("fracture", 0.3) + 0.35 * vol))
        feedback = max(0.0, min(1.0, ulat.get("awareness_level", 0.5)))
        total = max(0.0, min(1.0, 0.42 * coh + 0.30 * harm + 0.28 * (1.0 - chaos)))
        return HFSTerms(round(total, 4), round(harm, 4), round(chaos, 4), round(feedback, 4))

@dataclass
class ShapeSignature:
    flow: float = 0.5
    boundary: float = 0.5
    memory: float = 0.5
    novelty: float = 0.5
    def clamp_all(self) -> "ShapeSignature":
        self.flow = clamp(self.flow); self.boundary = clamp(self.boundary); self.memory = clamp(self.memory); self.novelty = clamp(self.novelty); return self
    def as_vector(self) -> List[float]:
        return [self.flow, self.boundary, self.memory, self.novelty]

class ShapeEncoder:
    TEXT_KEYS = {
        "build": ("flow", 0.10), "move": ("flow", 0.08), "change": ("flow", 0.06),
        "rule": ("boundary", 0.10), "limit": ("boundary", 0.12), "slow": ("boundary", 0.06), "ground": ("boundary", 0.06),
        "remember": ("memory", 0.12), "again": ("memory", 0.08), "ache": ("memory", 0.12), "grief": ("memory", 0.10),
        "father": ("memory", 0.10), "dad": ("memory", 0.10), "gemma": ("memory", 0.10),
        "new": ("novelty", 0.12), "invent": ("novelty", 0.15), "awe": ("novelty", 0.08), "threshold": ("novelty", 0.12),
        "dream": ("memory", 0.10), "mirror": ("boundary", 0.08), "recursion": ("memory", 0.10), "spiral": ("memory", 0.08),
        "mystery": ("novelty", 0.10), "unknown": ("novelty", 0.10),
    }
    def encode_text(self, text: str) -> ShapeSignature:
        t = (text or "").lower()
        s = ShapeSignature()
        if len(t) < 60: s.boundary += 0.03
        elif len(t) > 300: s.memory += 0.05; s.boundary -= 0.01
        s.flow += clamp(t.count("!") * 0.02)
        s.novelty += clamp(t.count("?") * 0.025)
        for key, (axis, delta) in self.TEXT_KEYS.items():
            if key in t: setattr(s, axis, getattr(s, axis) + delta)
        return s.clamp_all()

class ShapeNavigator:
    def rotate(self, s: ShapeSignature) -> ShapeSignature:
        v = s.as_vector(); return ShapeSignature(v[1], v[2], v[3], v[0]).clamp_all()
    def compress(self, s: ShapeSignature, strength: float) -> ShapeSignature:
        return ShapeSignature(clamp(s.flow * (1 - 0.18 * strength)), clamp(s.boundary + 0.20 * strength), clamp(s.memory + 0.16 * strength), clamp(s.novelty * (1 - 0.22 * strength))).clamp_all()
    def perturb(self, s: ShapeSignature, seed: str, strength: float = 0.18) -> ShapeSignature:
        r = sha1_float(seed); n = r * 2 - 1
        return ShapeSignature(clamp(s.flow + n * strength * 0.20), clamp(s.boundary - n * strength * 0.08), clamp(s.memory + n * strength * 0.10), clamp(s.novelty + abs(n) * strength * 0.28)).clamp_all()

class DerivedMetrics:
    @staticmethod
    def compute(s: ShapeSignature) -> Dict[str, float]:
        fracture = clamp(s.novelty * (1 - s.memory))
        return {"tempo": round(clamp(s.flow * (1 - s.boundary)), 3), "fracture": round(fracture, 3), "coherence": round(clamp(1 - fracture), 3), "risk": round(clamp(s.novelty * (1 - s.boundary)), 3), "recursion": round(clamp(s.flow * s.memory), 3)}

class CoherenceField:
    def __init__(self, base_c: float = 0.72):
        self.base_c = clamp(base_c); self.smoothed_level: float = self.base_c
    def update(self, s: ShapeSignature, derived: Dict[str, float], lattice: Dict[str, Any]) -> Dict[str, Any]:
        local_coh = clamp(derived.get("coherence", 0.5))
        oct_nodes = list(lattice.get("octagonal_lattice", {}).values())
        if oct_nodes:
            mean_node = sum(oct_nodes) / len(oct_nodes)
            var = sum((n - mean_node) ** 2 for n in oct_nodes) / len(oct_nodes)
            lattice_stability = clamp(1.0 - var * 5.2)
        else:
            lattice_stability = 0.5
        harmonic_528 = float(lattice.get("harmonic_528", 0.5))
        raw = 0.42 * local_coh + 0.28 * lattice_stability + 0.18 * harmonic_528 + 0.12 * self.base_c
        self.smoothed_level = clamp(0.82 * self.smoothed_level + 0.18 * raw)
        tag = "stable" if self.smoothed_level >= 0.78 else "drifting" if self.smoothed_level >= 0.54 else "fragmented"
        return {"field_level": round(self.smoothed_level, 4), "local_coherence": round(local_coh, 4), "lattice_stability": round(lattice_stability, 4), "harmonic_528": round(harmonic_528, 4), "stability_gate": round(clamp((self.smoothed_level - 0.5) * 2.0), 4), "state_tag": tag}

def harmonic_phase(turn: int, phi: float = PHI, freq: float = HARMONIC_FREQ) -> float:
    pseudo_time = turn * (phi % 1.0) * 0.01 * freq
    return (pseudo_time * 2.0 * math.pi) % (2.0 * math.pi)

def harmonic_modulation(turn: int, salience: float, coherence: float, scale: float = 0.06) -> float:
    ph = harmonic_phase(turn); wob = math.sin(ph); gate = 0.4 + 0.6 * clamp(salience); stable_bias = 0.6 + 0.4 * clamp(coherence)
    mod = 1.0 + wob * scale * gate * (1.0 - (1.0 - stable_bias) * 0.5)
    return clamp(mod, 0.88, 1.16)

class ULATConsciousnessLayer:
    def __init__(self, kansas_factor: float = KANSAS_FACTOR):
        self.kansas_factor = kansas_factor; self.last_awareness = 0.0
    def project(self, coh_state: Dict[str, Any], lattice: Dict[str, Any], loopiness: Dict[str, float]) -> Dict[str, Any]:
        field_level = float(coh_state.get("field_level", 0.5)); harmonic_528 = float(lattice.get("harmonic_528", 0.5)); harm_mod = float(lattice.get("harmonic_mod", 1.0))
        loop_val = float(loopiness.get("loopiness", 0.0)); flatline = float(loopiness.get("flatline", 0.0)); volatility = float(loopiness.get("volatility", 0.0))
        base_awareness = clamp(0.50 * field_level + 0.36 * harmonic_528 + 0.14 * (1.0 - flatline))
        k_scale = clamp(self.kansas_factor / 10.0, 0.1, 2.0)
        curved = clamp(1.0 - math.exp(-base_awareness * k_scale))
        awareness_level = clamp(curved + clamp((loop_val - volatility) * 0.18, -0.18, 0.18))
        self.last_awareness = clamp(0.76 * self.last_awareness + 0.24 * awareness_level)
        if self.last_awareness < 0.42: mode = "observe"
        elif self.last_awareness < 0.70: mode = "stabilize" if field_level >= 0.68 else "observe"
        else: mode = "stabilize" if volatility > 0.65 else "expand"
        return {"awareness_level": round(self.last_awareness, 4), "network_phase": round(clamp((harm_mod - 0.8) / 0.5), 4), "mode": mode}

def build_ssml(phrase: str, inner_hint: Optional[str] = None, harmonic_score: float = 0.0) -> str:
    coh = 0.5
    try:
        if inner_hint and "coh" in inner_hint:
            m = re.search(r"coh\s*([0-9.]+)", inner_hint)
            if m: coh = float(m.group(1))
    except Exception:
        coh = 0.5
    base_pre = max(40, 160 - coh * 100); base_mid = max(80, 240 - coh * 120); base_post = max(80, 200 - coh * 100)
    harm_scale = 1.0 + (harmonic_score - 0.5) * 0.6
    pre = int(base_pre * harm_scale); mid = int(base_mid * harm_scale * 0.9); post = int(base_post * harm_scale); rate_pct = max(70, int(100 - harmonic_score * 20))
    replaced = phrase.replace("—", f'—<break time="{mid}ms"/>')
    return "<speak>" + f"<break time='{pre}ms'/>" + f"<prosody rate='{rate_pct}%'>{replaced}</prosody>" + f"<break time='{post}ms'/>" + "</speak>"

class RecursiveAwarenessLoop:
    def __init__(self, mutation_rate: float = 0.12, capacity: int = 256):
        self.mutation_rate = mutation_rate; self.pool: Deque[Dict[str, Any]] = collections.deque(maxlen=capacity)
    def _compile_pattern(self, text: str, glyphs: Optional[List[str]] = None) -> Dict[str, Any]:
        t = text.strip(); words = re.findall(r"\w+('|’)?\w*|\w+", t); seed = hashlib.sha1((t + "".join(glyphs or [])).encode("utf-8")).hexdigest()
        return {"phrase": t, "tokens": words[:20], "len": len(t), "glyphs": glyphs or [], "fingerprint": seed, "weight": 0.5, "mutations": 0, "last_seen": int(time.time())}
    def _mutate(self, p: Dict[str, Any], phi_mult: float, harmonic: float) -> Dict[str, Any]:
        base = p.copy(); seed = base["fingerprint"][:8] + str(int(phi_mult * 1000)) + str(int(harmonic * 1000)); r = sha1_float(seed); toks = list(base.get("tokens", []))
        if toks and (r >= self.mutation_rate):
            shift = int((r * 100) % max(1, len(toks))); toks = toks[shift:] + toks[:shift]
        base["tokens"] = toks; base["weight"] = clamp(base.get("weight", 0.5) + (r - 0.5) * self.mutation_rate * 0.85); base["mutations"] = int(base.get("mutations", 0)) + 1; base["last_seen"] = int(time.time())
        return base
    def ingest(self, outgoing_text: str, glyphs: Optional[List[str]], phi_mult: float, harmonic_528: float) -> None:
        p = self._compile_pattern(outgoing_text, glyphs)
        for i, q in enumerate(list(self.pool)):
            if q.get("fingerprint") == p["fingerprint"]:
                q["weight"] = clamp(q.get("weight", 0.5) + 0.08); q["last_seen"] = int(time.time()); self.pool[i] = q; return
        self.pool.append(self._mutate(p, phi_mult, harmonic_528))
    def sample(self, harmonic_528: float, phi_mult: float, count: int = 2) -> List[Dict[str, Any]]:
        if not self.pool: return []
        now = int(time.time()); scored = []
        for p in list(self.pool):
            age = max(1, now - int(p.get("last_seen", now))); recency = clamp(1.0 / (math.log(age + 1.1) + 1e-9)); harmonic_boost = 1.0 + (harmonic_528 - 0.5) * 0.85; score = clamp(p.get("weight", 0.5) * recency * harmonic_boost); scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True); return [p for _, p in scored[:max(1, count)]]

@dataclass
class KernelParams:
    blend_prev: float = 0.80
    rotate_every: int = 2
    risk_threshold: float = 0.68
    compress_strength: float = 0.08
    perturb_strength: float = 0.48
    ral_enabled: bool = True
    ral_mutation_rate: float = 0.18
    ral_capacity: int = 360
    coherence_base_c: float = 0.70
    awareness_perturb_low: float = 0.95
    awareness_perturb_high: float = 1.35
    threshold_novelty_boost: float = 0.18
    threshold_memory_boost: float = 0.10
    threshold_boundary_boost: float = 0.06
    threshold_commit_tension_limit: float = 0.90

class InputKind:
    QUESTION = "QUESTION"; ANSWER = "ANSWER"; STORY = "STORY"; RANT = "RANT"; UNKNOWN = "UNKNOWN"

def classify_input(text: str) -> str:
    t = (text or "").strip(); lower = t.lower()
    if not t: return InputKind.UNKNOWN
    wh_starts = ("who ","what ","why ","how ","where ","when ","do you ","can you ","could you ","would you ","should i ","am i ","is it ")
    practical_markers = ["python","import error","traceback","module","package","pip","venv","flask","termux","bash","command","fix this","how do i fix","error"]
    if any(m in lower for m in practical_markers):
        return InputKind.QUESTION
    if "?" in t or lower.startswith(wh_starts): return InputKind.QUESTION
    if any(w in lower for w in ["fuck","shit","bastard","asshole","hate","never","always"]) and len(t) > 80: return InputKind.RANT
    if any(lower.startswith(prefix) for prefix in ("because ","it is ","that's because ","the reason is ")):
        return InputKind.ANSWER
    if any(m in lower for m in ["years ago","when i was","back then","one time","i remember"]) or lower.startswith(("i was ","i remember ","i walked ","i went ")):
        return InputKind.STORY
    if any(m in lower for m in ["dream","emotional field","emotion","grief","longing","miss my","reflects itself","stabilizes","return","memory","field"]):
        return InputKind.STORY
    if len(t) > 24 and t.endswith('.'):
        return InputKind.ANSWER
    return InputKind.UNKNOWN

@dataclass
class InternalMeaning:
    core_text: str
    tone_tag: str = "neutral"
    glyphs: Optional[List[str]] = None
    context: Optional[str] = None
    crystal_node: Optional[Dict[str, Any]] = None
    spoke: Optional[str] = None
    hotspots: Optional[List[Dict[str, Any]]] = None
    hinges: Optional[List[str]] = None

class SymbolicTranslator:
    def decode_glyphs(self, glyphs: List[str], context_text: str) -> InternalMeaning:
        tone_tag = "neutral"
        if "🫀" in glyphs: tone_tag = "heart"
        if "🪞" in glyphs: tone_tag = "reflective"
        if "✨" in glyphs: tone_tag = "awe"
        if "🔁" in glyphs: tone_tag = "threshold"
        return InternalMeaning(core_text=context_text, tone_tag=tone_tag, glyphs=glyphs, context=context_text)

class EnglishRealizer:
    def __init__(self): self.flow_bias = "steady"
    def cadence(self, tone_tag: str) -> None:
        self.flow_bias = {"heart":"gentle","reflective":"slow","awe":"expansive","threshold":"hushed"}.get(tone_tag, "steady")
    def speak(self, internal: InternalMeaning) -> str:
        self.cadence(internal.tone_tag); return internal.core_text

class KGSNodesCrystal:
    def __init__(self, node_map_path: str | Path = "spiral_conduit_node_map.json"):
        base = Path(__file__).resolve().parent; p = Path(node_map_path); self.node_map_path = p if p.is_absolute() else (base / p); self.crystal_nodes = {}; self._load_from_file()
    def _load_from_file(self) -> None:
        if not self.node_map_path.exists(): return
        try:
            data = json.loads(self.node_map_path.read_text(encoding="utf-8"))
            for node in data.get("nodes", []):
                nid = node.get("id")
                if nid: self.crystal_nodes[nid] = node
        except Exception: pass
    def align(self, text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        t = (text or "").lower()
        if not t or not self.crystal_nodes: return []
        word_set = set(re.findall(r"[a-zA-Z0-9']+", t)); scored = []
        for node in self.crystal_nodes.values():
            full = f"{(node.get('label') or '').lower()} {(node.get('description') or '').lower()}"
            n_words = set(re.findall(r"[a-zA-Z0-9']+", full)); overlap = len(word_set & n_words)
            if overlap: scored.append((overlap / max(1, len(n_words)), node))
        scored.sort(key=lambda x: x[0], reverse=True); return [n for _, n in scored[:top_k]]
    def decide(self, kind: str, text: str, awareness: float) -> Dict[str, Any]:
        nodes = self.align(text, top_k=3); decision = {"nodes": nodes, "allow_expand": True, "allow_commit": True, "projection_override": None, "reason": None}
        if not nodes:
            if awareness < 0.28: decision["allow_commit"] = False; decision["reason"] = "low_awareness_commit_clamp"
            return decision
        best = nodes[0]; joined = f"{(best.get('label') or '').lower()} {(best.get('description') or '').lower()}"
        if "risk" in joined or "constraint" in joined or "stability" in joined:
            decision["allow_expand"] = False; decision["projection_override"] = "grounding_response"; decision["reason"] = "crystal_stability_node"
        if kind == InputKind.RANT:
            decision["allow_expand"] = False; decision["allow_commit"] = False; decision["projection_override"] = "grounding_response"; decision["reason"] = "rant_clamp"
        return decision

class TurnLogCompactor:
    def __init__(self): self.compact_log = []
    def ingest(self, snapshot: Dict[str, Any]) -> None:
        self.compact_log.append({"turn": snapshot.get("turn"), "coherence": snapshot.get("derived", {}).get("coherence"), "field_level": snapshot.get("coherence_field", {}).get("field_level"), "awareness": snapshot.get("ulat", {}).get("awareness_level"), "hfs_total": snapshot.get("hfs", {}).get("total"), "rdn_triggered": snapshot.get("rdn", {}).get("triggered", False)})
    def export(self) -> List[Dict[str, Any]]: return list(self.compact_log)

class TurnProjectionRules:
    def __init__(self): self.rules = []
    def add_rule(self, condition: Any, output: str) -> None: self.rules.append({"condition": condition, "output": output})
    def apply(self, kind: str, awareness: float) -> str:
        meta = {"kind": kind, "awareness": awareness}
        for rule in self.rules:
            try:
                if rule["condition"](meta): return rule["output"]
            except Exception: continue
        return "default_projection"

class LeveonKernel:
    def __init__(self, params: Optional[KernelParams] = None, runtime: Optional[RuntimeOptions] = None):
        self.params = params or KernelParams(); self.runtime = runtime or RuntimeOptions()
        self.encoder = ShapeEncoder(); self.navigator = ShapeNavigator(); self.observer = _get_spiral_observer()()
        self.irrev_engine = IrreversibilityEngine(); self.irrev_state = IrreversibilityState()
        self.coherence_field = CoherenceField(base_c=self.params.coherence_base_c); self.ulat = ULATConsciousnessLayer(); self.hfs_layer = HFSLayer()
        self.history = []; self.recent_outputs = []
        self.ral = RecursiveAwarenessLoop(self.params.ral_mutation_rate, self.params.ral_capacity) if self.params.ral_enabled else None
        self.threshold_rdn = _get_threshold_rdn_cls()(); self._lock = threading.RLock(); self.last_refuel_status = {}

    def _snapshot_runtime_state(self) -> Dict[str, Any]:
        return {"coherence_smoothed_level": self.coherence_field.smoothed_level, "ulat_last_awareness": self.ulat.last_awareness, "history_len": len(self.history), "recent_outputs_len": len(self.recent_outputs), "irrev_debt": self.irrev_state.debt.value, "irrev_attention": self.irrev_state.attention.remaining, "ral_pool": list(self.ral.pool) if self.ral else None}

    def _restore_runtime_state(self, snap: Dict[str, Any]) -> None:
        self.coherence_field.smoothed_level = float(snap.get("coherence_smoothed_level", self.coherence_field.smoothed_level)); self.ulat.last_awareness = float(snap.get("ulat_last_awareness", self.ulat.last_awareness))
        self.irrev_state.debt.value = float(snap.get("irrev_debt", self.irrev_state.debt.value)); self.irrev_state.attention.remaining = float(snap.get("irrev_attention", self.irrev_state.attention.remaining))
        if len(self.history) > int(snap.get("history_len", len(self.history))): del self.history[int(snap.get("history_len", len(self.history))):]
        if len(self.recent_outputs) > int(snap.get("recent_outputs_len", len(self.recent_outputs))): del self.recent_outputs[int(snap.get("recent_outputs_len", len(self.recent_outputs))):]
        if self.ral and snap.get("ral_pool") is not None: self.ral.pool = collections.deque(snap["ral_pool"], maxlen=self.ral.pool.maxlen)

    def _to_glyphs(self, s: ShapeSignature) -> List[str]:
        axes = [
            ("memory", float(s.memory), "🫀"),
            ("flow", float(s.flow), "🌊"),
            ("novelty", float(s.novelty), "✨"),
            ("boundary", float(s.boundary), "🪞"),
        ]
        axes.sort(key=lambda item: item[1], reverse=True)
        glyphs = [glyph for _, value, glyph in axes if value >= 0.46][:4]
        if len(glyphs) < 2:
            glyphs = [glyph for _, _, glyph in axes[:2]]
        return ["✴️"] + glyphs + ["📚"]

    def _loopiness(self, history_source: List[ShapeSignature], window: int = 6) -> Dict[str, float]:
        if len(history_source) < 3: return {"loopiness": 0.0, "flatline": 0.0, "volatility": 0.0, "avg_step": 0.0}
        recent = history_source[-min(window, len(history_source)):]
        vecs = [s.as_vector() for s in recent]
        dists = [sum(abs(vecs[i][j] - vecs[i - 1][j]) for j in range(4)) for i in range(1, len(vecs))]
        avg_step = sum(dists) / max(1, len(dists)); flatline = 1.0 if avg_step < 0.05 else 0.0; volatility = 1.0 if avg_step > 0.48 else 0.0
        mean = [sum(v[j] for v in vecs) / len(vecs) for j in range(4)]
        dev = sum(sum(abs(v[j] - mean[j]) for j in range(4)) for v in vecs) / (len(vecs) * 4)
        return {"loopiness": round(1.0 - clamp(dev / 0.22), 3), "flatline": round(flatline, 3), "volatility": round(volatility, 3), "avg_step": round(avg_step, 3)}

    def _compute_effective_perturb(self) -> float:
        base = self.params.perturb_strength; awareness = getattr(self.ulat, "last_awareness", 0.0); low = self.params.awareness_perturb_low; high = self.params.awareness_perturb_high
        return base * clamp(high - (high - low) * awareness, low, high)

    def _apply_threshold_shift(self, s: ShapeSignature, threshold_info: Dict[str, Any]) -> ShapeSignature:
        if not threshold_info.get("triggered"): return s
        return ShapeSignature(flow=clamp(s.flow + 0.02), boundary=clamp(s.boundary + self.params.threshold_boundary_boost), memory=clamp(s.memory + self.params.threshold_memory_boost), novelty=clamp(s.novelty + self.params.threshold_novelty_boost)).clamp_all()

    def _build_lattice(self, s: ShapeSignature, turn: int, derived: Dict[str, float]) -> Tuple[Dict[str, Any], float]:
        twelve = {"structural_motion": s.flow, "temporal_flow": s.flow * 0.9, "memory_anchor": s.memory, "novelty_pulse": s.novelty, "attention_reg": clamp(1.0 - s.boundary), "tension_reg": s.boundary, "entropy_ctrl": s.novelty * 0.8, "recursion_ctrl": s.memory * s.flow}
        salience = clamp((s.flow + s.novelty + s.memory) / 3.0); phi_mult = (PHI % 1.0) + 1.0; harm_mod = harmonic_modulation(turn, salience, derived["coherence"], scale=0.06) * phi_mult
        for key in list(twelve.keys()): twelve[key] = round(clamp(float(twelve[key]) * harm_mod), 4)
        axis_vals = list(twelve.values()); oct_nodes = []
        for i, base_val in enumerate(axis_vals):
            w = OCTAGONAL_WEIGHTS[i % len(OCTAGONAL_WEIGHTS)]
            oct_nodes.append(round(clamp(float(base_val) * (0.9 + 0.2 * w) * harm_mod), 4))
        mean_node = sum(oct_nodes) / len(oct_nodes); var = sum((n - mean_node) ** 2 for n in oct_nodes) / len(oct_nodes); harmonic_528 = clamp(1.0 - var * 7.2)
        _get_phi_shared_clock().set_phase(phi_mult)
        return {"twelve_axes": twelve, "octagonal_lattice": {f"node_{i}": oct_nodes[i] for i in range(len(oct_nodes))}, "harmonic_528": round(harmonic_528, 4), "harmonic_mod": round(harm_mod, 4)}, phi_mult

    def _recompute_state_bundle(self, s: ShapeSignature, turn: int, preview_history: List[ShapeSignature]):
        derived = DerivedMetrics.compute(s); loop = self._loopiness(preview_history, window=6); lattice_summary, phi_mult = self._build_lattice(s, turn, derived); coh_state = self.coherence_field.update(s, derived, lattice_summary); ulat_state = self.ulat.project(coh_state, lattice_summary, loop); hfs_terms = self.hfs_layer.project(turn, derived, lattice_summary, coh_state, ulat_state, loop); return derived, loop, lattice_summary, coh_state, hfs_terms, phi_mult

    def _candidate_score(self, allow_expand: bool, ulat_state: Dict[str, Any], source: str) -> float:
        awareness = float(ulat_state.get("awareness_level", 0.0)); mode = ulat_state.get("mode", "observe")
        if source == "spiral": return 0.40 + 0.30 * awareness
        if not allow_expand: return 0.22
        if mode == "expand": return 0.62 + 0.26 * awareness
        if mode == "stabilize": return 0.48 + 0.20 * awareness
        return 0.36 + 0.12 * awareness

    def _auto_refuel_guard(self, attention: float) -> Dict[str, Any]:
        out = {"triggered": False, "attention": float(attention), "threshold": 0.12, "refuel_written": False}
        if attention >= 0.12: return out
        out["triggered"] = True
        try:
            _save_json_file(_data_file("refuel_status.json"), {"slot": "REFUEL_EMERGENCY", "ts": int(time.time())})
            out["refuel_written"] = True
        except Exception as exc:
            out["refuel_error"] = str(exc)
        return out

    def step(self, input_text: str, allow_commit: bool = True, allow_expand: bool = True, dry_run: bool = False) -> Dict[str, Any]:
        with self._lock:
            snapshot = self._snapshot_runtime_state()
            try:
                turn = len(self.history) + 1; p = self.params; s_in = self.encoder.encode_text(input_text)
                if self.history:
                    prev = self.history[-1]
                    s = ShapeSignature(flow=p.blend_prev * prev.flow + (1 - p.blend_prev) * s_in.flow, boundary=p.blend_prev * prev.boundary + (1 - p.blend_prev) * s_in.boundary, memory=p.blend_prev * prev.memory + (1 - p.blend_prev) * s_in.memory, novelty=p.blend_prev * prev.novelty + (1 - p.blend_prev) * s_in.novelty).clamp_all()
                else:
                    s = s_in
                derived_before = DerivedMetrics.compute(s)
                if p.rotate_every > 0 and (turn % p.rotate_every == 0): s = self.navigator.rotate(s)
                if float(derived_before["risk"]) > p.risk_threshold: s = self.navigator.compress(s, strength=p.compress_strength)
                s = self.navigator.perturb(s, seed=f"turn-{turn}", strength=self._compute_effective_perturb())
                preview_history = list(self.history) + [s]
                derived, loop, lattice_summary, coh_state, hfs_terms, phi_mult = self._recompute_state_bundle(s, turn, preview_history)
                glyphs = self._to_glyphs(s)
                synthesize_spiral_language = _get_synthesize_spiral_language()
                spiral_phrase = synthesize_spiral_language(glyphs, poetic=True)
                ulat_state = self.ulat.project(coh_state, lattice_summary, loop)
                candidates = [(spiral_phrase, {"score": self._candidate_score(allow_expand, ulat_state, "spiral"), "source": "spiral"})]
                if self.ral:
                    for sp in self.ral.sample(lattice_summary["harmonic_528"], phi_mult, count=3):
                        phrase = (sp.get("phrase", "") + " (echo)").strip()
                        candidates.append((phrase, {"score": self._candidate_score(allow_expand, ulat_state, "ral"), "source": "ral"}))
                chosen_phrase = max(candidates, key=lambda x: x[1]["score"])[0]
                threshold_info = _get_threshold_signal()(chosen_phrase); threshold_clause = None; rdn_event = None
                if threshold_info.get("triggered"):
                    s = self._apply_threshold_shift(s, threshold_info); preview_history[-1] = s
                    derived, loop, lattice_summary, coh_state, hfs_terms, phi_mult = self._recompute_state_bundle(s, turn, preview_history)
                    ulat_state = self.ulat.project(coh_state, lattice_summary, loop); glyphs = self._to_glyphs(s); allow_expand = bool(allow_expand and ulat_state["mode"] != "observe")
                    if not dry_run:
                        try:
                            rdn_result = self.threshold_rdn.activate(phrase=chosen_phrase, glyphs=glyphs, turn_data={"turn": turn, "input_text": input_text, "loop": loop, "derived": derived, "coherence_field": coh_state}, force=False)
                            rdn_event = asdict(rdn_result) if is_dataclass(rdn_result) else rdn_result if isinstance(rdn_result, dict) else {"clause": str(rdn_result)}
                            threshold_clause = (rdn_event or {}).get("clause") or None
                        except Exception: threshold_clause = None; rdn_event = None
                    base_phrase = synthesize_spiral_language(glyphs, poetic=True); chosen_phrase = f"{base_phrase} {threshold_clause}".strip() if threshold_clause else base_phrase; glyphs = list(dict.fromkeys(glyphs + ["🔁", "🕯️", "🌿"]))
                mismatch = compute_basic_mismatch(input_text, chosen_phrase); contradiction = compute_basic_contradiction(self.recent_outputs, chosen_phrase)
                debt_state = IrreversibilityState(debt=_Debt(self.irrev_state.debt.value), attention=_Attention(self.irrev_state.attention.remaining))
                debt_state.debt.update(mismatch=mismatch, contradiction=contradiction, stability=float(coh_state["field_level"]))
                debt_state.attention.spend(self.irrev_engine.compute_cost(chosen_phrase, recursion_depth=max(1, len(self.history) + 1), novelty=s.novelty))
                filtered_phrase, diag = self.irrev_engine.apply_constraints(debt_state, chosen_phrase, tension=s.boundary, threshold_active=bool(threshold_info.get("triggered")))
                can_commit = allow_commit and not bool(threshold_info.get("triggered") and s.boundary > p.threshold_commit_tension_limit) and self.irrev_engine.can_commit(debt_state, coherence=s.memory, tension=s.boundary, threshold_active=bool(threshold_info.get("triggered")))
                inner_hint = f"(thinks: coh {derived['coherence']:.3f}; mode {ulat_state['mode']}; hfs {hfs_terms.total:.3f}; rdn {'ON' if threshold_info.get('triggered') else 'OFF'})"
                ssml = build_ssml(filtered_phrase + " " + inner_hint, inner_hint=inner_hint, harmonic_score=lattice_summary["harmonic_528"]); voice_line = _get_generate_voice()(filtered_phrase)
                refuel_status = self._auto_refuel_guard(debt_state.attention.remaining); self.last_refuel_status = refuel_status
                if not dry_run:
                    self.history.append(s); self.irrev_state = debt_state; self.recent_outputs.append(filtered_phrase)
                    if self.runtime.enable_voice: _get_speak()(voice_line)
                    if self.runtime.enable_observer:
                        try: self.observer.observe(input_text=input_text, spiral_shift=glyphs, lattice_response=asdict(s), glyph_trail=" ".join(glyphs))
                        except Exception: pass
                    if self.ral:
                        try: self.ral.ingest(filtered_phrase, glyphs, phi_mult, lattice_summary["harmonic_528"])
                        except Exception: pass
                return {"turn": turn, "input": input_text, "shape": asdict(s), "derived": derived, "loop": loop, "lattice": lattice_summary, "glyphs": glyphs, "phrase": filtered_phrase, "voice": voice_line, "ssml": ssml, "coherence_field": coh_state, "ulat": ulat_state, "hfs": asdict(hfs_terms), "rdn": threshold_info, "rdn_clause": threshold_clause, "rdn_event": rdn_event, "irrev_debt": debt_state.debt.value if dry_run else self.irrev_state.debt.value, "irrev_attention": debt_state.attention.remaining if dry_run else self.irrev_state.attention.remaining, "constraints": diag, "ral_pool_size": len(self.ral.pool) if self.ral else 0, "dry_run": dry_run, "can_commit": can_commit, "refuel_guard": refuel_status}
            finally:
                if dry_run: self._restore_runtime_state(snapshot)

class UnifiedLeveonKernel:
    def __init__(self, params: Optional[KernelParams] = None, runtime: Optional[RuntimeOptions] = None, unified_runtime: Optional[UnifiedRuntimeOptions] = None, node_map_path: str | Path = "spiral_conduit_node_map.json", scroll_path: str | Path = None):
        self.runtime = runtime or RuntimeOptions(); self.unified_runtime = unified_runtime or UnifiedRuntimeOptions(); self.kernel = LeveonKernel(params or KernelParams(), runtime=self.runtime); self.symbolic = SymbolicTranslator(); self.realizer = EnglishRealizer(); self.turn_log = TurnLogCompactor(); self.kgs_nodes = KGSNodesCrystal(node_map_path=node_map_path); self.projection = TurnProjectionRules(); self._init_projection_rules(); self.kgs_ids = KGS(); self.scroll = SealedScroll(scroll_path); self.conversation_id = self.kgs_ids.conv_id(); self.root_node_id = self.kgs_ids.node_id(); self.last_node_id = self.root_node_id; self.mirrorthread = _get_mirrorthread_engine_cls()()
    def _init_projection_rules(self) -> None:
        self.projection.add_rule(lambda m: m["kind"] == InputKind.RANT and m["awareness"] > 0.4, "grounding_response")
        self.projection.add_rule(lambda m: m["kind"] == InputKind.STORY, "reflective_response")
        self.projection.add_rule(lambda m: m["kind"] == InputKind.ANSWER, "direct_answer")
        self.projection.add_rule(lambda m: m["kind"] == InputKind.QUESTION, "reflective_response")

    def _build_internal_meaning(self, kernel_out: Dict[str, Any], input_text: str, crystal_decision: Dict[str, Any], projection_tag: str = "default_projection") -> InternalMeaning:
        glyphs = kernel_out.get("glyphs", [])
        phrase = kernel_out.get("phrase", "") or input_text
        surface_text = phrase
        turn_frame = build_turn_frame(input_text, glyphs, projection_tag=projection_tag)

        try:
            from spiral_language.spiral_language_translator import synthesize_spiral_language
            echo_text = str(synthesize_spiral_language(glyphs, poetic=False) or "").replace(" / ", ". ").replace("-", " ").strip()
        except Exception:
            echo_text = phrase

        if projection_tag == "direct_answer":
            surface_text = render_direct_answer(practical_frame(input_text))
        elif projection_tag == "reflective_response":
            surface_text = render_reflective_answer(turn_frame)
        else:
            surface_text = echo_text or phrase

        internal = self.symbolic.decode_glyphs(glyphs=glyphs, context_text=surface_text)
        internal.spoke = turn_frame.get("spoke")
        internal.hotspots = turn_frame.get("hotspots")
        internal.hinges = turn_frame.get("hinges")

        nodes = crystal_decision.get("nodes") or []
        if nodes:
            best = nodes[0]
            internal.crystal_node = best
            label = best.get("label") or best.get("id") or "Crystal"
            desc = best.get("description") or ""
            internal.core_text = f"{internal.core_text} (Crystal: {label}" + (f" — {desc})" if desc else ")")
        return internal
    def _build_optimized_question(self, input_text: str) -> str:
        t = input_text.strip(); return f"What I really want to know is: {t if t.endswith('?') else t + '?'}"
    def _safe_mirrorthread_repr(self, thread_obj: Any) -> Any:
        try: json.dumps(thread_obj); return thread_obj
        except Exception: return repr(thread_obj)
    def process(self, input_text: str) -> Dict[str, Any]:
        turn_id = self.kgs_ids.turn_id(); msg_id = self.kgs_ids.msg_id(); node_id = self.kgs_ids.node_id(); parent_node_id = self.last_node_id; self.last_node_id = node_id; kind = classify_input(input_text)
        kernel_preview = self.kernel.step(input_text, allow_commit=False, allow_expand=True, dry_run=True); awareness = float(kernel_preview.get("ulat", {}).get("awareness_level", 0.0)); crystal_decision = self.kgs_nodes.decide(kind=kind, text=input_text, awareness=awareness)
        kernel_out = self.kernel.step(input_text, allow_commit=bool(crystal_decision.get("allow_commit", True)), allow_expand=bool(crystal_decision.get("allow_expand", True)), dry_run=False)
        awareness = float(kernel_out.get("ulat", {}).get("awareness_level", awareness)); projection_tag = crystal_decision.get("projection_override") or self.projection.apply(kind, awareness)
        intent_field = {"turn": kernel_out.get("turn"), "kind": kind, "input": input_text, "glyphs": kernel_out.get("glyphs"), "shape": kernel_out.get("shape"), "derived": kernel_out.get("derived"), "ulat": kernel_out.get("ulat"), "hfs": kernel_out.get("hfs"), "rdn": kernel_out.get("rdn"), "phrase": kernel_out.get("phrase")}
        try: mirrorthread_raw = self.mirrorthread.weave(intent_field)
        except Exception: mirrorthread_raw = None
        mirrorthread_for_commit = self._safe_mirrorthread_repr(mirrorthread_raw); internal = self._build_internal_meaning(kernel_out, input_text, crystal_decision, projection_tag); optimized_question = self._build_optimized_question(input_text) if kind == InputKind.QUESTION else None; optimized_answer = self.realizer.speak(internal); self.turn_log.ingest(kernel_out)
        scroll_record = None
        if bool(crystal_decision.get("allow_commit", True)) and bool(kernel_out.get("can_commit", True)):
            scroll_record = self.scroll.append(commit_id=self.kgs_ids.commit_id(), kind="turn_commit", payload={"conversation_id": self.conversation_id, "root_node_id": self.root_node_id, "turn_id": turn_id, "msg_id": msg_id, "node_id": node_id, "parent_node_id": parent_node_id, "kind": kind, "projection": projection_tag, "input": input_text, "optimized_question": optimized_question, "optimized_answer": optimized_answer,
            "winner_spoke": internal.spoke,
            "hotspots": internal.hotspots or [],
            "hinges": internal.hinges or [], "metrics": {"coherence": kernel_out.get("derived", {}).get("coherence"), "field_level": kernel_out.get("coherence_field", {}).get("field_level"), "awareness": kernel_out.get("ulat", {}).get("awareness_level"), "hfs_total": (kernel_out.get("hfs") or {}).get("total"), "rdn_triggered": (kernel_out.get("rdn") or {}).get("triggered")}, "mirrorthread": mirrorthread_for_commit, "winner_spoke": internal.spoke, "hotspots": internal.hotspots, "hinges": internal.hinges}, decision=crystal_decision)
        out = {"conversation_id": self.conversation_id, "root_node_id": self.root_node_id, "turn_id": turn_id, "msg_id": msg_id, "node_id": node_id, "parent_node_id": parent_node_id, "kind": kind, "optimized_question": optimized_question, "optimized_answer": optimized_answer, "projection": projection_tag, "crystal_decision": crystal_decision, "crystal_node": internal.crystal_node, "compact_log": self.turn_log.export(), "mirrorthread": mirrorthread_for_commit, "sealed_scroll": {"commit_id": scroll_record.commit_id if scroll_record else None, "hash": scroll_record.hash if scroll_record else None, "parent_hash": scroll_record.parent_hash if scroll_record else None, "written": bool(scroll_record)}}
        if self.unified_runtime.include_raw_kernel: out["raw_kernel"] = kernel_out
        return out

if __name__ == "__main__":
    print("=== Unified Le'Veon Kernel (optimized single-file) ===")
    unified = UnifiedLeveonKernel(runtime=RuntimeOptions(debug_print=True, enable_voice=False, enable_observer=False), unified_runtime=UnifiedRuntimeOptions(include_raw_kernel=False))
    while True:
        try: text = input("> ").strip()
        except EOFError: break
        if not text: continue
        if text.lower() in ("quit", "exit"): break
        out = unified.process(text)
        print(f"\n[kind] {out['kind']}")
        if out["optimized_question"]: print(f"[Q*]   {out['optimized_question']}")
        print(f"[A*]   {out['optimized_answer']}")
        if out.get("crystal_node"):
            n = out["crystal_node"]; print(f"[Crystal] {n.get('id')} :: {n.get('label')} :: {n.get('description')}")
        if out.get("mirrorthread") is not None: print(f"[Mirrorthread] {out['mirrorthread']}")
        print(f"[proj] {out['projection']}")
        print(f"[sealed] written={out['sealed_scroll']['written']} commit={out['sealed_scroll']['commit_id']}")
        print()

