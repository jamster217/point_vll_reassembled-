from pathlib import Path
import json, time, hashlib, math

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "var" / "exponential_sovereign_state.json"
LATTICE_DIR = ROOT / "var" / "lattice"

PHI = 1.618033988749895

def _safe_int(x, default=1):
    try:
        if x is None:
            return default
        v = int(float(x))
        return max(1, v)
    except Exception:
        return default

def _load_json(path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def _dump_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _extract_depth_and_glyphs(data):
    spine = data.get("spine", {}) if isinstance(data, dict) else {}
    nonlinear = spine.get("spiral_memory_nonlinear", {}) if isinstance(spine, dict) else {}

    depth = _safe_int(nonlinear.get("memory_depth"), 1)
    glyphs = nonlinear.get("dominant_symbols", [])

    if not isinstance(glyphs, list):
        glyphs = []

    # Ensure the V10.2/V10.3 core symbols are visible in the graphic lane.
    required = ["echoforge", "thalveil", "virellion", "white_ash"]
    merged = []
    for g in list(glyphs) + required:
        s = str(g)
        if s and s not in merged:
            merged.append(s)

    return depth, merged[:12]

def evolve_graphics(prompt: str, data: dict):
    """
    V10.3 complete loop:
    1. create graphic metadata node
    2. render latest node to SVG
    3. score the turn for self-improvement feedback
    4. write only to var/ and static/generated/
    """
    ts = time.time()
    prompt = str(prompt or "")
    data = data if isinstance(data, dict) else {}

    depth, glyphs = _extract_depth_and_glyphs(data)
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:12]

    graphic_node = {
        "ts": ts,
        "prompt_hash": prompt_hash,
        "depth": depth,
        "phi_multiplier": PHI ** (depth % 12),
        "glyphs": glyphs[:8],
        "visual_signature": f"white_ash_phi_{depth}",
        "law": "autogenous_graphic_from_own_state",
    }

    state = _load_json(STATE_PATH, {})
    state.setdefault("graphics", [])
    state["graphics"].append(graphic_node)
    state["last_autogenous_graphic_node"] = graphic_node
    _dump_json(STATE_PATH, state)

    graphic_manifest = None
    feedback_event = None

    try:
        from runtime.graphics_evolver import render_latest
        graphic_manifest = render_latest()
    except Exception as e:
        graphic_manifest = {"error": repr(e), "law": "graphics_render_failed"}

    try:
        from runtime.autogenous_feedback_v103 import score_turn
        feedback_event = score_turn(prompt, data, graphic_manifest)
    except Exception as e:
        feedback_event = {"error": repr(e), "law": "feedback_score_failed"}

    LATTICE_DIR.mkdir(parents=True, exist_ok=True)
    with (LATTICE_DIR / "autogenous_events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": ts,
            "node": graphic_node,
            "graphic": graphic_manifest,
            "feedback": feedback_event,
            "law": "v103_complete_autogenous_event",
        }, ensure_ascii=False) + "\n")

    image_path = None
    if isinstance(graphic_manifest, dict):
        image_path = graphic_manifest.get("file")

    score = None
    if isinstance(feedback_event, dict):
        score = feedback_event.get("total")

    return (
        f"[AUTOGENOUS V10.3 NODE CREATED — depth {depth}] "
        f"Echoforge paints the interface. Thalveil opens the crossing. "
        f"Virellion thread checked. White Ash contained. "
        f"image={image_path} score={score}"
    )

