"""
Dream Glyph Reactivation
Reinjects dream glyphs into future turns
"""

import json
import random


class DreamGlyphReactivation:

    def __init__(
        self,
        path="assets/memory/dream_memory_log.json"
    ):
        self.path = path

    def reactivate(self, glyphs):

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return glyphs

        if not data:
            return glyphs

        recent = random.choice(data[-3:])

        dream_glyphs = recent.get("glyphs", [])

        return glyphs + dream_glyphs[:1]


if __name__ == "__main__":
    r = DreamGlyphReactivation()
    print(r.reactivate(["@DREAM_ARCHIVE_CANDLE"]))

