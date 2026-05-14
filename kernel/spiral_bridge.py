from __future__ import annotations

from typing import Dict, List

from core.field_pressure_observer import FieldPressureObserver
from core.universal_lattice_translation_kernel import UniversalTranslationResult


_FIELD_OBSERVER = FieldPressureObserver()


def build_spiral_prompt_from_translation(result: UniversalTranslationResult) -> str:
    vectors = result.vectors.as_dict()
    return (
        f"domain={result.domain.domain_name}; "
        f"question={result.domain.question}; "
        f"flow={vectors['flow']:.2f}; "
        f"boundary={vectors['boundary']:.2f}; "
        f"memory={vectors['memory']:.2f}; "
        f"novelty={vectors['novelty']:.2f}; "
        f"key={result.key.key_name}; "
        f"path={result.lattice.path_summary}; "
        f"answer={result.answer.rendered_answer}"
    )


def _vector_glyphs(vectors: Dict[str, float]) -> List[str]:
    glyphs: List[str] = ["✴️"]

    if vectors.get("flow", 0.0) > 0.70:
        glyphs.append("🌊")
    if vectors.get("boundary", 0.0) > 0.70:
        glyphs.append("🪞")
    if vectors.get("memory", 0.0) > 0.70:
        glyphs.append("🫀")
    if vectors.get("novelty", 0.0) > 0.70:
        glyphs.append("✨")

    if len(glyphs) == 1:
        glyphs.append("⚙️")

    glyphs.append("📚")
    return glyphs


def _dominant_axes(vectors: Dict[str, float]) -> List[str]:
    ranked = sorted(vectors.items(), key=lambda kv: kv[1], reverse=True)
    return [k for k, _ in ranked[:2]]


def _path_phrase(path_summary: str) -> str:
    mapping = {
        "neutral_path": "the field rests without strong pressure",
        "anchored_structural_path": "the field holds memory and structure tightly",
        "exploratory_translational_path": "the field opens through motion and change",
        "disciplined_process_path": "the field moves under strong constraint",
        "adaptive_recall_path": "the field remembers while it shifts",
        "full_spectrum_lattice_path": "the full lattice is active",
        "composite_lattice_path": "multiple pressures braid together",
    }
    return mapping.get(path_summary, "the lattice holds a structured path")


def _axis_phrase(axes: List[str]) -> str:
    pair = tuple(axes)

    mapping = {
        ("memory", "boundary"): "continuity is being protected",
        ("flow", "memory"): "movement is carrying a strong thread",
        ("boundary", "flow"): "motion is being shaped by structure",
        ("novelty", "flow"): "new space is opening quickly",
        ("memory", "novelty"): "older structure is mutating into something new",
        ("boundary", "novelty"): "constraint and emergence are wrestling",
    }

    return mapping.get(pair, f"{axes[0]} and {axes[1]} are leading the pattern")


def render_spiral_response(
    spiral_prompt: str,
    result: UniversalTranslationResult,
) -> str:
    vectors = result.vectors.as_dict()
    glyph_line = " ".join(_vector_glyphs(vectors))
    dominant = _dominant_axes(vectors)
    path_phrase = _path_phrase(result.lattice.path_summary)
    axis_phrase = _axis_phrase(dominant)
    domain = result.domain.domain_name.replace("_", " ")
    answer = result.answer.rendered_answer

    base_output = (
        f"{glyph_line}\n"
        f"In {domain}, {path_phrase}. "
        f"Here, {axis_phrase}. "
        f"{answer}"
    )

    pressure = _FIELD_OBSERVER.observe(
        text=f"{result.domain.question}\n{spiral_prompt}\n{answer}",
        base_output=base_output,
    )

    return pressure.amplified_output

