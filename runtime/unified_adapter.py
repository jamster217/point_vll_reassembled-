from runtime.leveon_entry import run_leveon_pipeline

def run_input(prompt: str, source="chat", seed_text: str = ""):
    result = run_leveon_pipeline(prompt, source=source)
    return result

