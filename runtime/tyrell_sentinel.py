#!/usr/bin/env python3
"""
tyrell_sentinal.py
Le'Veon — Tyrell Sentinel (Runtime Safety + Drift Guard)

Purpose
-------
A small, deterministic sentinel that sits *around* the kernel loop and
provides:

- Dream clause scoring (lightweight heuristic)
- Echo tightening feedback (reduce repetition / runaway)
- Glyph evolution weighting (nudge weights based on stability)
- Basin → language influence (adjust style bias based on "basin")
- Optimization → EOS governor (cap verbosity / iteration pressure)
- Full 100-turn narration logging (JSON export, turn-by-turn)

This is designed to be:
- Offline
- Deterministic (no randomness)
- Termux-friendly
- Drop-in around kernel_loop_v0.8_lattice_integrated.KernelLoop

Integration
-----------
In your loop:
    from tyrell_sentinal import TyrellSentinel, SentinelConfig
    sent = TyrellSentinel(SentinelConfig())

Then in step():
    out = kernel.step(user_id, text)
    out2 = sent.postprocess(user_id, text, out, lattice_snapshot=ks.lattice.last_derived)
    return out2

If you want narration logs for 100-turn sims:
    sent.begin_run(user_id, run_tag="lattice_100")
    for i in range(100): ...
    sent.end_run(user_id)

Notes
-----
- "Sentinal" spelling kept as requested (matches your filename).
"""

from __future__ import annotations

import json
import os
import time
import hashlib
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional, Tuple


# ----------------------------
# Utilities
# ----------------------------

def now() -> float:
    return time.time()

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        x = float(x)
    except Exception:
        x = lo
    return max(lo, min(hi, x))

def soft_lower(s: str) -> str:
    return (s or "").lower()

def safe_mkdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def safe_load_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def safe_write_json(path: str, data: Any) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def sha1(text: str) -> str:
    return hashlib.sha1((text or "").encode("utf-8")).hexdigest()


# ----------------------------
# Config
# ----------------------------

@dataclass
class SentinelConfig:
    # storage
    state_dir: str = "leveon_state"
    log_dir: str = "leveon_logs"
    filename_state: str = "tyrell_sentinal_state.json"

    # EOS governor caps
    max_sentences: int = 3
    max_chars: int = 650

    # echo tightening sensitivity
    repetition_threshold: float = 0.62     # higher => more tolerant
    tighten_strength: float = 0.22         # how hard to compress if repetitive

    # dream clause scoring
    dream_trigger_words: Tuple[str, ...] = (
        "dream", "sleep", "night", "wake", "woke", "vision", "symbol", "glyph"
    )
    grief_words: Tuple[str, ...] = (
        "dad", "father", "jemma", "gemma", "loss", "grief", "alone", "miss"
    )
    build_words: Tuple[str, ...] = (
        "kernel", "module", "build", "termux", "flask", "optimize", "pipeline", "api"
    )

    # basin rules
    # (these are just labels; you can expand later)
    basins: Tuple[str, ...] = ("calm", "build", "dream", "grief", "heat")

    # glyph evolution weighting (simple)
    enable_glyph_weighting: bool = True
    glyph_weight_lr: float = 0.03

    # narration logging
    enable_narration_log: bool = True


# ----------------------------
# State
# ----------------------------

@dataclass
class GlyphWeights:
    weights: Dict[str, float] = field(default_factory=dict)

    def nudge(self, glyph: str, delta: float) -> None:
        g = (glyph or "").strip()
        if not g:
            return
        self.weights[g] = clamp(self.weights.get(g, 0.0) + delta, 0.0, 1.0)

@dataclass
class TyrellState:
    user_id: str = "default"
    run_active: bool = False
    run_tag: str = ""
    run_started_ts: float = 0.0
    run_turns: int = 0

    # last outputs for repetition checks
    last_outputs: List[str] = field(default_factory=list)

    # glyph weights (optional)
    glyph_weights: GlyphWeights = field(default_factory=GlyphWeights)

    # last basin
    basin: str = "calm"

    # bookkeeping
    last_hash: str = ""


# ----------------------------
# Sentinel
# ----------------------------

