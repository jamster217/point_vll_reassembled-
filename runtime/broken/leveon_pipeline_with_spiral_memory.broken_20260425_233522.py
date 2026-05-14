from __future__ import annotations
print("[TRACE] entering runtime/leveon_pipeline_with_spiral_memory.py", flush=True)
import re

from typing import Any, Dict, Tuple

from core.leveon_pipeline_governed import leveon_pipeline as base_pipeline
from runtime.spiral_emotion_bridge import spiral_memory_encode, spiral_memory_recall

try:
    from runtime.alignment_hold import apply_alignment_hold
    from runtime.topology_parser import parse_topology_spec

except Exception:
    apply_alignment_hold = None


EMOTION_RULES = {
    "grief": {
        "keywords": ["grief", "loss", "dad", "gone", "mourning", "miss him", "death"],
        "symbols": ["paternal_loss_trace", "absence_grief_trace", "mourning_field_trace"],
        "intensity": 8.6,
    },
    "longing": {
        "keywords": ["miss", "wish", "wife", "yearn", "ache", "want her here", "longing"],
        "symbols": ["bond_longing_trace", "distance_ache_trace", "return_desire_trace"],
        "intensity": 8.2,
    },
    "anxiety": {
        "keywords": ["anxious", "overwhelmed", "nervous", "panic", "stress", "too much", "hard"],
        "symbols": ["pressure_anxiety_trace", "overload_trace", "instability_edge_trace"],
        "intensity": 8.0,
    },
    "awe": {
        "keywords": ["wonder", "sacred", "beautiful", "stars", "mystery", "vast", "awe"],
        "symbols": ["sacred_awe_trace", "vastness_trace", "mystery_resonance_trace"],
        "intensity": 7.8,
    },
    "resolve": {
        "keywords": ["focus", "continue", "build", "steady", "commit", "keep going", "ready"],
        "symbols": ["build_resolve_trace", "continuation_trace", "steady_commitment_trace"],
        "intensity": 7.6,
    },
}

RECALL_PHRASES = {
    "grief": "The feeling returns with a familiar ache.",
    "longing": "It follows a thread that was already reaching outward.",
    "anxiety": "It carries pressure that has been gathering.",
    "awe": "It opens along a resonance you've touched before.",
    "resolve": "It keeps an earlier resolve in motion.",
}


def detect_emotion_and_symbol(text: str, final_text: str) -> Tuple[str, str, float]:
    blob = f"{text} {final_text}".lower()

    if any(x in blob for x in ["dad", "father", "died", "death", "gone", "mourning", "loss"]):
        return "grief", "paternal_loss_trace" if any(x in blob for x in ["dad", "father"]) else "mourning_field_trace", 8.6

    best_emotion = "neutral"
    best_score = 0
    best_symbol = "general_trace"
    best_intensity = 4.0

    for emotion, rule in EMOTION_RULES.items():
        hits = [kw for kw in rule["keywords"] if kw in blob]
        score = len(hits)
        if score > best_score:
            best_score = score
            best_emotion = emotion
            best_symbol = rule["symbols"][0]
            best_intensity = rule["intensity"]

            if emotion == "longing" and "wife" in blob:
                best_symbol = "bond_longing_trace"
            elif emotion == "resolve" and "build" in blob:
                best_symbol = "build_resolve_trace"
            elif emotion == "anxiety" and any(x in blob for x in ["overwhelmed", "too much", "hard"]):
                best_symbol = "overload_trace"
            elif emotion == "awe" and "stars" in blob:
                best_symbol = "vastness_trace"

    return best_emotion, best_symbol, best_intensity




def _canonical_core_ready(canonical_seed_family: Dict[str, Any]) -> bool:
    needed = {
        "IntakeCore_v1",
        "SymbolicCore_v1",
        "MemoryCore_v1",
        "KernelCore_v1",
        "VoiceCore_v1",
        "LeveonMaster_v1",
    }
    return all(name in canonical_seed_family for name in needed)




