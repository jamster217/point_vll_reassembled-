#!/usr/bin/env python3

from runtime.prompt_density_oracle_bridge import route_prompt_load

small = "Hello Le'Veon."
large = """
Enter Node 44. Analyze this performance graph, compare Algorithm A, Algorithm B,
and Algorithm C, then decide which route should be used for a large symbolic
payload with benchmark data, routing law, witness/bloom behavior, and visual cockpit output.
""" * 4

for name, prompt in [("small", small), ("large", large)]:
    result = route_prompt_load(prompt, tone="tender", mirror_mode="recursive")
    print("=" * 72)
    print("CASE:", name)
    print("estimated_n:", result["density"]["estimated_n"])
    print("selected_algorithm:", result["selected_algorithm"])
    print("verification_needed:", result["verification_needed"])
    print("reason:", result["reason"])