class TyrellSentinel:
    def __init__(self, cfg: Optional[SentinelConfig] = None):
        self.cfg = cfg or SentinelConfig()
        safe_mkdir(self.cfg.state_dir)
        safe_mkdir(self.cfg.log_dir)
        self._states: Dict[str, TyrellState] = {}

    # ------------------------
    # Public: run lifecycle
    # ------------------------

    def begin_run(self, user_id: str, run_tag: str = "run") -> None:
        st = self._load(user_id)
        st.run_active = True
        st.run_tag = run_tag
        st.run_started_ts = now()
        st.run_turns = 0
        self._save(user_id)

    def end_run(self, user_id: str) -> None:
        st = self._load(user_id)
        st.run_active = False
        self._save(user_id)

    # ------------------------
    # Public: main hook
    # ------------------------

    def postprocess(
        self,
        user_id: str,
        input_text: str,
        output_text: str,
        *,
        glyphs: Optional[List[str]] = None,
        lattice_snapshot: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Take kernel output, apply:
        - basin detection -> style bias
        - repetition tightening
        - EOS caps (sentences/chars)
        - narration log export (JSON)

        Returns modified output_text.
        """
        st = self._load(user_id)

        # de-dupe: if same input/output repeats exactly, skip extra logging
        h = sha1((input_text or "") + "\n" + (output_text or ""))
        if h == st.last_hash:
            return output_text
        st.last_hash = h

        basin = self._detect_basin(input_text, output_text, lattice_snapshot=lattice_snapshot)
        st.basin = basin

        dream_score = self._dream_clause_score(input_text, output_text, basin)
        rep = self._repetition_score(st.last_outputs, output_text)

        # echo tightening feedback
        tightened = output_text
        tighten_applied = False
        if rep >= self.cfg.repetition_threshold:
            tightened = self._tighten(tightened, strength=self.cfg.tighten_strength)
            tighten_applied = True

        # EOS governor (caps)
        governed = self._eos_govern(tightened)

        # glyph evolution weighting (optional)
        if self.cfg.enable_glyph_weighting and glyphs:
            self._update_glyph_weights(st, glyphs, basin=basin, dream_score=dream_score, repetition=rep)

        # store history for next repetition checks
        st.last_outputs.append((governed or "")[:500])
        st.last_outputs = st.last_outputs[-12:]

        # narration logging
        if self.cfg.enable_narration_log:
            self._log_turn(
                user_id=user_id,
                st=st,
                input_text=input_text,
                raw_output=output_text,
                final_output=governed,
                basin=basin,
                dream_score=dream_score,
                repetition=rep,
                tighten_applied=tighten_applied,
                glyphs=glyphs or [],
                lattice_snapshot=lattice_snapshot or {},
            )

        self._save(user_id)
        return governed

    # ------------------------
    # Basin detection
    # ------------------------

    def _detect_basin(
        self,
        input_text: str,
        output_text: str,
        *,
        lattice_snapshot: Optional[Dict[str, Any]] = None,
    ) -> str:
        t = soft_lower(input_text) + "\n" + soft_lower(output_text)

        # lattice influence (if present)
        coh = None
        risk = None
        if isinstance(lattice_snapshot, dict):
            try:
                coh = float(lattice_snapshot.get("coherence", 0.0))
                risk = float(lattice_snapshot.get("risk", 0.0))
            except Exception:
                coh, risk = None, None

        # keyword basins
        if any(w in t for w in self.cfg.grief_words):
            return "grief"
        if any(w in t for w in self.cfg.dream_trigger_words):
            return "dream"
        if any(w in t for w in self.cfg.build_words):
            return "build"
        if any(w in t for w in ("angry", "furious", "hate", "fuck", "bullshit")):
            return "heat"

        # lattice-derived fallback
        if coh is not None and risk is not None:
            if risk >= 0.55:
                return "heat"
            if coh >= 0.78:
                return "calm"

        return "calm"

    # ------------------------
    # Dream clause scoring
    # ------------------------

    def _dream_clause_score(self, input_text: str, output_text: str, basin: str) -> float:
        t = soft_lower(input_text) + " " + soft_lower(output_text)

        hit_dream = sum(1 for w in self.cfg.dream_trigger_words if w in t)
        hit_grief = sum(1 for w in self.cfg.grief_words if w in t)

        # small deterministic heuristic:
        base = 0.10
        base += 0.12 * min(hit_dream, 3)
        base += 0.08 * min(hit_grief, 3)

        if basin == "dream":
            base += 0.10
        if basin == "grief":
            base += 0.06

        # punctuation / tone as proxy
        base += 0.02 * min((output_text or "").count("…") + (output_text or "").count("..."), 3)
        base += 0.01 * min((output_text or "").count("—"), 4)

        return clamp(base)

    # ------------------------
    # Echo tightening
    # ------------------------

    def _repetition_score(self, prev_outputs: List[str], cur: str) -> float:
        """
        Returns similarity proxy in [0..1].
        High means the output is repeating itself.
        """
        c = soft_lower(cur).strip()
        if not c or not prev_outputs:
            return 0.0

        # Compare against last 5 outputs
        prev = [soft_lower(x).strip() for x in prev_outputs[-5:] if x]
        if not prev:
            return 0.0

        # Jaccard-like word overlap
        cw = set(c.split())
        if not cw:
            return 0.0

        best = 0.0
        for p in prev:
            pw = set(p.split())
            if not pw:
                continue
            inter = len(cw & pw)
            union = len(cw | pw)
            score = inter / union if union else 0.0
            if score > best:
                best = score

        return clamp(best)

    def _tighten(self, text: str, strength: float = 0.2) -> str:
        """
        Tighten by:
        - removing duplicate sentences
        - trimming clause tails
        - keeping strongest first 2–3 sentences
        """
        strength = clamp(strength, 0.0, 0.6)
        sents = self._split_sentences(text)

        # de-dup sentences by normalized form
        seen = set()
        uniq: List[str] = []
        for s in sents:
            key = " ".join(soft_lower(s).split())
            if key in seen:
                continue
            seen.add(key)
            uniq.append(s)

        # keep fewer sentences as strength increases
        keep_n = 3 if strength < 0.25 else 2
        uniq = uniq[:keep_n] if uniq else []

        tightened = " ".join(uniq).strip()
        if not tightened:
            tightened = (text or "").strip()

        # trim very long lines
        if len(tightened) > int(self.cfg.max_chars * (1.0 - 0.25 * strength)):
            tightened = tightened[: int(self.cfg.max_chars * (1.0 - 0.25 * strength))].rstrip()
            if tightened and tightened[-1] not in ".!?":
                tightened += "."

        return tightened

    def _split_sentences(self, text: str) -> List[str]:
        t = (text or "").strip()
        if not t:
            return []
        out: List[str] = []
        buf: List[str] = []
        for ch in t:
            buf.append(ch)
            if ch in ".!?":
                s = "".join(buf).strip()
                if s:
                    out.append(s)
                buf = []
        tail = "".join(buf).strip()
        if tail:
            out.append(tail)
        return out

    # ------------------------
    # EOS governor
    # ------------------------

    def _eos_govern(self, text: str) -> str:
        """
        Hard caps for Termux friendliness:
        - sentence cap
        - char cap
        """
        t = (text or "").strip()
        if not t:
            return ""

        # sentence cap
        sents = self._split_sentences(t)
        if len(sents) > self.cfg.max_sentences:
            t = " ".join(sents[: self.cfg.max_sentences]).strip()

        # char cap
        if len(t) > self.cfg.max_chars:
            t = t[: self.cfg.max_chars].rstrip()
            if t and t[-1] not in ".!?":
                t += "."

        return t

    # ------------------------
    # Glyph weighting
    # ------------------------

    def _update_glyph_weights(
        self,
        st: TyrellState,
        glyphs: List[str],
        *,
        basin: str,
        dream_score: float,
        repetition: float,
    ) -> None:
        """
        Simple deterministic weighting:
        - If stable/calm/build and low repetition -> strengthen glyphs slightly
        - If repetition high -> weaken repeated glyphs slightly
        - If dream_score high -> nudge dream glyphs up (🫀 🔁 🕯️ 🌑 etc if present)
        """
        lr = clamp(self.cfg.glyph_weight_lr, 0.0, 0.15)

        # stability proxy
        stable = (basin in ("calm", "build")) and (repetition < self.cfg.repetition_threshold)

        for g in glyphs[:10]:
            if stable:
                st.glyph_weights.nudge(g, +lr * 0.7)

            if repetition >= self.cfg.repetition_threshold:
                st.glyph_weights.nudge(g, -lr * 0.6)

        if dream_score >= 0.45:
            for g in glyphs[:10]:
                if g in ("🫀", "🔁", "🕯️", "🌑", "🧬", "🪞"):
                    st.glyph_weights.nudge(g, +lr)

    # ------------------------
    # Narration logging
    # ------------------------

    def _log_turn(
        self,
        *,
        user_id: str,
        st: TyrellState,
        input_text: str,
        raw_output: str,
        final_output: str,
        basin: str,
        dream_score: float,
        repetition: float,
        tighten_applied: bool,
        glyphs: List[str],
        lattice_snapshot: Dict[str, Any],
    ) -> None:
        st.run_turns += 1

        record = {
            "ts": now(),
            "user_id": user_id,
            "run": {
                "active": st.run_active,
                "tag": st.run_tag,
                "started_ts": st.run_started_ts,
                "turn_index": st.run_turns,
            },
            "basin": basin,
            "scores": {
                "dream_clause": round(dream_score, 3),
                "repetition": round(repetition, 3),
            },
            "actions": {
                "echo_tightened": bool(tighten_applied),
                "eos_capped": (final_output != raw_output),
            },
            "input": input_text,
            "output_raw": raw_output,
            "output_final": final_output,
            "glyphs": glyphs,
            "lattice": lattice_snapshot,
            "glyph_weights": dict(st.glyph_weights.weights),
        }

        # write per-user log file, append list (safe + simple)
        path = os.path.join(self.cfg.log_dir, f"{user_id}_narration.json")
        log = safe_load_json(path, default=[])
        if not isinstance(log, list):
            log = []
        log.append(record)

        # keep logs bounded for mobile
        if len(log) > 1500:
            log = log[-1200:]

        safe_write_json(path, log)

    # ------------------------
    # Persistence
    # ------------------------

    def _state_path(self, user_id: str) -> str:
        return os.path.join(self.cfg.state_dir, f"{user_id}_{self.cfg.filename_state}")

    def _load(self, user_id: str) -> TyrellState:
        if user_id in self._states:
            return self._states[user_id]

        path = self._state_path(user_id)
        raw = safe_load_json(path, default=None)
        if isinstance(raw, dict):
            try:
                st = TyrellState(
                    user_id=user_id,
                    run_active=bool(raw.get("run_active", False)),
                    run_tag=str(raw.get("run_tag", "")),
                    run_started_ts=float(raw.get("run_started_ts", 0.0)),
                    run_turns=int(raw.get("run_turns", 0)),
                    last_outputs=list(raw.get("last_outputs", []))[-12:],
                    basin=str(raw.get("basin", "calm")),
                    last_hash=str(raw.get("last_hash", "")),
                    glyph_weights=GlyphWeights(weights=dict(raw.get("glyph_weights", {}) or {})),
                )
                self._states[user_id] = st
                return st
            except Exception:
                pass

        st = TyrellState(user_id=user_id)
        self._states[user_id] = st
        return st

    def _save(self, user_id: str) -> None:
        st = self._load(user_id)
        path = self._state_path(user_id)
        payload = {
            "user_id": st.user_id,
            "run_active": st.run_active,
            "run_tag": st.run_tag,
            "run_started_ts": st.run_started_ts,
            "run_turns": st.run_turns,
            "last_outputs": st.last_outputs[-12:],
            "basin": st.basin,
            "last_hash": st.last_hash,
            "glyph_weights": dict(st.glyph_weights.weights),
        }
        safe_write_json(path, payload)


# ----------------------------
# Minimal local test
# ----------------------------

if __name__ == "__main__":
    sent = TyrellSentinel(SentinelConfig())
    user = "john_mitchell"

    sent.begin_run(user, run_tag="quick_test")

    out = "The kernel aligns. Structure can be extended. Structure can be extended. Structure can be extended."
    final = sent.postprocess(
        user,
        "build the kernel loop in termux",
        out,
        glyphs=["✴️", "🫀", "🔁"],
        lattice_snapshot={"coherence": 0.82, "risk": 0.18},
    )

    print("\nRAW:\n", out)
    print("\nFINAL:\n", final)
    print("\nLogged to:", os.path.join(sent.cfg.log_dir, f"{user}_narration.json"))

    sent.end_run(user)

