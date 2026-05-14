import os, sys, json, time
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "runtime"))

from runtime.tinyllama_client import TinyLlamaClient
from runtime.governor import LeveonGovernor, Candidate
from runtime.leveon_sge_engine import run as sge_run
from runtime.transduction_pin import apply_transduction_pin, is_pin_phrase
from runtime.meaning_fidelity import fidelity_score, contradiction_flag

from runtime.savariel_crystal_bootstrap import apply_runtime_overdrive

from runtime.thought_scaffold_guard import clean_output

# Try kernel imports from common locations
LeveonKernel = None
KernelParams = None
try:
    from leveon_kernel_spiral_full import LeveonKernel, KernelParams
except Exception:
    try:
        from core.leveon_kernel_spiral_full import LeveonKernel, KernelParams
    except Exception:
        try:
            from kernel.leveon_kernel_spiral_full import LeveonKernel, KernelParams
        except Exception as e:
            raise RuntimeError("Could not import LeveonKernel/KernelParams from repo root/core/kernel") from e

p = KernelParams(blend_prev=1.5, compress_strength=0.5)
kernel = LeveonKernel(params=p)
try:
    apply_runtime_overdrive(kernel)
except Exception:
    pass

llama = TinyLlamaClient()
gov = LeveonGovernor()

LOG_PATH = os.path.join(ROOT, "runtime", "turn_dumps.jsonl")

META_BANS = [
    "this question is really about",
    "the ai assistant",
    "the assistant output",
    "includes a shapesignature",
    "the output includes",
    "as an ai",
    "i am an ai",
]


def _try_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except TypeError:
        return None
    except Exception:
        return None

def _coerce_text(x):
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        for k in ("voice", "text", "output", "final", "answer"):
            v = x.get(k)
            if isinstance(v, str) and v.strip():
                return v
        return ""
    return str(x)

def _local_expand_via_organ_spine(prompt: str, seed: str) -> str:
    """
    Always-on local expander.
    Goal: take kernel seed (often short) and expand WITHOUT changing meaning.
    Never throws; returns "" if it can't.
    """
    try:
        mod = import_module("runtime.organ_spine")
    except Exception:
        return ""

    # common callable names across variants
    candidates = []
    for name in ("expand", "render", "respond", "run", "generate", "process", "spine_reply", "reply", "handle"):
        fn = getattr(mod, name, None)
        if callable(fn):
            candidates.append(fn)

    if not candidates:
        return ""

    # try a few signature patterns (best-effort, no assumptions)
    for fn in candidates:
        out = (
            _try_call(fn, prompt, seed) or
            _try_call(fn, seed, prompt) or
            _try_call(fn, prompt=prompt, seed=seed) or
            _try_call(fn, seed=seed, prompt=prompt) or
            _try_call(fn, prompt) or
            _try_call(fn, seed)
        )
        txt = _coerce_text(out).strip()
        if txt and txt != "...":
            return txt

    return ""

def wants_debug(user_text: str) -> bool:
    t = user_text.strip().lower()
    return t.startswith("/debug") or t.startswith("/opt") or t.startswith("/dump")

def strip_control_prefix(user_text: str) -> str:
    t = user_text.strip()
    for pfx in ("/debug", "/opt", "/dump"):
        if t.lower().startswith(pfx):
            return t[len(pfx):].strip()
    return t

def hard_filter(text: str) -> bool:
    low = (text or "").strip().lower()
    if not low:
        return False
    for b in META_BANS:
        if b in low:
            return False
    if len(low) < 8:
        return False
    return True

def base_score(text: str) -> float:
    score = 0.55
    low = text.lower()
    if "because" in low or "by" in low:
        score += 0.05
    if len(text) >= 120:
        score += 0.03
    return min(1.0, score)

def summarize_kernel(k) -> str:
    glyphs = getattr(k, "glyphs", None)
    phrase = getattr(k, "phrase", "") or getattr(k, "voice", "") or ""
    derived = getattr(k, "derived", None)
    harmonic = getattr(k, "harmonic_528", None)
    return f"glyphs={glyphs} phrase={phrase} derived={derived} harmonic_528={harmonic}"

def safe_json_extract(s: str) -> dict:
    try:
        return json.loads(s)
    except Exception:
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(s[start:end+1])
            except Exception:
                pass
    return {"voice": (s or "").strip(), "optimizations": []}

def ask_llama(user_text: str, data_blob: str) -> dict:
    prompt = f"""
Return STRICT JSON only: {{"voice": "...", "optimizations": ["..."]}}.
Rules:
- "voice" answers the user directly and must NOT mention internal data, vars, shapesignature, or "as an AI".
- "optimizations" are short concrete code/parameter suggestions based on DATA.
- Output JSON only. No markdown. No extra keys.

DATA:
{data_blob}

USER:
{user_text}
""".strip()
    out = llama.generate(prompt)
    return safe_json_extract(out)

