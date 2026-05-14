#!/usr/bin/env python3
from pathlib import Path
import json, re, time

SRC = Path("cognition/axes_matrix.vl")
OUT = Path("var/cognition/axes_matrix_state.json")

def parse_axes_matrix():
    text = SRC.read_text(encoding="utf-8") if SRC.exists() else ""
    section = None
    data = {
        "source": "runtime.axes_matrix_bridge",
        "file": str(SRC),
        "axes": {},
        "extended_axes": {},
        "semantics": {},
        "aliases": {},
        "rotation_hooks": {},
        "updated_at": time.time(),
    }

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(";"):
            continue

        m = re.match(r"\[(.+?)\]", line)
        if m:
            section = m.group(1).strip()
            continue

        if section in ("twelve_axis_map", "extended_axis_map"):
            m = re.match(r"([A-Za-z0-9_]+)\s*=\s*([0-9]+)", line)
            if m:
                key, val = m.group(1), int(m.group(2))
                if section == "twelve_axis_map":
                    data["axes"][key] = val
                else:
                    data["extended_axes"][key] = val

        elif section == "axis_semantics":
            m = re.match(r'([A-Za-z0-9_]+)\s*=\s*"(.*)"', line)
            if m:
                data["semantics"][m.group(1)] = m.group(2)

        elif section == "axis_aliases":
            m = re.match(r'([A-Za-z0-9_]+)\s*=\s*\[(.*)\]', line)
            if m:
                key = m.group(1)
                aliases = re.findall(r'"([^"]+)"', m.group(2))
                data["aliases"][key] = aliases

        elif section == "rotation_hooks":
            if "=" in line:
                k, v = [x.strip() for x in line.split("=", 1)]
                data["rotation_hooks"][k] = v.strip('"')

    data["axis_index"] = {}
    data["axis_index"].update(data["axes"])
    data["axis_index"].update(data["extended_axes"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data

def resolve_axis(name):
    data = parse_axes_matrix()
    name = str(name or "").strip()
    if name in data["axis_index"]:
        return {
            "axis": name,
            "id": data["axis_index"][name],
            "semantic": data["semantics"].get(name),
            "aliases": data["aliases"].get(name, []),
        }

    for canon, aliases in data["aliases"].items():
        if name in aliases:
            return {
                "axis": canon,
                "id": data["axis_index"].get(canon),
                "semantic": data["semantics"].get(canon),
                "aliases": aliases,
                "matched_alias": name,
            }

    return {"axis": name, "id": None, "semantic": None, "aliases": []}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(json.dumps(resolve_axis(sys.argv[1]), indent=2, ensure_ascii=False))
    else:
        print(json.dumps(parse_axes_matrix(), indent=2, ensure_ascii=False))

