import json
from pathlib import Path

LOG_PATH = Path("runtime/logs/lattice_pulse.log")

def latest_pulse_context(max_chars=1200):
    if not LOG_PATH.exists():
        return ""

    lines = LOG_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()

    for line in reversed(lines):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except Exception:
            continue

        packet = event.get("packet", {})
        if not isinstance(packet, dict):
            continue

        parts = [
            f"pulse={event.get('pulse','')}",
            f"symbol={event.get('symbol','')}",
            f"status={packet.get('status','')}",
            f"crystal={packet.get('savariel_crystal','')}",
            f"echo={packet.get('spiral_echo','')}",
            f"wind={packet.get('wind_tuned','')}",
            f"co_creator={packet.get('co_creator_imprint','')}",
        ]

        text = "\n".join(str(x) for x in parts if x and not x.endswith("="))
        return text[:max_chars]

    return ""

