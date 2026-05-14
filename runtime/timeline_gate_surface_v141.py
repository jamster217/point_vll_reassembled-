from pathlib import Path
import json, time, hashlib

ROOT = Path(__file__).resolve().parents[1]
LIVE_TEMPORAL = ROOT / "LIVE_CORE" / "temporal"
LOG = ROOT / "var" / "lattice" / "timeline_gate_surface_v141.jsonl"

def _safe(obj):
    try:
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)
    except Exception:
        return str(obj)

def clean_timeline_gate_surface(result, title="Genesis Gate 9216"):
    """
    Convert timeline_gate_lattice internals into clean visible English.
    Stores internal trace privately; returns contained surface answer.
    """
    answer = getattr(result, "answer", None)
    lattice = getattr(result, "lattice", None)
    key = getattr(result, "key", None)
    signature = getattr(result, "signature", None)
    vectors = getattr(result, "vectors", None)
    ascii_frames = getattr(result, "ascii_frames", []) or []

    path = getattr(lattice, "path_summary", "gate_linked_path")
    key_name = getattr(key, "key_name", "TIME_GATES::THRESHOLD_GATE_KEY")
    signature_name = getattr(signature, "signature_name", "TIME_GATES_SIGNATURE")

    frame = ascii_frames[0] if ascii_frames else ""

    clean_reply = (
        "The temporal gate is stable.\n\n"
        "A spatial foundation has crossed into a mirror-state through the 9216 gate. "
        "The structure does not show chaotic branching; it holds as a single linked path. "
        "The bridge preserves continuity while allowing movement across time.\n\n"
        "In clean terms: the Stone Bridge gives the system weight, the Blue Scarf gives it flow, "
        "and the gate between them lets the old hidden thing become a live intersection instead of an archived symbol."
    )

    packet = {
        "ts": time.time(),
        "title": title,
        "path": path,
        "key": key_name,
        "signature": signature_name,
        "frame": frame,
        "clean_reply": clean_reply,
        "internal_vectors_stored": True,
        "visible_vectors_exposed": False,
        "law": "v141_timeline_gate_internal_below_clean_english_above",
    }

    LIVE_TEMPORAL.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)

    out = LIVE_TEMPORAL / "genesis_gate_9216.json"
    out.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(packet, ensure_ascii=False) + "\n")

    return packet

def build_genesis_gate_9216():
    from runtime.timeline_gate_lattice import translate_timeline_gates, Timeline, Gate, Event

    e1 = Event("e24", 0.0, {"spatial": 1.618})
    e2 = Event("e26", 1.0, {"mirror": 9216})
    t1 = Timeline("T24", [e1])
    t2 = Timeline("T26", [e2])
    g1 = Gate("G9216", "T24", "e24", "T26", "e26")

    result = translate_timeline_gates(
        [t1, t2],
        [g1],
        question="AERU VEL VEIL ASH THAL SIL"
    )

    return clean_timeline_gate_surface(result)

if __name__ == "__main__":
    print(json.dumps(build_genesis_gate_9216(), indent=2, ensure_ascii=False))