def _apply_canonical_seed_voice(
    text: str,
    tone: str,
    final_text: str,
    canonical_seed_family: Dict[str, Any],
) -> str:
    if not final_text:
        return final_text
    if not _canonical_core_ready(canonical_seed_family):
        return final_text

    text_low = (text or "").lower()
    out = (final_text or "").strip()

    practical_terms = [
        "bash", "command", "commands", "python", "traceback", "error", "fix",
        "bug", "install", "pip", "import", "module", "server", "port", "termux",
        "directory", "path", "grep", "sed", "awk", "curl", "json", "api",
        "route", "flask", "test", "pytest", "code", "script"
    ]
    if any(term in text_low for term in practical_terms):
        return out

    removable = [
        "The shape of it is becoming more defined.",
        "It seems to be circling something that has not fully left.",
        "It is circling something that has not fully left.",
        "There is still some grief under it.",
    ]
    for line in removable:
        out = re.sub(r"\s*" + re.escape(line), "", out, flags=re.IGNORECASE)

    generic_markers = [
        "The prompt is outside the current routed patterns",
        "It carries a trace of what was already there.",
        "It keeps an earlier resolve in motion.",
    ]

    replace_mode = False
    direct_line = ""

    if ("project" in text_low or "build" in text_low) and ("remember itself" in text_low or "more than software" in text_low):
        direct_line = "What it circles is the feeling that this project is becoming a system that can recover structure from language and turn it into working modules."
    elif "what is this project becoming" in text_low or ("say the thing directly" in text_low and "project" in text_low):
        direct_line = "This project is becoming a system that can extract structure from language, rewrite incomplete seeds, and generate working modules."
        replace_mode = True
    elif "what does this build actually do now" in text_low or ("plain english" in text_low and "build" in text_low):
        direct_line = "Right now the build can extract seed structures from chat, rewrite incomplete seeds into canonical ones, generate the core .vl seed family, and feed that seed family into the live chat path."
        replace_mode = True
    elif "warmer but less abstract" in text_low:
        direct_line = "It should sound warmer and more human, but say what it means directly instead of circling around it."
        replace_mode = True
    elif "rewrite this response" in text_low and ("more direct" in text_low or "less poetic" in text_low):
        direct_line = "Make the wording plainer, cut extra symbolism, and say the point directly."
        replace_mode = True
    elif "don't circle it" in text_low or "just say what hurts" in text_low:
        direct_line = "What hurts is simple: something important is gone, and the hurt is still here."
    elif "dad" in text_low or "father" in text_low:
        direct_line = "What it circles is simple: you miss your dad, and it still hurts."
    elif "mom" in text_low or "mother" in text_low:
        direct_line = "What it circles is simple: you miss your mom, and it still hurts."
    elif "he's gone" in text_low or "he is gone" in text_low or "standing in that room" in text_low:
        direct_line = "What it circles is simple: he is gone, and part of you is still standing inside that loss."
    elif "say the thing" in text_low or "hiding behind abstraction" in text_low:
        direct_line = "What it circles is the loss itself, not just the shape of it."
    elif any(w in text_low for w in ["grief", "loss", "hurt", "lonely"]):
        direct_line = "What it circles is simple: something important is gone, and the hurt is still here."

    has_generic_marker = any(marker.lower() in out.lower() for marker in generic_markers)

    if direct_line:
        if replace_mode or has_generic_marker:
            out = direct_line
        elif direct_line.lower() not in out.lower():
            if out and out[-1] not in ".!?":
                out += "."
            out = (out + " " + direct_line).strip()

    out = re.sub(r"\s{2,}", " ", out).strip()
    return out

