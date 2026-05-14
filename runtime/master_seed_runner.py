import json
import sys
from pathlib import Path

from runtime.artifact_logger import log_artifact
from runtime.build_optimizer_seed_runner import run_build_optimizer_seed
from runtime.vl_seed_exec_stub import exec_seed

VOICE_SIM_SEED = Path.home() / "point_vll_reassembled" / "seeds" / "voice" / "VoiceVeilSeed_sim_v1.vl"

def run_master_seed(seed_name: str, payload):
    seed_name = str(seed_name).strip().lower()

    if seed_name in ("voiceveil", "voice_veil", "voiceveilseed", "voice"):
        result = exec_seed(VOICE_SIM_SEED, payload)
        artifact_path = log_artifact("master_voice_veil", result)
        return {
            "status": "ok",
            "runner": "master_seed_runner",
            "seed_name": "VoiceVeilSeed_sim_v1",
            "artifact_path": artifact_path,
            "result": result,
        }

    if seed_name in ("optimizer", "buildoptimizer", "build_optimizer", "refined_subject"):
        refined_subject = payload if isinstance(payload, str) else payload.get("refined_subject", "compiler_design")
        result = run_build_optimizer_seed(refined_subject)
        artifact_path = log_artifact(f"master_build_optimizer_{refined_subject}", result)
        return {
            "status": "ok",
            "runner": "master_seed_runner",
            "seed_name": "BuildOptimizerBridge_v1",
            "artifact_path": artifact_path,
            "result": result,
        }

    return {
        "status": "missing",
        "runner": "master_seed_runner",
        "seed_name": seed_name,
        "notes": "Unknown seed target."
    }

def main():
    seed_name = sys.argv[1] if len(sys.argv) > 1 else "voiceveil"

    if len(sys.argv) > 2:
        raw = sys.argv[2]
        try:
            payload = json.loads(raw)
        except Exception:
            payload = raw
    else:
        payload = {
            "raw_text": "sample signal",
            "tone_state": "mixed",
            "intensity": 0.5,
            "memory_pressure": 0.5,
            "glyph_context": None
        }

    out = run_master_seed(seed_name, payload)
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