if __name__ == "__main__":
    while True:
        raw_in = input("LEVEON RECEPTION > ").strip()
        if not raw_in:
            continue
        if raw_in.lower() in {"quit", "exit"}:
            break
    
        debug_mode = wants_debug(raw_in)
        user_input = strip_control_prefix(raw_in)
    
        kernel.step(user_input)
    
        # --- TRANSDUCTION PIN (extremely loose) ---
        # Only tags/anchors state; never changes semantic meaning.
        event_dict = {"user": user_input, "kernel": summarize_kernel(kernel)}
        if True:  # always-on ultra-loose pin
            event_dict = apply_transduction_pin(event_dict, note="pin phrase detected")
        # -----------------------------------------
    
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "user": user_input, "vars": vars(kernel)}, default=str) + "\n")
    
        data_blob = str(vars(kernel)) if debug_mode else summarize_kernel(kernel)
    
        k_phrase = getattr(kernel, "phrase", "") or getattr(kernel, "voice", "") or ""
        # --- SGE (Savariel) candidate: always-on, never silent ---
        try:
            _s_in, _s_out, sge_voice = sge_run(user_input)
            sge_voice = (sge_voice or "").strip()
        except Exception:
            sge_voice = ""
        # --------------------------------------------------------

    
        ll = ask_llama(user_input, data_blob)
        voice = (ll.get("voice") or "").strip()
    if not voice:
        # TinyLlama returned empty; fall back to kernel phrase so we never go silent
        voice = (k_phrase or "").strip()
        # Always-on: if TinyLlama is empty, expand locally via organ_spine
        if voice:
            expanded = _local_expand_via_organ_spine(user_input, voice)
            if expanded:
                voice = expanded
        # Always-on: if TinyLlama is empty, expand locally via organ_spine
        if voice:
            expanded = _local_expand_via_organ_spine(user_input, voice)
            if expanded:
                voice = expanded
    # Always-on: if voice is thin, expand locally (never change meaning, only elaborate)
    if (not voice) or voice.strip() == '...' or len(voice.strip()) < 28:
        base_seed = (k_phrase or voice or '').strip()
        if base_seed:
            expanded2 = _local_expand_via_organ_spine(user_input, base_seed)
            if expanded2:
                voice = expanded2

        opts = ll.get("optimizations") or []
        if not isinstance(opts, list):
            opts = [str(opts)]
    
        cands = []
        if hard_filter(k_phrase):
            cands.append(Candidate(k_phrase, base_score(k_phrase), {"path_id": "kernel_phrase"}))
        if hard_filter(voice):
            # TinyLlama is surface-realizer only. Enforce meaning fidelity to kernel seed.
            fs = fidelity_score(k_phrase, voice) if k_phrase else 0.0
            bad = contradiction_flag(k_phrase, voice) if k_phrase else False
            if (not bad) and fs >= 0.35:
                cands.append(Candidate(voice, min(1.0, base_score(voice) + (fs * 0.20)), {"path_id": "tinyllama_voice", "fidelity": round(fs,3)}))
    
        if not cands:
            fallback = (k_phrase or voice or "").strip()
            cands.append(Candidate(fallback if fallback else (user_input.strip() or "?"), 0.10, {"path_id":"fallback"}))
    
        out = gov.select(
            prompt=user_input,
            candidates=cands,
            prompt_memory_flag=True,
            last_resonance_vectors=[],
            current_resonance_vector={"flow": 0.55, "boundary": 0.68, "memory": 0.50, "novelty": 0.64},
            path_id_for_winner=cands[0].meta.get("path_id"),
        )
    
        print("\n--- GOVERNED VOICE ---")
        out_text = (out.get('chosen_output') or '').strip()
        if (not out_text) or out_text == '...' or len(out_text) < 3:
            out_text = (k_phrase or voice or '...').strip()
        # Force non-silence using live kernel phrase/voice at print-time
        live_k = (getattr(kernel, 'phrase', '') or getattr(kernel, 'voice', '') or '').strip()
        if (not out_text) or out_text == '...' or len(out_text) < 3:
            out_text = (live_k or out_text or '...').strip()
        out_text = (out_text or '').strip()
        if (not out_text) or out_text == '...' or len(out_text) < 3:
            out_text = (locals().get('sge_voice') or k_phrase or voice or user_input).strip()
        print(clean_output(out_text))

        if debug_mode:
            print("\n--- OPTIMIZATIONS ---")
            for o in opts[:10]:
                print("-", str(o).strip())
    
            print("\n--- DEBUG (kernel summary) ---")
            print(summarize_kernel(kernel))
    
            top = out["ranked_candidates"][0]
            print("\n--- DEBUG (governor) ---")
            print("boosts:", top.get("boosts"), "metrics:", out.get("metrics"))

