from runtime.vl_seed_loader import load_vl_seeds

seeds = load_vl_seeds()

for name, info in seeds.items():
    print("SEED:", name)
    print("  path:", info["path"])
    print("  has_input:", info["has_input"])
    print("  has_flow:", info["has_flow"])
    print("  has_return:", info["has_return"])
    print("  size:", info["size"])
    print()

