#!/usr/bin/env python3
from runtime.performance_routing_oracle import choose_algorithm, summarize_routing

tests = [
    (10, "Algorithm B"),
    (50, "Algorithm B"),
    (100, "Algorithm C"),
    (1000, "Algorithm C"),
    (10000, "Algorithm C"),
]

print("=== PERFORMANCE ROUTING ORACLE ===")
print(summarize_routing())
print()

failed = False

for n, expected in tests:
    result = choose_algorithm(n)
    selected = result["selected_algorithm"]
    ok = selected == expected
    print(f"N={n} -> {selected} | expected={expected} | ok={ok}")
    if not ok:
        failed = True

if failed:
    raise SystemExit("Performance routing test failed.")

print()
print("Performance routing oracle locked.")
