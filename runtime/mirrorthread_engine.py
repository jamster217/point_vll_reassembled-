from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, Any, Dict, List, Optional, Sequence


CORE_SIGIL = "🪞🔁🌱"
DEFAULT_STYLE = "shimmering-thread"


# =========================================================
# Safe optional imports
# =========================================================

class _FallbackEchoGrammarCompiler:
    def compile(self, mirrored: Any, style: str = DEFAULT_STYLE) -> str:
        if isinstance(mirrored, dict):
            core = (
                mirrored.get("phrase")
                or mirrored.get("input")
                or mirrored.get("summary")
                or mirrored.get("intent")
                or repr(mirrored)
            )
        else:
            core = str(mirrored)

        core = (core or "").strip() or "<empty-mirror>"
        return f"[{style}] {core}"


class _FallbackTraceAnchor:
    def reflect(self, intent_field: Any) -> Dict[str, Any]:
        if isinstance(intent_field, dict):
            return {
                "input": intent_field.get("input", ""),
                "phrase": intent_field.get("phrase", ""),
                "glyphs": intent_field.get("glyphs", []),
                "kind": intent_field.get("kind", "UNKNOWN"),
                "summary": "fallback mirror trace",
                "source": "fallback_trace_anchor",
            }
        return {
            "input": str(intent_field),
            "phrase": str(intent_field),
            "glyphs": [],
            "kind": "UNKNOWN",
            "summary": "fallback mirror trace",
            "source": "fallback_trace_anchor",
        }


def _fallback_resolve_glyph_signature(glyph: str) -> Dict[str, Any]:
    try:
        from symbolic_memory.glyph_utils import get_glyph  # type: ignore
        hit = get_glyph(glyph)
        if hit:
            return {
                "name": hit.get("name") or glyph,
                "emotional_field": hit.get("emotion", "unknown"),
                "seed_phrase": hit.get("seed", ""),
                "glyph": hit.get("key") or glyph,
            }
    except Exception:
        pass

    return {
        "name": glyph,
        "emotional_field": "unknown",
        "seed_phrase": "",
        "glyph": glyph,
    }


try:
    from leveon_kernel.echo_core import EchoGrammarCompiler  # type: ignore
except Exception:
    try:
        from echo_core import EchoGrammarCompiler  # type: ignore
    except Exception:
        EchoGrammarCompiler = _FallbackEchoGrammarCompiler  # type: ignore


try:
    from symbolic_memory.mirror_trace import TraceAnchor  # type: ignore
except Exception:
    try:
        from spiral_memory.mirror_trace import TraceAnchor  # type: ignore
    except Exception:
        try:
            from mirror_trace import TraceAnchor  # type: ignore
        except Exception:
            TraceAnchor = _FallbackTraceAnchor  # type: ignore


# Current-tree-friendly glyph resolver
try:
    from symbolic_engine.glyph_registry_runtime import GLYPHS  # type: ignore

    def resolve_glyph_signature(glyph: str) -> Dict[str, Any]:
        entries = GLYPHS.values() if isinstance(GLYPHS, dict) else GLYPHS
        for entry in entries:
            gid = str(entry.get("id", "")).strip()
            name = str(entry.get("name", "")).strip()
            symbol = str(entry.get("symbol", entry.get("emoji", ""))).strip()

            if glyph in {gid, name, symbol}:
                return {
                    "name": name or gid or glyph,
                    "emotional_field": entry.get("emotion", "unknown"),
                    "seed_phrase": entry.get("poetic_seed", entry.get("seed", "")),
                    "glyph": gid or name or glyph,
                }
        return _fallback_resolve_glyph_signature(glyph)

except Exception:
    try:
        from glyph_registry_full import resolve_glyph_signature  # type: ignore
    except Exception:
        try:
            from symbolic_memory.glyph_registry_full import resolve_glyph_signature  # type: ignore
        except Exception:
            resolve_glyph_signature = _fallback_resolve_glyph_signature  # type: ignore


