from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import time
import uuid
import re


def _clean(x: Any) -> str:
    return str(x or "").strip()


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9_']+", _clean(text).lower())


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _unique(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        item = _clean(item)
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


@dataclass
class UserProfile:
    user_id: str
    user_name: str
    created_at: float
    updated_at: float
    aliases: List[str] = field(default_factory=list)
    dominant_domains: Dict[str, float] = field(default_factory=dict)
    dominant_emotions: Dict[str, float] = field(default_factory=dict)
    shape_centroid: Dict[str, float] = field(default_factory=lambda: {
        "flow": 0.5, "boundary": 0.5, "memory": 0.5, "novelty": 0.5, "confidence": 0.5
    })
    hotspot_families: Dict[str, float] = field(default_factory=dict)
    sequence_families: Dict[str, float] = field(default_factory=dict)
    recent_patterns: List[Dict[str, Any]] = field(default_factory=list)


class UserPatternLattice:
    """
    Personal pattern memory + shared cross-user lattice.
    Experimental prototype:
    - per-user profile store
    - global sequence store
    - cross-user connections by pattern similarity
    """

    def __init__(
        self,
        user_db_path: str = "memory/user_profiles.json",
        sequence_db_path: str = "memory/user_sequence_packets.jsonl",
        connection_db_path: str = "memory/user_connections.jsonl",
    ) -> None:
        self.user_db_path = Path(user_db_path)
        self.sequence_db_path = Path(sequence_db_path)
        self.connection_db_path = Path(connection_db_path)

        self.user_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.sequence_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection_db_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.user_db_path.exists():
            self.user_db_path.write_text("{}", encoding="utf-8")

    # ---------------------------------------------------------
    # User identity
    # ---------------------------------------------------------
    def resolve_user(self, user_name: str) -> Dict[str, Any]:
        user_name = _clean(user_name) or "unknown"
        db = self._read_user_db()

        for user_id, payload in db.items():
            if payload.get("user_name", "").lower() == user_name.lower():
                payload["updated_at"] = time.time()
                db[user_id] = payload
                self._write_user_db(db)
                return payload

            aliases = [str(x).lower() for x in (payload.get("aliases") or [])]
            if user_name.lower() in aliases:
                payload["updated_at"] = time.time()
                db[user_id] = payload
                self._write_user_db(db)
                return payload

        user_id = f"user_{uuid.uuid4().hex[:12]}"
        profile = asdict(UserProfile(
            user_id=user_id,
            user_name=user_name,
            created_at=time.time(),
            updated_at=time.time(),
        ))
        db[user_id] = profile
        self._write_user_db(db)
        return profile

    def observe_user_sequence(
        self,
        *,
        user_name: str,
        prompt_text: str,
        reply_text: str,
        domain: str = "",
        logical_coherence: float = 0.5,
        emotional_fidelity: float = 0.5,
        hotspot_score: float = 0.5,
        sequence_family: str = "",
        relation_chain: Optional[List[str]] = None,
        shape_signature: Optional[Dict[str, float]] = None,
        emotion_weights: Optional[Dict[str, float]] = None,
        hotspot_hint: str = "",
    ) -> Dict[str, Any]:
        profile = self.resolve_user(user_name)
        relation_chain = relation_chain or []
        shape_signature = shape_signature or {}
        emotion_weights = emotion_weights or {}

        packet = {
            "packet_id": f"up_{uuid.uuid4().hex[:12]}",
            "timestamp": time.time(),
            "user_id": profile["user_id"],
            "user_name": profile["user_name"],
            "prompt_text": _clean(prompt_text),
            "reply_text": _clean(reply_text),
            "domain": _clean(domain),
            "logical_coherence": round(_clamp(logical_coherence), 4),
            "emotional_fidelity": round(_clamp(emotional_fidelity), 4),
            "hotspot_score": round(_clamp(hotspot_score), 4),
            "sequence_family": _clean(sequence_family),
            "relation_chain": _unique(relation_chain),
            "shape_signature": {
                "flow": float(shape_signature.get("flow", 0.5)),
                "boundary": float(shape_signature.get("boundary", 0.5)),
                "memory": float(shape_signature.get("memory", 0.5)),
                "novelty": float(shape_signature.get("novelty", 0.5)),
                "confidence": float(shape_signature.get("confidence", 0.5)),
            },
            "emotion_weights": dict(emotion_weights),
            "hotspot_hint": _clean(hotspot_hint),
        }

        self._append_jsonl(self.sequence_db_path, packet)
        self._update_profile_from_packet(profile["user_id"], packet)
        self._refresh_connections(profile["user_id"])
        return packet

    def get_user_patterns(self, user_name: str) -> Dict[str, Any]:
        profile = self.resolve_user(user_name)
        return profile

    def correlate_user_prompt(self, user_name: str, prompt_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        profile = self.resolve_user(user_name)
        packets = self._read_jsonl(self.sequence_db_path)

        target_keywords = set(_tokens(prompt_text))
        hits: List[Tuple[float, Dict[str, Any]]] = []

        for packet in packets:
            if packet.get("user_id") != profile["user_id"]:
                continue

            prompt_keywords = set(_tokens(packet.get("prompt_text", "")))
            reply_keywords = set(_tokens(packet.get("reply_text", "")))
            overlap = 0.0
            if target_keywords:
                overlap = max(
                    len(target_keywords & prompt_keywords) / max(1, min(len(target_keywords), len(prompt_keywords) or 1)),
                    len(target_keywords & reply_keywords) / max(1, min(len(target_keywords), len(reply_keywords) or 1)),
                )

            shape_score = self._shape_similarity(
                self._quick_shape(prompt_text),
                packet.get("shape_signature", {}) or {},
            )

            score = round(_clamp((overlap * 0.55) + (shape_score * 0.45)), 4)
            if score > 0.18:
                row = dict(packet)
                row["correlation_score"] = score
                hits.append((score, row))

        hits.sort(key=lambda x: x[0], reverse=True)
        return [row for _, row in hits[:limit]]

    def get_cross_user_connections(self, user_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        profile = self.resolve_user(user_name)
        rows = self._read_jsonl(self.connection_db_path)
        related = []
        for row in rows:
            if row.get("user_a") == profile["user_id"] or row.get("user_b") == profile["user_id"]:
                related.append(row)
        related.sort(key=lambda r: float(r.get("connection_score", 0.0)), reverse=True)
        return related[:limit]

    # ---------------------------------------------------------
    # Internal updates
    # ---------------------------------------------------------
    def _update_profile_from_packet(self, user_id: str, packet: Dict[str, Any]) -> None:
        db = self._read_user_db()
        profile = dict(db[user_id])

        domain = _clean(packet.get("domain"))
        if domain:
            dd = dict(profile.get("dominant_domains") or {})
            dd[domain] = round(float(dd.get(domain, 0.0)) + 1.0, 4)
            profile["dominant_domains"] = dd

        emo = dict(profile.get("dominant_emotions") or {})
        for k, v in (packet.get("emotion_weights") or {}).items():
            emo[k] = round(float(emo.get(k, 0.0)) + float(v), 4)
        profile["dominant_emotions"] = emo

        sf = dict(profile.get("sequence_families") or {})
        seq_family = _clean(packet.get("sequence_family"))
        if seq_family:
            sf[seq_family] = round(float(sf.get(seq_family, 0.0)) + 1.0, 4)
            profile["sequence_families"] = sf

        hf = dict(profile.get("hotspot_families") or {})
        hotspot = _clean(packet.get("hotspot_hint"))
        if hotspot:
            hf[hotspot] = round(float(hf.get(hotspot, 0.0)) + float(packet.get("hotspot_score", 0.0)), 4)
            profile["hotspot_families"] = hf

        centroid = dict(profile.get("shape_centroid") or {})
        cur = dict(packet.get("shape_signature") or {})
        alpha = 0.22
        for key in ("flow", "boundary", "memory", "novelty", "confidence"):
            prev_val = float(centroid.get(key, 0.5))
            cur_val = float(cur.get(key, 0.5))
            centroid[key] = round((1.0 - alpha) * prev_val + alpha * cur_val, 4)
        profile["shape_centroid"] = centroid

        recent = list(profile.get("recent_patterns") or [])
        recent.append({
            "packet_id": packet.get("packet_id"),
            "domain": packet.get("domain"),
            "sequence_family": packet.get("sequence_family"),
            "relation_chain": packet.get("relation_chain"),
            "logical_coherence": packet.get("logical_coherence"),
            "emotional_fidelity": packet.get("emotional_fidelity"),
            "hotspot_score": packet.get("hotspot_score"),
        })
        profile["recent_patterns"] = recent[-20:]

        profile["updated_at"] = time.time()
        db[user_id] = profile
        self._write_user_db(db)

    def _refresh_connections(self, user_id: str) -> None:
        db = self._read_user_db()
        if user_id not in db:
            return

        this_profile = db[user_id]
        for other_id, other_profile in db.items():
            if other_id == user_id:
                continue

            score = self._profile_similarity(this_profile, other_profile)
            if score < 0.18:
                continue

            row = {
                "connection_id": f"conn_{uuid.uuid4().hex[:12]}",
                "timestamp": time.time(),
                "user_a": user_id,
                "user_b": other_id,
                "user_a_name": this_profile.get("user_name"),
                "user_b_name": other_profile.get("user_name"),
                "connection_score": round(score, 4),
                "shared_domains": self._shared_keys(
                    this_profile.get("dominant_domains", {}),
                    other_profile.get("dominant_domains", {}),
                ),
                "shared_emotions": self._shared_keys(
                    this_profile.get("dominant_emotions", {}),
                    other_profile.get("dominant_emotions", {}),
                ),
                "shared_sequence_families": self._shared_keys(
                    this_profile.get("sequence_families", {}),
                    other_profile.get("sequence_families", {}),
                ),
            }
            self._append_jsonl(self.connection_db_path, row)

    # ---------------------------------------------------------
    # Similarity helpers
    # ---------------------------------------------------------
    def _profile_similarity(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        dom = self._weighted_overlap(a.get("dominant_domains", {}), b.get("dominant_domains", {}))
        emo = self._weighted_overlap(a.get("dominant_emotions", {}), b.get("dominant_emotions", {}))
        seq = self._weighted_overlap(a.get("sequence_families", {}), b.get("sequence_families", {}))
        shape = self._shape_similarity(a.get("shape_centroid", {}), b.get("shape_centroid", {}))
        return _clamp((dom * 0.24) + (emo * 0.28) + (seq * 0.24) + (shape * 0.24))

    def _shape_similarity(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        if not a or not b:
            return 0.0
        keys = ("flow", "boundary", "memory", "novelty", "confidence")
        dist = 0.0
        for k in keys:
            dist += abs(float(a.get(k, 0.5)) - float(b.get(k, 0.5)))
        dist /= len(keys)
        return round(_clamp(1.0 - dist), 4)

    def _weighted_overlap(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        if not a or not b:
            return 0.0
        shared = set(a.keys()) & set(b.keys())
        if not shared:
            return 0.0
        vals = []
        for k in shared:
            vals.append(min(float(a.get(k, 0.0)), float(b.get(k, 0.0))))
        return round(_clamp(sum(vals) / max(1.0, sum(float(v) for v in a.values()) / max(1, len(a)))), 4)

    def _shared_keys(self, a: Dict[str, Any], b: Dict[str, Any]) -> List[str]:
        return sorted(list(set(a.keys()) & set(b.keys())))[:20]

    def _quick_shape(self, text: str) -> Dict[str, float]:
        lower = _clean(text).lower()
        flow = 0.5
        boundary = 0.5
        memory = 0.5
        novelty = 0.5
        confidence = 0.5

        if any(x in lower for x in ["why", "how", "what", "explain"]):
            flow += 0.08
            novelty += 0.05
        if any(x in lower for x in ["grief", "pain", "miss", "wife", "dad", "mom", "hurt"]):
            memory += 0.16
            boundary += 0.10
        if any(x in lower for x in ["hi", "hello", "hey"]):
            novelty -= 0.08
            confidence += 0.04

        return {
            "flow": _clamp(flow),
            "boundary": _clamp(boundary),
            "memory": _clamp(memory),
            "novelty": _clamp(novelty),
            "confidence": _clamp(confidence),
        }

    # ---------------------------------------------------------
    # IO
    # ---------------------------------------------------------
    def _read_user_db(self) -> Dict[str, Any]:
        try:
            return json.loads(self.user_db_path.read_text(encoding="utf-8") or "{}")
        except Exception:
            return {}

    def _write_user_db(self, db: Dict[str, Any]) -> None:
        self.user_db_path.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

    def _append_jsonl(self, path: Path, payload: Dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _read_jsonl(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
        return rows


__all__ = ["UserPatternLattice"]

