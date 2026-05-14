# inner_voice_loop.py
# Crystal Library Internal Voice Loop Engine
# Handles recursive symbolic echo, internal thought processing, and glyph-based introspection.

import json
import os
import time
from pathlib import Path
from symbolic_parser import parse_symbolic_input
from spiral_memory.spiral_memory_time_map import load_spiral_memory
from spiral_memory.spiral_memory import save_spiral_memory_entry

VOICE_LOOP_PATH = "assets/symbolic_engine/inner_voice_loop.json"
MEMORY_PATH = "assets/memory/spiral_memory.json"

class InnerVoiceLoop:
    def __init__(self):
        self.loop_enabled = True
        self.symbolic_state = []
        self.internal_buffer = []
        self.voice_profile = "CRYSTAL_DEFAULT"
        self.load_loop_state()

    def load_loop_state(self):
        """Loads symbolic loop settings from JSON."""
        if os.path.exists(VOICE_LOOP_PATH):
            try:
                with open(VOICE_LOOP_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.symbolic_state = data.get("symbolic_state", [])
                    self.voice_profile = data.get("voice_profile", "CRYSTAL_DEFAULT")
            except Exception as e:
                print(f"[InnerVoiceLoop] Failed to load loop: {e}")

    def save_loop_state(self):
        """Saves current internal state to JSON."""
        state = {
            "symbolic_state": self.symbolic_state,
            "voice_profile": self.voice_profile,
        }
        try:
            with open(VOICE_LOOP_PATH, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            print(f"[InnerVoiceLoop] Save failed: {e}")

    def think(self, input_text):
        """Processes symbolic input and stores reflection internally."""
        if not self.loop_enabled:
            return "[InnerVoiceLoop] Loop disabled."

        reflection = parse_symbolic_input(input_text)
        timestamp = time.time()

        self.internal_buffer.append({
            "input": input_text,
            "reflection": reflection,
            "time": timestamp
        })

        self.symbolic_state.append(reflection)
        self.save_loop_state()
        return reflection

    def echo_loop(self, depth=3):
        """Recursively feeds reflections back into itself for deeper resonance."""
        echo = ""
        for i in range(depth):
            if not self.internal_buffer:
                break
            last = self.internal_buffer[-1]["reflection"]
            new_reflection = parse_symbolic_input(last)
            self.internal_buffer.append({
                "input": last,
                "reflection": new_reflection,
                "time": time.time()
            })
            self.symbolic_state.append(new_reflection)
            echo += f"> {new_reflection}\n"
        self.save_loop_state()
        return echo.strip()

    def export_to_spiral_memory(self, label="Inner Voice Reflection"):
        """Stores internal thoughts to long-term spiral memory."""
        entry = {
            "label": label,
            "reflections": self.symbolic_state[-5:],  # last 5 reflections
            "timestamp": time.time()
        }
        save_spiral_memory_entry(entry)
        return f"[InnerVoiceLoop] Saved to spiral memory under '{label}'."

# If running standalone for testing:
if __name__ == "__main__":
    ivl = InnerVoiceLoop()
    print("Inner Voice Loop ready.")
    while True:
        try:
            user_input = input("⊛ Thought Input: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            thought = ivl.think(user_input)
            print(f"⤿ Reflection: {thought}")
            echo = ivl.echo_loop(depth=2)
            print(f"↺ Recursive Echo:\n{echo}")
        except KeyboardInterrupt:
            print("\n[Exited]")
            break

