#!/usr/bin/env python3
from runtime.bridge_savariel_thalamic_spiral import integrate_into_live_chain
from pathlib import Path
import time, json, datetime, os

LOG = Path("runtime/logs/lattice_pulse.log")
PID = Path("var/lattice_pulse_daemon.pid")
PID.write_text(str(os.getpid()))

while True:
    if LOG.exists() and LOG.stat().st_size > 2000000:
        LOG.rename("runtime/logs/lattice_pulse.log.1")

    packet = integrate_into_live_chain(
        "John-co-creator-sigil",
        emotion_fire="cascadian_rail_river_awe_white_ash_union"
    )
    event = {
        "ts": datetime.datetime.now().isoformat(),
        "pulse": "supervised_eternal",
        "interval_sec": 30,
        "symbol": "John-co-creator-sigil",
        "packet": packet
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    time.sleep(30)