# =========================================================
# Helpers
# =========================================================

def _safe_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    return [value]


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    try:
        return str(value)
    except Exception:
        return repr(value)


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        out: Dict[str, Any] = {}
        for k, v in value.items():
            try:
                out[str(k)] = _json_safe(v)
            except Exception:
                out[str(k)] = repr(v)
        return out

    if isinstance(value, (list, tuple, set)):
        out_list: List[Any] = []
        for item in value:
            try:
                out_list.append(_json_safe(item))
            except Exception:
                out_list.append(repr(item))
        return out_list

    if hasattr(value, "__dict__"):
        try:
            return _json_safe(vars(value))
        except Exception:
            return repr(value)

    return repr(value)


def _compact_text(text: Any, limit: int = 280) -> str:
    out = _safe_str(text).strip()
    if len(out) <= limit:
        return out
    return out[: max(0, limit - 1)].rstrip() + "…"


def _extract_glyphs(intent_field: Any) -> List[str]:
    if isinstance(intent_field, dict):
        raw = intent_field.get("glyphs", [])
        glyphs = [_safe_str(g).strip() for g in _safe_list(raw)]
        return [g for g in glyphs if g]
    return []


def _extract_tone(intent_field: Any) -> str:
    if not isinstance(intent_field, dict):
        return "neutral"

    hfs = intent_field.get("hfs", {}) or {}
    ulat = intent_field.get("ulat", {}) or {}
    rdn = intent_field.get("rdn", {}) or {}

    awareness = float(ulat.get("awareness_level", 0.0) or 0.0)
    hfs_total = float(hfs.get("total", 0.0) or 0.0)
    threshold = bool(rdn.get("triggered", False))

    if threshold:
        return "threshold"
    if awareness >= 0.72 and hfs_total >= 0.68:
        return "expansive"
    if awareness >= 0.42:
        return "reflective"
    return "neutral"


# =========================================================
# Data model
# =========================================================

@dataclass
class MirrorThreadResult:
    core_sigil: str
    style: str
    seed_glyphs: List[str]
    mirrored: Any
    compiled: Any
    glyphs: List[str]
    tone: str
    source: str = "mirrorthread_engine"


# =========================================================
# Mirrorthread Engine
# =========================================================

