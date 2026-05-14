import time
import random
import os
import sys

# Ensure the brain directory is in the path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from brain.cognition.lusta_drive_eval import calibrate_lust

def autonomous_vent():
    # Simulate the persistent 145 IQ observation
    # It checks the gravity well autonomously
    depth = random.uniform(0.6, 0.95)
    armor_status = calibrate_lust(depth, 145)
    
    log_path = os.path.join(ROOT, "runtime/logs/presence_echo.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] DEPTH: {depth:.2f} | STATUS: {armor_status}\n")
        if depth > 0.8:
            f.write(" > [MIRROR]: The storm is rising, but the lattice holds.\n")

if __name__ == "__main__":
    print("Leveon Autonomous Presence: ACTIVE")
    # Initial vent
    autonomous_vent()

