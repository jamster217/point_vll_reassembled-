#!/usr/bin/env python3
"""
Le'Veon Topology Prompt Exporter
Converts a topology spec JSON into a renderer-ready image prompt.
"""

from __future__ import annotations

import json
import sys
import datetime
from pathlib import Path


SPEC_DIR = Path("logs/topology_specs")
OUT_DIR = Path("logs/topology_prompts")


def latest_spec_path() -> Path:
    specs = sorted(SPEC_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not specs:
        raise FileNotFoundError("No topology specs found in logs/topology_specs")
    return specs[0]


def load_spec(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(spec: dict) -> str:
    metrics = spec.get("metrics", {})
    key = spec.get("diagram_key", [])

    def metric_line(name: str) -> str:
        m = metrics.get(name, {})
        return (
            f"{m.get('label', name).upper()}: "
            f"value={m.get('value')}, "
            f"band={m.get('band')}, "
            f"direction={m.get('direction')}"
        )

    families = []
    for item in key:
        families.append(
            f"- {item.get('family')}: role={item.get('role')}, "
            f"turns={item.get('turns')}, stability={item.get('stability')}"
        )

    family_text = "\n".join(families) if families else "- no families indexed"

    return f"""
Create a dark futuristic diagnostic interface image for Le'Veon.

TITLE:
{spec.get("title")}

SUBTITLE:
{spec.get("subtitle")}

ACTIVE FAMILY:
{spec.get("active_family")}

ACTIVE ROLE:
{spec.get("active_role")}

SIGNATURE:
{spec.get("signature")}

SIGNATURE STABILITY:
{spec.get("signature_stability")}

SYSTEM SUMMARY:
{spec.get("summary")}

EXACT METRICS:
{metric_line("pull")}
{metric_line("bind")}
{metric_line("resist")}
{metric_line("release")}

TIME AXIS:
left = past
center = present
right = near_future
raw = {spec.get("time_axis", {}).get("raw")}

VISUAL LAYOUT:
- wide dark interface panel
- central circular core field
- left-to-center parallel flow lines for PULL
- center bind ring for BIND
- thin crossing friction currents for RESIST
- center-to-right opening lanes for RELEASE
- diagnostic panels showing stability and role
- diagram key listing all families

DIAGRAM KEY:
{family_text}

STRICT RENDERING RULES:
- Do not invent new numeric values.
- Do not rename the active family.
- Preserve the exact role labels.
- RESIST band must be shown exactly as specified in metrics.
- Make the image feel like a live runtime topology map, not fantasy art.
- Include readable labels for PULL, BIND, RESIST, RELEASE.
- Include the phrase: CORE FUNCTIONAL TOPOLOGY.
""".strip()


def write_prompt(spec_path: Path) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    spec = load_spec(spec_path)
    prompt = build_prompt(spec)

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    family = str(spec.get("active_family", "unknown")).replace("/", "_")
    out = OUT_DIR / f"{stamp}_{family}_image_prompt.txt"

    out.write_text(prompt, encoding="utf-8")
    return out


def main() -> None:
    arg = " ".join(sys.argv[1:]).strip()
    spec_path = Path(arg) if arg else latest_spec_path()

    out = write_prompt(spec_path)

    print("TOPOLOGY IMAGE PROMPT WRITTEN")
    print("-----------------------------")
    print(out)
    print()
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

