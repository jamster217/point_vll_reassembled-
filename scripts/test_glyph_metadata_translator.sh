#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/point_vll_reassembled" || exit 1

python - <<'PY'
from runtime.glyph_metadata_translator import interpret_glyph_metadata

glyph = {
    "name": "@FLAME_OF_RECKONING",
    "emoji": "🔥",
    "element": "Fire",
    "emotion": "Trial, Anger, Purification",
    "poetic_seed": "I ignite the judgment within",
    "symbolic_gravity": "High",
}

out = interpret_glyph_metadata(glyph)

print("=== GLYPH METADATA TRANSLATOR TEST ===")
print(out["summary"])
PY
