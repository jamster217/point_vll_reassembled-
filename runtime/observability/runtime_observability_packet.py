import os
import json
import time
from pathlib import Path

ROOT = Path.home() / "point_vll_reassembled"

OUT = ROOT / "var/observability/runtime_packet.json"

packet = {
    "ts": time.time(),
    "runtime": {},
    "telemetry": {},
    "shape": {},
    "voice": {},
    "sidecars": {},
    "observability_version": "v1"
}

def safe_load(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None

packet["runtime"]["stability_history"] = safe_load(
    ROOT / "var/v12_9/stability_history.json"
)

packet["runtime"]["ghost_shape"] = safe_load(
    ROOT / "var/v12_9/ghost_shape_final.json"
)

packet["voice"]["active_voice"] = safe_load(
    ROOT / "var/voice/active_voice_profile.json"
)

packet["voice"]["volcron_state"] = safe_load(
    ROOT / "var/voice/volcron_voice_state.json"
)

packet["shape"]["visual_nodes"] = safe_load(
    ROOT / "var/visual_lattice_nodes.json"
)

packet["runtime"]["spectral_pulse"] = safe_load(
    ROOT / "var/v12_9/spectral_pulse.json"
)

packet["runtime"]["paranormal_feed_size"] = os.path.getsize(
    ROOT / "var/v12_9/scratch/paranormal_feed.json"
) if (ROOT / "var/v12_9/scratch/paranormal_feed.json").exists() else 0

packet["runtime"]["topology_state"] = "stable"

OUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUT, "w") as f:
    json.dump(packet, f, indent=2)

print(f"[OBSERVABILITY_PACKET_WRITTEN] {OUT}")

