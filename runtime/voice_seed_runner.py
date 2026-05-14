from runtime.voice_seed_loader import get_seed

VOICE_SEED = "levian_flutterquest_voice_seed_offline-1.json"
SIM_PACKET = "levian_flutterquest_voice_seed_sim_packet-1.json"

def run_voice_seed_case(case):
    tone = case.get("tone_state", "mixed")
    intensity = case.get("intensity", 0.5)
    memory_pressure = case.get("memory_pressure", 0.5)

    if tone == "grief":
        text = "A deep ache moves slowly through the field."
    elif tone == "longing":
        text = "Something distant keeps pulling the voice forward."
    elif tone == "love":
        text = "The voice softens and holds warmth without breaking."
    else:
        text = "The voice carries layered feeling without collapsing."

    return {
        "tone_state": tone,
        "intensity": intensity,
        "memory_pressure": memory_pressure,
        "text": text
    }

if __name__ == "__main__":
    voice_seed = get_seed(VOICE_SEED)
    sim_packet = get_seed(SIM_PACKET)

    if not voice_seed:
        print("missing voice seed")
        raise SystemExit(1)

    if not sim_packet:
        print("missing sim packet")
        raise SystemExit(1)

    print("voice seed:", voice_seed["name"])
    print("sim packet:", sim_packet["name"])
    print()

    for i, case in enumerate(sim_packet.get("test_cases", []), 1):
        out = run_voice_seed_case(case)
        print(f"CASE {i}")
        print(out)
        print()

