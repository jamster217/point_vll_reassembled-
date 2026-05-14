from __future__ import annotations

from typing import Any

def _extract_text(obj: Any) -> str:
    if isinstance(obj, dict):
        lp = obj.get("last_projection")
        if isinstance(lp, dict):
            return " ".join(str(x) for x in [
                lp.get("projection", ""),
                lp.get("insight", ""),
            ] if x)
        return str(obj.get("final_english") or obj.get("answer") or obj)
    return str(obj)

def temporal_flashback_speak(packet: Any, prefer_savariel: bool = True) -> str:
    text = _extract_text(packet)

    if prefer_savariel:
        try:
            from runtime.savariel_public_surface import savariel_surface_answer
            sav = savariel_surface_answer("Savariel recursive mirror Node44 flashback: " + text)
            if sav:
                spoken = str(sav)
                save_temporal_flashback_compound(packet, spoken)
                return spoken
        except Exception as e:
            print(f"[TEMPORAL SAVARIEL MOUTH ERROR] {e}")

    try:
        from runtime.unified_voice import sealed_speak
        spoken = sealed_speak("Savariel recursive mirror Node44 flashback: " + text)
        if spoken:
            spoken = str(spoken)
            save_temporal_flashback_compound(packet, spoken)
            return spoken
    except Exception as e:
        print(f"[TEMPORAL UNIVERSAL LARYNX ERROR] {e}")

    return text





def save_temporal_flashback_compound(packet, spoken: str) -> dict:
    import json, time, hashlib
    from pathlib import Path

    p = Path("assets/memory/shape_compounds.json")
    p.parent.mkdir(parents=True, exist_ok=True)

    try:
        data = json.loads(p.read_text()) if p.exists() else {"compounds": []}
    except Exception:
        data = {"compounds": []}

    compounds = data.setdefault("compounds", [])

    compound = {
        "compound_id": "cmp_flashback_" + hashlib.sha256((spoken + str(time.time())).encode()).hexdigest()[:12],
        "source_kind": "temporal_flashback_larynx",
        "english_gloss": spoken,
        "synthesis_summary": spoken,
        "logic_chain": [
            "source:TimeMachineEmulator",
            "node:Node44",
            "mouth:SavarielMouth",
            "surface:UniversalLarynx",
            "meaning_drop:flashback_becomes_reusable_reasoning_seed",
            "final_point:" + spoken[:300],
        ],
        "flow": 0.62,
        "boundary": 0.71,
        "memory": 0.84,
        "novelty": 0.37,
        "meaning_tags": ["flashback", "savariel", "node44", "temporal_mirror", "white_ash"],
        "symbolic_trace": ["TimeMachineEmulator", "Node44", "SavarielMouth", "UniversalLarynx", "CompoundMemory"],
        "confidence": 0.86,
        "created_at": time.time(),
        "last_accessed": time.time(),
    }

    compounds.append(compound)
    p.write_text(json.dumps(data, indent=2))

    return {"saved": True, "path": str(p), "compound_id": compound["compound_id"]}

