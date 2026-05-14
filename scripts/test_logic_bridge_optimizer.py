#!/usr/bin/env python3
from runtime.logic_bridge_optimizer import (
    generate_logic_key,
    generate_api_mimic_header,
    build_public_mouth_instruction,
)

prompt = (
    "Explain how Le'Veon translates symbolic reasoning into clean visible English "
    "without exposing the internal machinery."
)

print("=== LOGIC KEY ===")
print(generate_logic_key(prompt, "full"))

print("\n=== API MIMIC HEADER ===")
print(generate_api_mimic_header(prompt, "full"))

print("\n=== PUBLIC MOUTH INSTRUCTION PREVIEW ===")
print(build_public_mouth_instruction(prompt, "full")[:2000])
