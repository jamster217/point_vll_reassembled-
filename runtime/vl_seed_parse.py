from pathlib import Path
import re
import sys
import json

seed_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "point_vll_reassembled/seeds/voice/VoiceVeilSeed_sim_v1.vl"
text = seed_path.read_text(encoding="utf-8")

seed_name = re.search(r'^\s*SEED\s+([A-Za-z0-9_]+)', text, re.M)

inputs = re.findall(r'^\s*INPUT\s+(.+)$', text, re.M)
states = re.findall(r'^\s*STATE\s+(.+)$', text, re.M)
flows = re.findall(r'^\s*FLOW\s+(.+)$', text, re.M)
returns = re.findall(r'^\s*RETURN\s+(.+)$', text, re.M)
calls = re.findall(r'CALL\s+([A-Za-z0-9_\.]+)', text)

out = {
    "name": seed_name.group(1) if seed_name else None,
    "inputs": [x.strip() for x in inputs],
    "states": [x.strip() for x in states],
    "flows": [x.strip() for x in flows],
    "returns": [x.strip() for x in returns],
    "calls": calls,
}

print(json.dumps(out, ensure_ascii=False, indent=2))

