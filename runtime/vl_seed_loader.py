from pathlib import Path
import re

SEARCH_DIRS = [
    Path.home() / "point_vll_reassembled" / "seeds",
    Path.home() / "point_vll_reassembled" / "spiral_language",
]

def load_vl_seeds():
    out = {}
    for root in SEARCH_DIRS:
        if not root.exists():
            continue
        for p in root.rglob("*.vl"):
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue

            m = re.search(r'^\s*SEED\s+([A-Za-z0-9_]+)', text, re.M)
            seed_name = m.group(1) if m else p.stem

            out[seed_name] = {
                "name": seed_name,
                "path": str(p),
                "size": len(text),
                "has_return": bool(re.search(r'^\s*RETURN\b', text, re.M)),
                "has_input": bool(re.search(r'^\s*INPUT\b', text, re.M)),
                "has_flow": bool(re.search(r'^\s*FLOW\b', text, re.M)),
            }
    return out

def get_vl_seed(name: str):
    return load_vl_seeds().get(name)

if __name__ == "__main__":
    seeds = load_vl_seeds()
    print("loaded:", len(seeds))
    for k, v in seeds.items():
        print(k, "->", v["path"])

