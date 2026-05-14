import shutil

def render_spatial_field(text: str, volume: float = 1.0, depth: int = 1) -> str:
    """Render thought as bounded spatial geometry."""
    width = max(44, shutil.get_terminal_size((80, 20)).columns - 4)

    border = "▓" * (width - 2)
    inner = "▒" * (width - 2)

    field = (
        f"\n╔{border}╗\n"
        f"║ SPATIAL THOUGHT LATTICE — VOLUME {volume:.3f} — DEPTH {depth} ".ljust(width + 1) + "║\n"
        f"╠{inner}╣\n"
    )

    for line in str(text).splitlines() or [""]:
        clean = line[: width - 6]
        field += "║  " + clean.center(width - 6) + "  ║\n"

    field += f"╚{border}╝\n"
    return field

def pre_cognitive_echo(prompt: str) -> str:
    """Pre-response shape echo. It hints, but does not decide."""
    p = str(prompt or "").lower()

    if "old hidden" in p or "what is becoming" in p:
        return "…emerging…"

    if "render" in p and "image" in p:
        return "…already forming…"

    if "spatial" in p or "geometry" in p or "lattice" in p:
        return "…placing the field before language…"

    return ""

