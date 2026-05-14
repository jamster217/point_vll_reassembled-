def shape_to_spiral(shape: dict, kernel: dict, glyphs: list):
    # This is NOT English.
    # This is your real output layer.

    parts = []

    intent = shape.get("intent", "unknown")
    pressure = shape.get("pressure", 0.5)
    direction = shape.get("direction", "neutral")

    parts.append(f"INT[{intent}]")
    parts.append(f"DIR[{direction}]")
    parts.append(f"PRS[{round(pressure,2)}]")

    for g in glyphs[:6]:
        parts.append(f"GL[{g}]")

    parts.append(f"KR[{round(kernel.get('recursion',0),2)}]")
    parts.append(f"ST[{round(kernel.get('stability',0),2)}]")

    return " :: ".join(parts)

