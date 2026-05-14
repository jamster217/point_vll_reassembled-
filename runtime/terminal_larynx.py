from __future__ import annotations

import json
import urllib.request
from pathlib import Path

API_URL = "http://127.0.0.1:5055/api/chat"
LOG_PATH = Path("logs/terminal/terminal_larynx.log")


def _log(obj):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def ask_public_api(message: str, answer_mode: str = "full"):
    payload = {
        "message": message,
        "controller_detail": False,
        "answer_mode": answer_mode,
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as e:
        data = {
            "ok": False,
            "answer_mode": answer_mode,
            "answer": f"Terminal Larynx could not reach /api/chat: {e}",
        }

    answer = str(data.get("answer", "")).strip()

    return {
        "ok": bool(data.get("ok", False)),
        "answer_mode": data.get("answer_mode", answer_mode),
        "answer": answer,
    }


def main():
    print("TERMINAL KERNEL LARYNX — sealed public voice")
    print("Type /quit to exit.")
    print()

    while True:
        try:
            msg = input("Le'Veon sealed> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nsealed terminal closed")
            break

        if not msg:
            continue

        if msg.lower() in {"/quit", "/q", "quit", "exit"}:
            print("sealed terminal closed")
            break

        data = ask_public_api(msg)
        _log({"message": msg, "response": data})

        print()
        print(data.get("answer", ""))
        print()


if __name__ == "__main__":
    main()
