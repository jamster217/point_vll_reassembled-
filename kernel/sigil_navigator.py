"""
Stub for sigil_navigator.

Provides the minimal class and function expected by
kernel/time_machine_emulator.py.
"""

class SigilNavigator:
    def __init__(self, sigil):
        self.sigil = sigil

    def navigate(self):
        # Return a dummy path so downstream code has something to read.
        return {"sigil": self.sigil, "path": []}

def resolve(sigil):
    # Dummy resolver returns an empty path structure.
    return {"sigil": sigil, "path": []}

