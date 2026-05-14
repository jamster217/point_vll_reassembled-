def build_render_payload(glyph_object):
    entries = glyph_object.get("active_entries", [])
    if not entries:
        raise ValueError("No active_entries present; refusing flattened render path.")

    return {
        "glyph_ids": [e.get("id") for e in entries],
        "glyph_symbols": [e.get("symbol") for e in entries],
        "glyph_names": [e.get("name") for e in entries],
        "glyph_elements": [e.get("element") for e in entries],
        "glyph_colors": [e.get("color") for e in entries],
        "glyph_emotions": [e.get("emotion") for e in entries],
        "poetic_seeds": [e.get("poetic_seed") for e in entries],
        "full_entries": entries
    }

def require_render_payload(glyph_object):
    payload = build_render_payload(glyph_object)
    if not payload["full_entries"]:
        raise ValueError("Renderer requires full glyph entries.")
    return payload