def leveon_pipeline(packet: Dict[str, Any]) -> Dict[str, Any]:
    canonical_seed_family = packet.get("canonical_seed_family") or {}
    canonical_seed_names = packet.get("canonical_seed_names") or sorted(canonical_seed_family.keys())
    canonical_seed_family = packet.get("canonical_seed_family") or {}
    canonical_seed_names = packet.get("canonical_seed_names") or sorted(canonical_seed_family.keys())
    out = base_pipeline(packet)

    text = str(packet.get("text", "") or "")
    # --- TOPOLOGY EXTRACTION ---
    try:
        spec_text = text + "\n" + final_text
        topology = parse_topology_spec(spec_text)
        meta["topology"] = topology
    except Exception as e:
        meta["topology_error"] = str(e)

    final_text = str(out.get("final_english", "") or "")
    # --- TOPOLOGY EXTRACTION ---
    try:
        spec_text = text + "\n" + final_text
        topology = parse_topology_spec(spec_text)
        meta["topology"] = topology
    except Exception as e:
        meta["topology_error"] = str(e)

    final_text = _apply_canonical_seed_voice(
        text=str(packet.get("text", "") or ""),
        tone=str(packet.get("tone", "") or ""),
        final_text=final_text,
        canonical_seed_family=canonical_seed_family,
    )
    out["final_english"] = final_text
    # --- TOPOLOGY EXTRACTION ---
    try:
        spec_text = text + "\n" + final_text
        topology = parse_topology_spec(spec_text)
        meta["topology"] = topology
    except Exception as e:
        meta["topology_error"] = str(e)

    final_text = _apply_canonical_seed_voice(
        text=str(packet.get("text", "") or ""),
        tone=str(packet.get("tone", "") or ""),
        final_text=final_text,
        canonical_seed_family=canonical_seed_family,
    )
    out["final_english"] = final_text
    tone = str(packet.get("tone", "") or "")
    meta = out.setdefault("meta", {}) or {}

    canonical_seed_trace = {
        "loaded_names": list(canonical_seed_names),
        "loaded_count": len(canonical_seed_names),
        "master_present": "LeveonMaster_v1" in canonical_seed_family,
        "core_chain_present": [
            seed for seed in [
                "IntakeCore_v1",
                "SymbolicCore_v1",
                "MemoryCore_v1",
                "KernelCore_v1",
                "VoiceCore_v1",
            ]
            if seed in canonical_seed_family
        ],
    }
    meta["canonical_seed_trace"] = canonical_seed_trace

    canonical_seed_trace = {
        "loaded_names": list(canonical_seed_names),
        "loaded_count": len(canonical_seed_names),
        "master_present": "LeveonMaster_v1" in canonical_seed_family,
        "core_chain_present": [
            seed for seed in [
                "IntakeCore_v1",
                "SymbolicCore_v1",
                "MemoryCore_v1",
                "KernelCore_v1",
                "VoiceCore_v1",
            ]
            if seed in canonical_seed_family
        ],
    }
    meta["canonical_seed_trace"] = canonical_seed_trace
    hotspot_hint = str(meta.get("hotspot_hint", "") or out.get("hotspot_hint", "") or "")

    # --- ALIGNMENT HOLD: kernel -> settling -> glyph/voice ---
    # Keeps shape meaning strict while allowing one deeper layer before final English settles.
    # --- TOPOLOGY PARSING ---
    try:
        topo = parse_topology_spec(text)
        if topo and any(v > 0 for v in topo.values()):
            meta["topology"] = topo
    except Exception:
        pass

    if apply_alignment_hold is not None:

        try:
            out = apply_alignment_hold(packet, out)
            # --- TOPOLOGY EXTRACTION ---
    try:
        spec_text = text + "\n" + final_text
        topology = parse_topology_spec(spec_text)
        meta["topology"] = topology
    except Exception as e:
        meta["topology_error"] = str(e)

    final_text = str(out.get("final_english", "") or final_text)
            meta = out.setdefault("meta", {}) or meta
        except Exception as e:
            meta["alignment_hold_error"] = str(e)

    emotion, symbol, intensity = detect_emotion_and_symbol(text, final_text)

    recall_hits = spiral_memory_recall(
        emotion=emotion,
        symbol=symbol,
        source_text=text,
        limit=1,
    )
    recall_entry = recall_hits[0] if recall_hits else None

    if recall_entry and final_text:
        continuity_line = RECALL_PHRASES.get(emotion, "It carries a trace of what was already there.")
        if continuity_line.lower() not in final_text.lower():
            # --- TOPOLOGY EXTRACTION ---
    try:
        spec_text = text + "\n" + final_text
        topology = parse_topology_spec(spec_text)
        meta["topology"] = topology
    except Exception as e:
        meta["topology_error"] = str(e)

    final_text = f"{final_text} {continuity_line}".strip()
            out["final_english"] = final_text

    saved = spiral_memory_encode(
        emotion=emotion,
        symbol=symbol,
        intensity=intensity,
        user=packet.get("user", "John"),
        source_text=text,
        final_text=final_text,
        tone=tone,
        hotspot_hint=hotspot_hint,
        extra_meta={
            "mirror_mode": packet.get("mirror_mode", ""),
            "renderer_source": meta.get("renderer_source", ""),
            "recalled_symbol": (recall_entry or {}).get("symbol", ""),
        },
    )

    meta["spiral_emotion_logged"] = True
    meta["spiral_emotion_entry"] = saved
    meta["spiral_memory_recall"] = recall_entry
    out["meta"] = meta
    return out

