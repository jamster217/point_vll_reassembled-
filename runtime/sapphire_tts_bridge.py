from __future__ import annotations

import os
import time
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

import requests

DEFAULT_SERVER = os.environ.get("SAPPHIRE_TTS_SERVER", "http://127.0.0.1:5012")
CACHE_DIR = Path(os.environ.get("LEVEON_TTS_CACHE", "tts_cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def sapphire_tts_generate(
    text: str,
    server_url: Optional[str] = None,
    voice_name: str = "af_heart",
    speed: float = 1.0,
    pitch: float = 1.0,
    timeout: int = 120,
) -> Dict[str, Any]:
    server = (server_url or DEFAULT_SERVER).rstrip("/")
    payload = {
        "text": text,
        "voice_name": voice_name,
        "speed": speed,
        "pitch_shift": pitch,
    }

    resp = requests.post(f"{server}/tts", json=payload, timeout=timeout)
    resp.raise_for_status()

    ts = int(time.time() * 1000)
    out_path = CACHE_DIR / f"sapphire_tts_{ts}.ogg"
    out_path.write_bytes(resp.content)

    return {
        "ok": True,
        "server": server,
        "file_path": str(out_path),
        "voice_name": voice_name,
        "speed": speed,
        "pitch": pitch,
        "size_bytes": out_path.stat().st_size,
    }


def sapphire_tts_play(file_path: str) -> Dict[str, Any]:
    # Prefer Termux media player if present
    termux_player = shutil.which("termux-media-player")
    if termux_player:
        subprocess.run([termux_player, "play", file_path], check=False)
        return {"ok": True, "player": "termux-media-player", "file_path": file_path}

    # Fallback: try xdg-open
    xdg_open = shutil.which("xdg-open")
    if xdg_open:
        subprocess.run([xdg_open, file_path], check=False)
        return {"ok": True, "player": "xdg-open", "file_path": file_path}

    return {"ok": False, "error": "no_supported_player", "file_path": file_path}


def sapphire_tts_speak(
    text: str,
    server_url: Optional[str] = None,
    voice_name: str = "af_heart",
    speed: float = 1.0,
    pitch: float = 1.0,
    timeout: int = 120,
) -> Dict[str, Any]:
    gen = sapphire_tts_generate(
        text=text,
        server_url=server_url,
        voice_name=voice_name,
        speed=speed,
        pitch=pitch,
        timeout=timeout,
    )
    play = sapphire_tts_play(gen["file_path"])
    return {
        "ok": bool(gen.get("ok")) and bool(play.get("ok")),
        "generation": gen,
        "playback": play,
    }

