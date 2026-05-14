# runtime/veilweil_translator.py
# Compatibility shim.
# Routes old veilweil translator calls to the current veilwell_to_english implementation.

from __future__ import annotations

try:
    from runtime.veilwell_to_english import *  # noqa: F401,F403
except Exception as e:
    VEILWEIL_TRANSLATOR_IMPORT_ERROR = repr(e)


def translate(raw: str):
    try:
        from runtime.veilwell_to_english import translate_veilwell_to_english
        return translate_veilwell_to_english(raw)
    except Exception:
        return raw


def to_english(raw: str):
    return translate(raw)


def decode(raw: str):
    return translate(raw)

