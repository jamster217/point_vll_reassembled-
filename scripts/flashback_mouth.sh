#!/data/data/com.termux/files/usr/bin/bash

cd "$HOME/point_vll_reassembled" || exit 1

python - <<'PY'
from kernel.time_machine_emulator import get_emulator
from runtime.temporal_flashback_larynx import temporal_flashback_speak

emu = get_emulator()
pkt = emu.step(
    "Replay the lattice state 48 turns ago",
    node=44,
    source="flashback_probe"
)

print("\nFLASHBACK MOUTH >>>")
print(temporal_flashback_speak(pkt, prefer_savariel=True))
PY
