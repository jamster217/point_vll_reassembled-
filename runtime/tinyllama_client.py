import os
import requests

OLLAMA_URL = os.environ.get("LEVEON_OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
LLAMACPP_URL = os.environ.get("LEVEON_LLAMACPP_URL", "http://127.0.0.1:8080/completion")
TINYLLAMA_MODEL = os.environ.get("LEVEON_TINYLLAMA_MODEL", "tinyllama")

class TinyLlamaClient:
    def generate(self, prompt: str) -> str:
        out = self._try_ollama(prompt)
        if out:
            return out
        out = self._try_llamacpp(prompt)
        if out:
            return out
        return ""

    def creative_prompt(self, prompt: str) -> str:
        return (
            "Generate exploratory symbolic variations for a structured response system.\n"
            "Do not finalize the answer.\n"
            "Do not explain yourself.\n"
            "Return compressed variations, alternate framings, and symbolic possibilities.\n\n"
            f"INPUT:\n{prompt}\n"
        )

    def _try_ollama(self, prompt: str) -> str:
        try:
            r = requests.post(
                OLLAMA_URL,
                json={"model": TINYLLAMA_MODEL, "prompt": prompt, "stream": False},
                timeout=45
            )
            if r.status_code == 200:
                return r.json().get("response", "") or ""
        except Exception:
            pass
        return ""

    def _try_llamacpp(self, prompt: str) -> str:
        try:
            r = requests.post(
                LLAMACPP_URL,
                json={"prompt": prompt, "n_predict": 160},
                timeout=45
            )
            if r.status_code == 200:
                data = r.json()
                return data.get("content") or data.get("text") or ""
        except Exception:
            pass
        return ""

