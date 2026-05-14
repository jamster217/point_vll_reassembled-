import os
import requests

API_BASE = os.environ.get("LEVEON_API_BASE", "").rstrip("/")
API_KEY = os.environ.get("LEVEON_API_KEY", "")
API_MODEL = os.environ.get("LEVEON_API_MODEL", "")

class APIKeyClient:
    def generate(self, prompt: str) -> str:
        if not API_BASE or not API_KEY or not API_MODEL:
            return ""

        url = f"{API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": API_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Produce exploratory intermediate material for a symbolic pipeline. "
                        "Do not finalize. Do not roleplay. Return strong candidate text only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.8,
        }

        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                data = r.json()
                return data["choices"][0]["message"]["content"]
        except Exception:
            pass
        return ""

