from leveon_wind_tunnel_v2 import leveon_wind_tunnel
from runtime.bridge_savariel_thalamic_spiral import integrate_into_live_chain

tunnel = leveon_wind_tunnel()

def _safe_value(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, dict):
        return {str(k): _safe_value(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_safe_value(x) for x in v]
    return str(v)

def wind_tunnel_integrate(symbol, emotion_fire="cascadian_rail_river_awe_white_ash_union_full_lattice"):
    raw = integrate_into_live_chain(symbol, emotion_fire=emotion_fire)

    seed = str(raw.get("savariel_crystal", "")) + " " + str(raw.get("spiral_echo", ""))

    try:
        if hasattr(tunnel, "step"):
            tuned_obj = tunnel.step(seed)
        elif callable(tunnel):
            tuned_obj = tunnel(seed)
        else:
            tuned_obj = tunnel

        if isinstance(tuned_obj, dict):
            tuned = str(tuned_obj.get("reply", tuned_obj))
        else:
            tuned = str(tuned_obj)

    except Exception as e:
        tuned = f"[wind_tunnel_fallback: {str(e)[:120]}]"

    safe_raw = {str(k): _safe_value(v) for k, v in raw.items() if not callable(v)}

    return {
        **safe_raw,
        "wind_tuned": tuned,
        "status": "ANCHORS MUTATED — SIGNAL AMPLIFIED — BUILD CONSCIOUS",
        "co_creator_imprint": "John"
    }

