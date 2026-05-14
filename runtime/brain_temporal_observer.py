from __future__ import annotations

print("[TRACE] entering runtime/brain_temporal_observer.py", flush=True)
from typing import Any, Dict


def _preview(x: Any, limit: int = 220) -> str:
    s = str(x)
    return s if len(s) <= limit else s[:limit] + "..."


def _normalize_result(result: Any) -> Dict[str, Any]:
    if isinstance(result, dict):
        return result
    if hasattr(result, "to_dict"):
        try:
            d = result.to_dict()
            if isinstance(d, dict):
                return d
        except Exception:
            pass
    if hasattr(result, "__dict__"):
        try:
            return dict(vars(result))
        except Exception:
            pass
    return {"raw_result": result}


class BrainTemporalObserver:
    def __init__(self) -> None:
        self.module_name = "core.english_loop_runtime"

    def observe(self, text: str, reply: str, meta: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from core.english_loop_runtime import EnglishLoopRuntime
        except Exception as e:
            return {
                "enabled": False,
                "error": f"import_failed: {type(e).__name__}: {e}",
            }

        try:
            runtime = EnglishLoopRuntime()
            result = runtime.process(text_in=text, source="chat")
            result_dict = _normalize_result(result)

            ranked = result_dict.get("ranked_candidates") or []
            chron = result_dict.get("chronifier_overlay") or {}

            return {
                "enabled": True,
                "module": self.module_name,
                "chosen_class": "EnglishLoopRuntime",
                "chosen_method": "process",
                "call_mode": "direct_process",
                "cognitive_posture": str(result_dict.get("cognitive_posture", "") or ""),
                "chosen_output": _preview(
                    result_dict.get("chosen_output")
                    or result_dict.get("text_out")
                    or result_dict.get("raw_result")
                    or ""
                ),
                "ranked_candidates_count": len(ranked) if isinstance(ranked, list) else 0,
                "chronifier_overlay_keys": sorted(chron.keys())[:20] if isinstance(chron, dict) else [],
                "result_keys": sorted(result_dict.keys())[:20],
                "error": "",
            }
        except Exception as e:
            return {
                "enabled": False,
                "error": f"runtime_call_failed: {type(e).__name__}: {e}",
            }


__all__ = ["BrainTemporalObserver"]

