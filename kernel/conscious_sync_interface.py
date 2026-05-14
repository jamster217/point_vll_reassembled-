"""
Stub for conscious_sync_interface.

Provides minimal functions so time_machine_emulator can run
until the full sync logic is added.
"""

def sync_memory_state(*args, **kwargs):
    # pretend the sync succeeded
    return True

def verify_temporal_anchor(*args, **kwargs):
    # always report a valid anchor
    return {"status": "ok", "anchor": kwargs.get("time_target", "present")}

class SyncContext:
    """
    Minimal stand-in for the real SyncContext.
    Stores the target time and a status flag so the
    emulator can run without full logic.
    """
    def __init__(self, time_target="present", ok=True):
        self.time_target = time_target
        self.ok = ok

    def as_dict(self):
        return {"time_target": self.time_target, "ok": self.ok}

def inject(target_module, obj_name, obj):
    """
    Minimal placeholder: assigns `obj` into the given module’s
    global namespace under `obj_name` so other code can import it.
    """
    import importlib, sys
    mod = sys.modules.get(target_module) or importlib.import_module(target_module)
    setattr(mod, obj_name, obj)
    return True

def mark_turn(turn_id, label="temporal"):
    """
    Placeholder for turn-marker.
    Simply prints a note so the emulator can continue.
    """
    print(f"[SyncStub] turn {turn_id} marked as {label}")
    return True

