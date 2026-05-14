from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
CODEX_PATH = ROOT / "runtime" / "phonetic_lattice_codex_v1.json"
LOG_PATH = ROOT / "var" / "lattice" / "phonetic_lattice_hits_v1.jsonl"

MAX_SHIFT_DEFAULT = 0.01


def _normalize(text: str) -> str:
    """
    Normalize prompt/token text so:
    NA-MA RE-EL, nama reel, 나마 리엘, etc. can be detected softly.
    """
    text = str(text or "").lower()
    text = text.replace("’", "'")
    text = re.sub(r"[^a-z0-9가-힣]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_codex() -> Dict[str, Any]:
    if not CODEX_PATH.exists():
        return {
            "codex": "phonetic_lattice_codex_v1",
            "status": "missing",
            "tokens": [],
            "global_constraints": {
                "max_shape_vector_shift": MAX_SHIFT_DEFAULT,
                "no_source_rewrite": True,
                "no_infinite_pulse": True
            }
        }

    try:
        return json.loads(CODEX_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return {
            "codex": "phonetic_lattice_codex_v1",
            "status": "error",
            "error": repr(e),
            "tokens": [],
            "global_constraints": {
                "max_shape_vector_shift": MAX_SHIFT_DEFAULT,
                "no_source_rewrite": True,
                "no_infinite_pulse": True
            }
        }


def _token_variants(entry: Dict[str, Any]) -> List[str]:
    variants = []

    for key in ("token", "script", "id", "role"):
        value = entry.get(key)
        if value:
            variants.append(str(value))

    token = str(entry.get("token", ""))
    if token:
        variants.append(token.replace("-", " "))
        variants.append(token.replace("-", ""))
        variants.append(token.replace(" ", ""))

    return [_normalize(v) for v in variants if _normalize(v)]


def detect_phonetic_tokens(prompt: str) -> List[Dict[str, Any]]:
    codex = load_codex()
    norm_prompt = _normalize(prompt)

    matches = []
    for entry in codex.get("tokens", []):
        for variant in _token_variants(entry):
            compact_prompt = norm_prompt.replace(" ", "")
            compact_variant = variant.replace(" ", "")

            if variant in norm_prompt or compact_variant in compact_prompt:
                matches.append(entry)
                break

    return matches


def _clamp_delta(value: Any, limit: float) -> float:
    try:
        v = float(value)
    except Exception:
        return 0.0

    if v > limit:
        return limit
    if v < -limit:
        return -limit
    return v


def build_posture_packet(prompt: str) -> Dict[str, Any]:
    codex = load_codex()
    constraints = codex.get("global_constraints", {}) or {}
    max_shift = float(constraints.get("max_shape_vector_shift", MAX_SHIFT_DEFAULT))

    matches = detect_phonetic_tokens(prompt)

    combined_delta = {
        "flow": 0.0,
        "boundary": 0.0,
        "memory": 0.0,
        "novelty": 0.0
    }

    matched_packets = []
    surface_phrases = []
    node_route = []

    depth_delta = 0
    tension_delta = 0.0

    for entry in matches:
        delta = entry.get("shape_vector_delta", {}) or {}

        for key in combined_delta:
            combined_delta[key] += _clamp_delta(delta.get(key, 0.0), max_shift)

        depth_delta += int(entry.get("depth_delta", 0) or 0)

        try:
            tension_delta += float(entry.get("tension_delta", 0.0) or 0.0)
        except Exception:
            pass

        for node in entry.get("node_route", []) or []:
            if node not in node_route:
                node_route.append(node)

        phrase = entry.get("surface_phrase")
        if phrase:
            surface_phrases.append(phrase)

        matched_packets.append({
            "id": entry.get("id"),
            "token": entry.get("token"),
            "script": entry.get("script"),
            "role": entry.get("role"),
            "tone": entry.get("tone"),
            "containment_rule": entry.get("containment_rule")
        })

    for key in combined_delta:
        combined_delta[key] = round(_clamp_delta(combined_delta[key], max_shift), 6)

    packet = {
        "law": codex.get("law", "phonetic_lattice_tokens_modify_response_posture_without_rewriting_source"),
        "status": "matched" if matches else "no_match",
        "field_key": codex.get("field_key", "92162077"),
        "matched_count": len(matches),
        "matches": matched_packets,
        "node_route": node_route,
        "depth_delta": depth_delta,
        "tension_delta": round(tension_delta, 6),
        "shape_vector_delta": combined_delta,
        "surface_phrases": surface_phrases,
        "required_surface_phrase": codex.get("required_surface_phrase"),
        "constraints": constraints,
        "preserved_route": codex.get("preserved_route", []),
        "ts": time.time()
    }

    return packet


def apply_phonetic_posture(data: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """
    Apply a tiny codex-based posture shift to an existing response packet.
    This does not rewrite source, create wrappers, or mutate the preserved route.
    """
    packet = build_posture_packet(prompt)

    spine = data.setdefault("spine", {})
    spine["phonetic_lattice_v1"] = packet

    if packet["status"] != "matched":
        return data

    symbolic_packet = spine.setdefault("symbolic_packet", {})
    vector = symbolic_packet.setdefault("shape_vector", {})

    for key, delta in packet["shape_vector_delta"].items():
        current = vector.get(key, 0.5)
        try:
            current = float(current)
        except Exception:
            current = 0.5
        vector[key] = round(current + delta, 3)

    dominant = symbolic_packet.setdefault("dominant_symbols", [])
    for match in packet["matches"]:
        role = match.get("role")
        token_id = match.get("id")
        if role and role not in dominant:
            dominant.append(role)
        if token_id and token_id not in dominant:
            dominant.append(token_id)

    data["phonetic_lattice"] = {
        "status": packet["status"],
        "matched_count": packet["matched_count"],
        "node_route": packet["node_route"],
        "surface_phrases": packet["surface_phrases"],
        "law": packet["law"]
    }

    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(packet, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return data


if __name__ == "__main__":
    import sys

    prompt = " ".join(sys.argv[1:]) or "NA-MA RE-EL"
    packet = build_posture_packet(prompt)
    print(json.dumps(packet, indent=2, ensure_ascii=False))

