import os, json, urllib.request
from pathlib import Path

def load_strategy_echo_config():
    path = Path("LIVE_CORE/brain/strategy_echo_config.json")
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}

def post_filter_guardrail(text):
    text = (text or "").strip()

    bad_bits = [
        "This means that",
        "ASSISTANT cannot",
        "as ONE short",
        "our AI assistant",
        "SHAPE_PACKET",
        "JSON",
        "markdown",
        "bold",
        "italics",
    ]

    for bit in bad_bits:
        if bit in text:
            text = text.split(bit)[0].strip()

    for sep in [". ", "! ", "? "]:
        if sep in text:
            text = text.split(sep)[0].strip() + sep.strip()
            break

    return text.strip()

def build_renderer_prompt(shape_packet, context=None):
    strategy = load_strategy_echo_config()
    if strategy:
        shape_packet = dict(shape_packet)
        shape_packet["strategy_echo_config"] = strategy

    core = shape_packet.get("core_answer", "")
    must = " ".join(shape_packet.get("must_say", []))
    if strategy:
        must = (must + " Strategy state: " + strategy.get("state", "") + ". Seal: " + strategy.get("seal", "")).strip()
    return (
        "Write one plain sentence. No labels. No explanation. No preface.\n"
        "Meaning: " + core + " " + must + "\n"
        "Answer: "
    )

def tinyllama_generate(prompt):
    try:
        from runtime.tinyllama_client import TinyLlamaClient
        client = TinyLlamaClient()
        return (client.generate(prompt) or "").strip()
    except Exception as e:
        return f"TinyLlama path failed: {type(e).__name__}: {e}"

def call_openrouter(prompt, model=None):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "OpenRouter path selected, but OPENROUTER_API_KEY is not set."

    model = model or os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    data = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "You render structured packets into clear, warm, direct English."},
            {"role": "user", "content": prompt}
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.loads(r.read().decode("utf-8"))
    return out["choices"][0]["message"]["content"]

def render_english(shape_packet, context=None, backend="tinyllama"):
    prompt = build_renderer_prompt(shape_packet, context)

    if backend == "local_direct":
        return shape_packet.get("final_text") or shape_packet.get("core_answer") or ""
    elif backend == "tinyllama":
        raw = tinyllama_generate(prompt)
    elif backend == "openrouter":
        raw = call_openrouter(prompt)
    else:
        raise ValueError(f"Unknown backend: {backend}")

    return post_filter_guardrail(raw)

