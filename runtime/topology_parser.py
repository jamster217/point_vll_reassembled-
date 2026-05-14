import re
from typing import Dict

def parse_topology_spec(text: str) -> Dict:
    """
    Extracts core topology values from a visual/spec description.
    Keeps meaning tight — no guessing beyond what’s present.
    """

    def extract(pattern, default=0.0):
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except:
                return default
        return default

    topology = {
        "pull": extract(r"pull[^0-9]*([0-9.]+)"),
        "bind": extract(r"bind[^0-9]*([0-9.]+)"),
        "release": extract(r"release[^0-9]*([0-9.]+)"),
        "resist": extract(r"resist[^0-9]*([0-9.]+)"),
        "stability": extract(r"stability[^0-9]*([0-9.]+)"),
    }

    # derive simple state
    topology["flow_balance"] = round(
        (topology["pull"] + topology["release"]) / 2, 3
    )

    topology["friction"] = topology["resist"]

    if topology["release"] > topology["bind"]:
        topology["mode"] = "opening"
    elif topology["bind"] > topology["release"]:
        topology["mode"] = "holding"
    else:
        topology["mode"] = "neutral"

    return topology


def describe_topology(topology: Dict) -> str:
    """
    Turns parsed structure into a clean, dense line (not fluffy).
    """

    return (
        f"flow={topology['flow_balance']}, "
        f"bind={topology['bind']}, "
        f"release={topology['release']}, "
        f"resist={topology['resist']}, "
        f"mode={topology['mode']}"
    )

