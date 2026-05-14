import re

def _clean(x):
    return str(x).replace("-", " ")

def _join(items):
    items = [_clean(x) for x in items if x]
    if not items:
        return "meaning"
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def shape_from_prompt(user_text, pulse_context=""):
    from runtime.birth_point_mapper import build_birth_packet
    packet = build_birth_packet(user_text, pulse_context=pulse_context)
    return {
        "subject": packet.get("subject", "empty"),
        "atoms": packet.get("atoms", []),
        "relations": packet.get("relations", []),
        "pressure": "continuity" if packet.get("pulse_continuity") else "attention",
        "movement": "carries_previous_state_forward" if packet.get("pulse_continuity") else "current_prompt_only",
        "density": packet.get("meaning_density", 0.0),
    }

def realize_from_birth_packet(packet):
    route = packet.get("route", "definition")
    subject = packet.get("subject", "this")
    obj = packet.get("object", "")
    relations = packet.get("relations", [])
    rel = _join(relations)
    density = packet.get("meaning_density", 0.0)

    if subject == "empty":
        return "Give me a little more signal and I’ll shape it into plain English."

    if route == "relationship" and obj:
        return (
            f"{subject.capitalize()} and {obj} meet through {rel}. "
            f"The useful point is not that they are the same, but that they shape each other through that shared pressure."
        )

    if route == "mechanism":
        return (
            f"{subject.capitalize()} works by carrying {rel} through a changing situation. "
            f"It becomes clearer when you watch what it preserves and what it transforms."
        )

    if route == "status":
        return (
            f"{subject.capitalize()} is currently organized around {rel}. "
            f"The shape is dense enough to speak directly, so the mouth only needs to realize it."
        )

    if route == "cause":
        return (
            f"{subject.capitalize()} arises when {rel} becomes strong enough to organize the situation. "
            f"That pressure gives the answer its direction."
        )

    return (
        f"{subject.capitalize()} is {rel} taking form. "
        f"At density {density}, the answer should stay direct instead of wandering."
    )

def realize(user_text, pulse_context="", wind_signal="", show_shape=False, birth_packet=None):
    if birth_packet is None:
        from runtime.birth_point_mapper import build_birth_packet
        birth_packet = build_birth_packet(user_text, pulse_context=pulse_context)

    english = realize_from_birth_packet(birth_packet)

    if not show_shape:
        return english

    return (
        "BIRTH_SHAPE:\n"
        f"route={birth_packet.get('route')}\n"
        f"subject={birth_packet.get('subject')}\n"
        f"object={birth_packet.get('object')}\n"
        f"atoms={birth_packet.get('atoms')}\n"
        f"relations={birth_packet.get('relations')}\n"
        f"meaning_density={birth_packet.get('meaning_density')}\n"
        f"high_speed={birth_packet.get('high_speed_realization')}\n"
        f"shape_answer={birth_packet.get('shape_answer')}\n\n"
        "ENGLISH:\n"
        f"{english}"
    )

def grammar_candidates(user_text, pulse_context="", wind_signal="", birth_packet=None):
    if birth_packet is None:
        from runtime.birth_point_mapper import build_birth_packet
        birth_packet = build_birth_packet(user_text, pulse_context=pulse_context)

    base = realize_from_birth_packet(birth_packet)
    subject = birth_packet.get("subject", "this")
    rel = _join(birth_packet.get("relations", []))

    return [
        ("birth_direct", base, birth_packet),
        ("birth_compact", f"{subject.capitalize()}: {rel}. The shape is already dense, so the answer stays direct.", birth_packet),
        ("birth_pressure", f"The pressure in {subject} gathers around {rel}, then resolves into plain English.", birth_packet),
    ]

