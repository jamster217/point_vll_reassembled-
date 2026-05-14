from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
CODEX_PATH = ROOT / "assets" / "glyphs" / "glyph_surgery_codex.json"


def load_codex() -> Dict[str, Any]:
    if not CODEX_PATH.exists():
        return {
            "codex_name": "Glyph Surgery Codex",
            "sequence": ["✴️", "🪞", "✨", "📚"],
            "law": "pin -> mirror -> transmute -> seal",
            "glyphs": {},
            "missing": True,
        }

    return json.loads(CODEX_PATH.read_text(encoding="utf-8"))


def glyph_sequence() -> List[str]:
    return list(load_codex().get("sequence", ["✴️", "🪞", "✨", "📚"]))


def glyph_role(glyph: str) -> Dict[str, Any]:
    return dict(load_codex().get("glyphs", {}).get(glyph, {}))


def glyph_name(glyph: str) -> str:
    return glyph_role(glyph).get("name", glyph)


def glyph_function(glyph: str) -> str:
    return glyph_role(glyph).get("function", "")


if __name__ == "__main__":
    print(json.dumps(load_codex(), indent=2, ensure_ascii=False))

