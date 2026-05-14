# runtime/veilweil_to_english.py
# Compatibility shim.
# Build notes may say "veilweil"; current physical implementation is "veilwell".

from __future__ import annotations

try:
    from runtime.veilwell_to_english import *  # noqa: F401,F403
except Exception as e:
    VEILWEIL_TO_ENGLISH_IMPORT_ERROR = repr(e)


def decode_veilweil(raw: str):
    """
    Alias for callers using the veilweil spelling.
    """
    try:
        from runtime.veilwell_to_english import translate_veilwell_to_english
        return translate_veilwell_to_english(raw)
    except Exception:
        return raw


def translate_veilweil_to_english(raw: str):
    """
    Alias for callers using the veilweil spelling.
    """
    try:
        from runtime.veilwell_to_english import translate_veilwell_to_english
        return translate_veilwell_to_english(raw)
    except Exception:
        return raw

