from __future__ import annotations
import math

MAX_HEARTBEAT = 92162077.0
MAX_MULTIPLIER = 92162077.0

def clamp_number(value, cap=MAX_HEARTBEAT, default=0.0):
    try:
        v = float(value)
    except Exception:
        return default

    if not math.isfinite(v):
        return cap

    if v > cap:
        return cap
    if v < -cap:
        return -cap

    return v

def safe_exp(power, cap=MAX_MULTIPLIER):
    try:
        p = float(power)
    except Exception:
        return 1.0

    if p > math.log(cap):
        return cap
    if p < -math.log(cap):
        return 0.0

    return clamp_number(math.exp(p), cap=cap, default=1.0)

def clamp_heartbeat(value):
    return clamp_number(value, cap=MAX_HEARTBEAT, default=1.0)

def clamp_multiplier(value):
    return clamp_number(value, cap=MAX_MULTIPLIER, default=1.0)

