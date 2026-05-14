from pathlib import Path
import json
from datetime import datetime, timezone

ARTIFACT_DIR = Path.home() / "point_vll_reassembled" / "artifacts"

def log_artifact(name: str, payload):
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = ARTIFACT_DIR / f"{name}_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(path)

if __name__ == "__main__":
    demo = {"status": "ok", "message": "artifact logger ready"}
    print(log_artifact("artifact_logger_test", demo))