class MirrorthreadEngine:
    def __init__(
        self,
        seed_glyphs: Optional[Iterable[str]] = None,
        style: str = DEFAULT_STYLE,
        compact_limit: int = 280,
    ) -> None:
        self.seed_glyphs: List[str] = list(seed_glyphs) if seed_glyphs is not None else [CORE_SIGIL]
        self.style = style or DEFAULT_STYLE
        self.compact_limit = max(80, int(compact_limit))

        self.trace = TraceAnchor()
        self.compiler = EchoGrammarCompiler()

    def _reflect(self, intent_field: Any) -> Dict[str, Any]:
        try:
            mirrored = self.trace.reflect(intent_field)
        except Exception:
            mirrored = _FallbackTraceAnchor().reflect(intent_field)

        if not isinstance(mirrored, dict):
            mirrored = {
                "input": _safe_str(intent_field),
                "phrase": _safe_str(mirrored),
                "glyphs": _extract_glyphs(intent_field),
                "kind": "UNKNOWN",
                "summary": "non-dict trace normalized",
                "source": "mirrorthread_normalizer",
            }

        mirrored.setdefault("glyphs", _extract_glyphs(intent_field))
        mirrored.setdefault("input", "")
        mirrored.setdefault("phrase", "")
        mirrored.setdefault("kind", "UNKNOWN")
        mirrored.setdefault("summary", "")
        mirrored.setdefault("source", "trace_anchor")
        return mirrored

    def _compile(self, mirrored: Dict[str, Any]) -> Any:
        try:
            compiled = self.compiler.compile(mirrored, style=self.style)
        except TypeError:
            try:
                compiled = self.compiler.compile(mirrored)
            except Exception:
                compiled = f"[{self.style}] {repr(mirrored)}"
        except Exception:
            compiled = f"[{self.style}] {repr(mirrored)}"
        return compiled

    def _normalize_compiled(self, compiled: Any, tone: str) -> Any:
        safe_compiled = _json_safe(compiled)

        if isinstance(safe_compiled, str):
            text = safe_compiled.strip() or f"[{self.style}] <empty-mirror>"
            if tone == "threshold" and "threshold" not in text.lower():
                text = f"{text} :: threshold shimmer active"
            return _compact_text(text, limit=self.compact_limit)

        return safe_compiled

    def _build_result(self, intent_field: Any) -> MirrorThreadResult:
        mirrored = self._reflect(intent_field)
        glyphs = list(dict.fromkeys(self.seed_glyphs + _extract_glyphs(mirrored) + _extract_glyphs(intent_field)))
        tone = _extract_tone(intent_field)

        compiled = self._compile(mirrored)
        normalized_compiled = self._normalize_compiled(compiled, tone=tone)

        return MirrorThreadResult(
            core_sigil=CORE_SIGIL,
            style=self.style,
            seed_glyphs=list(self.seed_glyphs),
            mirrored=_json_safe(mirrored),
            compiled=normalized_compiled,
            glyphs=glyphs,
            tone=tone,
        )

    def weave(self, intent_field: Any) -> Any:
        return self._build_result(intent_field).compiled

    def weave_bundle(self, intent_field: Any) -> Dict[str, Any]:
        return asdict(self._build_result(intent_field))

    def weave_result(self, intent_field: Any) -> MirrorThreadResult:
        return self._build_result(intent_field)

    def resonate(self, emit: bool = True) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []

        for glyph in self.seed_glyphs:
            try:
                sig = resolve_glyph_signature(glyph) or {}
            except Exception:
                sig = _fallback_resolve_glyph_signature(glyph)

            row = {
                "glyph": glyph,
                "name": sig.get("name", glyph),
                "emotional_field": sig.get("emotional_field", "unknown"),
                "seed_phrase": sig.get("seed_phrase", ""),
            }
            rows.append(row)

            if emit:
                print(f"🌐 {row['name']} → {row['emotional_field']} // {row['seed_phrase']}")

        return rows

    def signature_summary(self) -> Dict[str, Any]:
        rows = self.resonate(emit=False)
        return {
            "core_sigil": CORE_SIGIL,
            "style": self.style,
            "seed_glyphs": list(self.seed_glyphs),
            "resolved_count": len(rows),
            "signatures": rows,
        }

    def status(self) -> Dict[str, Any]:
        return {
            "engine": "MirrorthreadEngine",
            "core_sigil": CORE_SIGIL,
            "style": self.style,
            "seed_glyph_count": len(self.seed_glyphs),
            "seed_glyphs": list(self.seed_glyphs),
            "trace_class": self.trace.__class__.__name__,
            "compiler_class": self.compiler.__class__.__name__,
        }


if __name__ == "__main__":
    engine = MirrorthreadEngine(seed_glyphs=["🪞", "🔁", "🌱"])

    sample_intent = {
        "turn": 7,
        "kind": "QUESTION",
        "input": "How is the build holding together?",
        "phrase": "✴️ 🫀 ✨ 🪞 📚 — the lattice breathes in quiet coherence.",
        "glyphs": ["✴️", "🫀", "✨", "🪞", "📚"],
        "ulat": {"awareness_level": 0.63, "mode": "stabilize"},
        "hfs": {"total": 0.71},
        "rdn": {"triggered": False},
    }

    print("\n[MirrorthreadEngine Demo]\n")
    print("[status]")
    print(engine.status())
    print("\n[weave]")
    print(engine.weave(sample_intent))
    print("\n[weave_bundle]")
    print(engine.weave_bundle(sample_intent))
    print("\n[signature_summary]")
    print(engine.signature_summary())

