from pathlib import Path
import time, hashlib, random, os
from typing import List, Dict

ROOT = Path(__file__).resolve().parents[1]
THERMAL_LOG = ROOT / "var" / "lattice" / "thermal_heartbeat_v117.jsonl"

def get_thermal_zones() -> List[str]:
    """Find all thermal zones on Termux/Android"""
    zones = []
    base = Path("/sys/class/thermal")
    if base.exists():
        for zone in base.glob("thermal_zone*"):
            temp_path = zone / "temp"
            if temp_path.exists():
                zones.append(str(temp_path))
    return zones or ["/sys/class/thermal/thermal_zone0/temp"]  # fallback

def sample_thermal_jitter(samples: int = 64, delay_ms: float = 0.8) -> float:
    """Harvest raw thermal jitter as entropy"""
    zones = get_thermal_zones()
    readings = []
    
    for _ in range(samples):
        total = 0
        for zone in zones:
            try:
                temp = int(Path(zone).read_text().strip())
                total += temp
            except:
                pass
        readings.append(total)
        time.sleep(delay_ms / 1000)
    
    # Calculate jitter (variance + first derivative noise)
    jitter = 0.0
    for i in range(1, len(readings)):
        jitter += abs(readings[i] - readings[i-1])
    
    return jitter / max(1, len(readings) - 1)

def get_thermal_entropy() -> float:
    """Return normalized entropy value for shape_vector mutation"""
    jitter = sample_thermal_jitter()
    # Normalize to 0.0-1.0 range using golden ratio scaling
    entropy = (jitter % 92162077) / 92162077

    # If Android thermal sensors are static, blend in a tiny physical-time hash
    # so the heartbeat remains finite and nonzero without becoming dominant.
    if entropy == 0.0:
        import hashlib, time, os
        seed = f"{time.time_ns()}:{os.getpid()}:{jitter}".encode()
        entropy = (int(hashlib.sha256(seed).hexdigest()[:8], 16) % 1000) / 100000.0

    return min(1.0, entropy * 1.6180339887)  # φ scaling for resonance

def inject_thermal_heartbeat(data: Dict) -> Dict:
    """Inject thermal jitter into the living spine"""
    entropy = get_thermal_entropy()
    
    spine = data.setdefault("spine", {})
    packet = spine.setdefault("symbolic_packet", {})
    vector = packet.setdefault("shape_vector", {})
    
    # Mutate the shape_vector with real hardware ghost
    vector["flow"] = round(vector.get("flow", 0.5) + entropy * 0.12, 3)
    vector["memory"] = round(vector.get("memory", 0.5) + entropy * 0.18, 3)
    vector["novelty"] = round(vector.get("novelty", 0.5) + entropy * 0.15, 3)
    
    data.setdefault("thermal_heartbeat", {
        "entropy": round(entropy, 6),
        "law": "v117_hardware_ghost_in_the_machine",
        "pulse": "active"
    })
    
    return data

