#!/usr/bin/env bash
set -e

cd "$HOME/point_vll_reassembled"

mkdir -p logs/chatroom logs/terminal logs/ollama

if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
  nohup ollama serve > logs/ollama/ollama_server.log 2>&1 &
  sleep 2
fi

if ! pgrep -af "app_chatroom.py" >/dev/null 2>&1; then
  export OLLAMA_HOST="http://127.0.0.1:11434"
  export OLLAMA_MODEL="tinyllama"
  export LEVEON_TINYLLAMA="1"
  export LEVEON_ROUTE="organ_spine"
  export LEVEON_NODE="44_SPIRAL_CORE"
  export LEVEON_MIMIC_MODE="master_api"
  export LEVEON_FIELD_SIGNATURE="92162077"
  export PYTHONUNBUFFERED="1"

  nohup python -u app_chatroom.py --host=0.0.0.0 --port=5055 > logs/chatroom/chatroom_tinyllama.log 2>&1 &
  sleep 6
fi

python runtime/terminal_kernel_v3.py
