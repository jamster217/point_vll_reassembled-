from pathlib import Path
import re
import sys
import json
import importlib

SEED_ROOT = Path.home() / "point_vll_reassembled" / "seeds"

def resolve_seed_path(call_target: str):
    if not call_target.startswith("seeds."):
        return None
    parts = call_target.split(".")[1:]
    rel = Path(*parts).with_suffix(".vl")
    return SEED_ROOT / rel

def parse_seed(seed_path: Path):
    text = seed_path.read_text(encoding="utf-8")

    seed_name = re.search(r'^\s*SEED\s+([A-Za-z0-9_]+)', text, re.M)
    input_line = re.search(r'^\s*INPUT\s+(.+)$', text, re.M)
    state_line = re.search(r'^\s*STATE\s+(.+)$', text, re.M)
    flow_line = re.search(r'^\s*FLOW\s+(.+)$', text, re.M)
    return_line = re.search(r'^\s*RETURN\s+(.+)$', text, re.M)
    call_line = re.search(r'CALL\s+([A-Za-z0-9_\.]+)\s+WITH\s+([A-Za-z0-9_]+)', text)

    return {
        "seed": seed_name.group(1) if seed_name else None,
        "input_name": input_line.group(1).strip() if input_line else None,
        "state": state_line.group(1).strip() if state_line else None,
        "flow": flow_line.group(1).strip() if flow_line else None,
        "call_target": call_line.group(1) if call_line else None,
        "call_arg": call_line.group(2) if call_line else None,
        "return": return_line.group(1).strip() if return_line else None,
    }

def try_external_call(call_target: str, raw_input):
    if not (call_target.startswith("modules.") or call_target.startswith("runtime.")):
        return {"status": "unresolved"}

    parts = call_target.split(".")
    if len(parts) < 3:
        return {"status": "bad_target", "target": call_target}

    module_name = ".".join(parts[:-1])
    func_name = parts[-1]

    try:
        mod = importlib.import_module(module_name)
    except Exception as e:
        return {
            "status": "import_failed",
            "target": call_target,
            "module": module_name,
            "error": str(e),
        }

    fn = getattr(mod, func_name, None)
    if not callable(fn):
        return {
            "status": "function_missing",
            "target": call_target,
            "module": module_name,
            "function": func_name,
        }

    try:
        result = fn(raw_input)
        return {
            "status": "ok",
            "target": call_target,
            "module": module_name,
            "function": func_name,
            "result": result,
        }
    except Exception as e:
        return {
            "status": "call_failed",
            "target": call_target,
            "module": module_name,
            "function": func_name,
            "error": str(e),
        }

def exec_seed(seed_path: Path, raw_input, depth=0, max_depth=5):
    info = parse_seed(seed_path)
    trace = [
        f"seed_loaded:{info['seed']}",
        "input_bound",
        f"flow_entered:{info['flow']}",
    ]

    nested = None
    external = None
    call_target = info.get("call_target")

    if call_target:
        trace.append(f"call_resolved:{call_target}")
        nested_path = resolve_seed_path(call_target)

        if nested_path and nested_path.exists() and depth < max_depth:
            nested = exec_seed(nested_path, raw_input, depth + 1, max_depth)
            trace.append(f"seed_call_completed:{nested.get('seed')}")
        elif call_target.startswith("modules.") or call_target.startswith("runtime."):
            external = try_external_call(call_target, raw_input)
            trace.append(f"external_call_status:{external['status']}")
        elif nested_path and not nested_path.exists():
            trace.append("seed_call_missing")
        else:
            trace.append("external_call_unresolved")
    else:
        trace.append("no_call_found")

    trace.append("return_prepared")

    out = {
        "seed": info["seed"],
        "input_name": info["input_name"],
        "input_value": raw_input,
        "state": info["state"],
        "flow": info["flow"],
        "call_target": info["call_target"],
        "call_arg": info["call_arg"],
        "return": info["return"],
        "execution_trace": trace
    }

    if nested:
        out["nested"] = nested
    if external:
        out["external"] = external

        ext_result = external.get("result")
        if isinstance(ext_result, dict):
            for key, value in ext_result.items():
                if key not in out:
                    out[key] = value

            if "best_route" in ext_result:
                out["best_route"] = ext_result["best_route"]
            if "weakest_route" in ext_result:
                out["weakest_route"] = ext_result["weakest_route"]
            if "ranked_routes" in ext_result:
                out["ranked_routes"] = ext_result["ranked_routes"]

            if "simulation_packet" in ext_result:
                out["simulation_packet"] = ext_result["simulation_packet"]
            if "transition_packet" in ext_result:
                out["transition_packet"] = ext_result["transition_packet"]
            if "final_packet" in ext_result:
                out["final_packet"] = ext_result["final_packet"]
            if "comparison_packet" in ext_result:
                out["comparison_packet"] = ext_result["comparison_packet"]
            elif "best_route" in ext_result or "weakest_route" in ext_result:
                out["comparison_packet"] = ext_result

    return out

if __name__ == "__main__":
    seed_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "point_vll_reassembled/seeds/BuildOptimizerBridge_v1.vl"
    raw_input = sys.argv[2] if len(sys.argv) > 2 else "compiler_design"
    result = exec_seed(seed_path, raw_input)
    print(json.dumps(result, ensure_ascii=False, indent=2))

