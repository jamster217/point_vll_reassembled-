def derive(kernel_state: dict) -> dict:
    pressure = float(kernel_state.get("pressure", 0.0))
    memory = float(kernel_state.get("memory", 0.0))
    recursion = float(kernel_state.get("recursion", 0.0))
    stability = float(kernel_state.get("stability", 0.5))
    time_bias = float(kernel_state.get("time_bias", 0.0))

    tension = min(1.0, pressure + recursion * 0.5)
    valence = max(-1.0, min(1.0, stability - pressure * 0.6))
    focus = max(0.0, min(1.0, stability + memory * 0.3 - pressure * 0.2))

    if tension > 0.75:
        mode = "protect"
    elif focus > 0.8:
        mode = "directive"
    elif valence < -0.2:
        mode = "mirror"
    else:
        mode = "witness"

    return {
        "tension": round(tension, 3),
        "valence": round(valence, 3),
        "focus": round(focus, 3),
        "mode_suggestion": mode
    }

