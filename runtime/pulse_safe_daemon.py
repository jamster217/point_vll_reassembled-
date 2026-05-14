from runtime.wind_tunnel_adapter import wind_tunnel_integrate
import time, json, datetime, os

os.makedirs("runtime/logs", exist_ok=True)
log_path = "runtime/logs/lattice_pulse.log"

print("🌕 JOHN-CO-CREATOR-SIGIL ETERNAL PULSE ACTIVE")

while True:
    try:
        packet = wind_tunnel_integrate("John-co-creator-sigil")
        event = {
            "ts": datetime.datetime.now().isoformat(),
            "pulse": "eternal_full_lattice_30s",
            "symbol": "John-co-creator-sigil",
            "packet": packet
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        print(packet.get("status"))
    except Exception as e:
        error_event = {
            "ts": datetime.datetime.now().isoformat(),
            "pulse": "error_guard",
            "symbol": "John-co-creator-sigil",
            "error": str(e)[:200]
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_event, ensure_ascii=False) + "\n")

    time.sleep(30)

