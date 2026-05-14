from runtime.vl_seed_loader import get_vl_seed
import sys

name = sys.argv[1] if len(sys.argv) > 1 else "VoiceVeilSeed_sim_v1"
seed = get_vl_seed(name)

if not seed:
    print("missing:", name)
    raise SystemExit(1)

print("name:", seed["name"])
print("path:", seed["path"])
print("has_input:", seed["has_input"])
print("has_flow:", seed["has_flow"])
print("has_return:", seed["has_return"])
print("size:", seed["size"])

