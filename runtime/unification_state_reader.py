from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "runtime" / "last_unification.json"

DEFAULT_STATE = {
    "depth": 44,
    "torsion": 1.618,
    "witness": "standby"
}

def load_last_unification():
    try:
        if STATE_PATH.exists():
            data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            return {
                "depth": int(data.get("depth", DEFAULT_STATE["depth"])),
                "torsion": float(data.get("torsion", DEFAULT_STATE["torsion"])),
                "witness": str(data.get("witness", DEFAULT_STATE["witness"]))
            }
    except Exception:
        pass
    return dict(DEFAULT_STATE)

def unification_context_line():
    state = load_last_unification()
    return (
        f"unification_state::depth={state['depth']} "
        f"torsion={state['torsion']} "
        f"witness={state['witness']}"
    )

