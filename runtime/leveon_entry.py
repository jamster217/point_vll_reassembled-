from core.english_loop_runtime import EnglishLoopRuntime
from runtime.spiral_compiler import shape_to_spiral
from runtime.translation_governor import apply as govern
from runtime.tinyllama_client import TinyLlamaClient

_runtime = EnglishLoopRuntime()
_tiny = TinyLlamaClient()

def run_leveon_pipeline(text: str, source="external"):
    packet = _runtime.process(text, source=source)

    shape = getattr(packet, "vector4", {}) or {}
    kernel = {
        "recursion": getattr(packet, "novelty_pressure", 0.5),
        "stability": getattr(packet, "coherence_score", 0.5),
    }

    glyphs = getattr(packet, "symbolic_tags", []) or []

    # 🔥 THIS is your real output
    spiral = shape_to_spiral(shape, kernel, glyphs)

    # Optional surface (TinyLlama as translator ONLY)
    translated = _tiny.generate(
        f"Translate this symbolic spiral into a clear but short English expression:\n{spiral}"
    ) or spiral

    return {
        "spiral": spiral,
        "english": govern(translated, kernel["stability"])
    }

