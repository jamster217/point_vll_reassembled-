#!/usr/bin/env python3
from pathlib import Path
import json, time, sys

STATE = Path("var/aerospire/aerospire_state.json")

BREATH_MAP = [
    (0.15, "pause"),
    (0.35, "soften"),
    (0.60, "steady"),
    (0.82, "open"),
    (1.01, "intensify"),
]

def _clamp(x):
    try:
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.0

def read(airflow):
    airflow = _clamp(airflow)
    cmd = "steady"
    for limit, name in BREATH_MAP:
        if airflow <= limit:
            cmd = name
            break

    packet = {
        "source": "runtime.aerospire_interface",
        "interface": "AeroSpire",
        "airflow": round(airflow, 3),
        "cmd": cmd,
        "breath_map": {
            "0.00-0.15": "pause",
            "0.16-0.35": "soften",
            "0.36-0.60": "steady",
            "0.61-0.82": "open",
            "0.83-1.00": "intensify",
        },
        "targets": {
            "voice_surface": cmd,
            "response_cadence": cmd,
            "co_regulation": "slow" if cmd in ("pause", "soften") else "active",
        },
        "updated_at": time.time(),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return packet

def exec(airflow):
    return read(airflow)

if __name__ == "__main__":
    airflow = sys.argv[1] if len(sys.argv) > 1 else "0.42"
    print(json.dumps(exec(airflow), indent=2, ensure_ascii=False))

