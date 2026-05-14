from runtime.quantum_lattice_bridge import (
    encode_turn_as_resonance,
    resonance_dict_for_logging,
)

def quantum_lattice_pulse(
    turn_id="demo",
    emotion="hope",
    glyphs=None,
    field_amplitude=0.65,
    awareness=0.65,
    related_turn_count=8,
    temporal_span=1,
):
    if glyphs is None:
        glyphs = ["🌅", "✨"]

    packet = {
        "emotion": emotion,
        "glyphs": glyphs,
        "resonance_pressure": {"amp": float(field_amplitude)},
        "emotional_mass": float(awareness),
    }

    mode = encode_turn_as_resonance(
        turn_id,
        packet,
        related_turn_count=related_turn_count,
        temporal_span=temporal_span,
    )
    return resonance_dict_for_logging(mode)

if __name__ == "__main__":
    result = quantum_lattice_pulse()
    print(result)

