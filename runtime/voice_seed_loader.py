import json
from pathlib import Path

VOICE_SEED_DIR = Path.home() / "point_vll_reassembled" / "voice_seeds"

def load_voice_seeds():
    out = {}
    if not VOICE_SEED_DIR.exists():
        return out

    for p in VOICE_SEED_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            name = data.get("name", p.name)
            out[name] = data
        except Exception:
            pass
    return out

def get_seed(name: str):
    return load_voice_seeds().get(name)

if __name__ == "__main__":
    seeds = load_voice_seeds()
    print("loaded:", len(seeds))
    for k, v in seeds.items():
        print(k, "->", v.get("type"), v.get("status"))

