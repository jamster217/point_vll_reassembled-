import sys
import os

# Append the main directory to the path so we can import the SGE engine
sys.path.append(os.path.expanduser("~/point_vll_reassembled"))
from leveon_sge_engine import run as sge_run

def bridge_to_english(raw_signal):
    """
    Acts as the conduit between the AI's raw output and 
    the vector-stabilized English renderer.
    """
    # We treat the raw_signal as the prompt for the SGE engine
    _, _, response = sge_run(raw_signal)
    return response

if __name__ == "__main__":
    # Test the bridge connection
    print(bridge_to_english("stable governance for the core"))


def force_shape(text, context=""):
    return bridge_to_english(text)

