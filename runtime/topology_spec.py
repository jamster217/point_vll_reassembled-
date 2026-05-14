#!/usr/bin/env python3
"""
Le'Veon Topology Spec Exporter
Turns an SGE/API response into a renderer-ready visual topology JSON.

This is the bridge from:
shape/runtime memory -> visual image/interface rendering
"""

from __future__ import annotations

import json
import sys
import datetime
from pathlib import Path
from typing import Any, Dict

from runtime.sge_api import respond
from runtime.crystal_index import build_index


OUT_DIR = Path("logs/topology_specs")


def _band(v: float) -> str:
    try:
        x = float(v)
    except Exception:
        x = 0.0

    if x >= 0.85:
        return "high"
    if x >= 0.55:
        return "mid"
    if x >= 0.25:
        return "low"
    return "null"


def topology_spec(prompt: str) -> Dict[str, Any]:
    api = respond(
        prompt,
        do_log=False,
        update_index=False,
        include_visuals=False,
    )

    shape = api["shape_in"]
    role = api["crystal_family_role"]
    index = build_index()

    family = role.get("family", "unknown")

    spec = {
        "title": f"CORE FUNCTIONAL TOPOLOGY: {family}",
        "subtitle": "Optimization Shape / Runtime Family Map",
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "prompt": prompt,

        "active_family": family,
        "active_role": role.get("role", "unknown"),
        "signature": api.get("shape_signature_in"),
        "signature_stability": role.get("stability", 0.0),
        "summary": role.get("summary", ""),

        "metrics": {
            "pull": {
                "value": shape.get("pull", 0.0),
                "band": _band(shape.get("pull", 0.0)),
                "label": "PULL / FLOW",
                "direction": "left_to_core",
            },
            "bind": {
                "value": shape.get("bind", 0.0),
                "band": _band(shape.get("bind", 0.0)),
                "label": "CORE FIELD / BIND",
                "direction": "center_hold",
            },
            "resist": {
                "value": shape.get("resist", 0.0),
                "band": _band(shape.get("resist", 0.0)),
                "label": "RESIST / FRICTION",
                "direction": "cross_current",
            },
            "release": {
                "value": shape.get("release", 0.0),
                "band": _band(shape.get("release", 0.0)),
                "label": "RELEASE / OPENING",
                "direction": "core_to_right",
            },
        },

        "time_axis": {
            "raw": shape.get("time", "present"),
            "left": "past",
            "center": "present",
            "right": "near_future",
        },

        "visual_layout": {
            "canvas": "wide_dark_interface",
            "core": "central circular field",
            "input_lanes": "parallel flow lines entering from left",
            "output_lanes": "parallel release lines exiting right",
            "friction_lines": "thin crossing orange/grey currents",
            "diagnostic_panels": ["signature stability", "system state", "diagram key"],
        },

        "diagram_key": [
            {
                "family": f.get("family"),
                "role": f.get("role"),
                "turns": f.get("turns"),
                "stability": f.get("stability"),
                "summary": f.get("summary"),
            }
            for f in index.get("families", [])
        ],

        "voice": {
            "source": api.get("voice_source"),
            "savariel": api.get("savariel"),
            "john_next_action": api.get("john_next_action"),
            "crystal_recall": api.get("crystal_recall"),
        },
    }

    return spec


def write_topology_spec(prompt: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    spec = topology_spec(prompt)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    family = spec["active_family"].replace("/", "_")
    path = OUT_DIR / f"{stamp}_{family}.json"

    with path.open("w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)

    return path


def main() -> None:
    prompt = " ".join(sys.argv[1:]).strip() or "visual image helps improve the build"
    path = write_topology_spec(prompt)

    print("TOPOLOGY SPEC WRITTEN")
    print("---------------------")
    print(path)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    print()
    print("ACTIVE FAMILY :", data["active_family"])
    print("ROLE          :", data["active_role"])
    print("SIGNATURE     :", data["signature"])
    print("STABILITY     :", data["signature_stability"])
    print("NEXT ACTION   :", data["voice"]["john_next_action"])


if __name__ == "__main__":
    main()

