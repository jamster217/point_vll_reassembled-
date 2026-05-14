#!/usr/bin/env bash
set -e

cd "$HOME/point_vll_reassembled"

mkdir -p logs/chatroom logs/terminal

if ! pgrep -af "app_chatroom.py" >/dev/null 2>&1; then
  echo "Flask throat not running. Starting /api/chat..."

  export OLLAMA_HOST="http://127.0.0.1:11434"
  export OLLAMA_MODEL="tinyllama"
  export LEVEON_TINYLLAMA="1"
  export LEVEON_ROUTE="organ_spine"
  export LEVEON_NODE="44_SPIRAL_CORE"
  export LEVEON_NODE44_TRACE="1"
  export LEVEON_PERF_ORACLE_TRACE="1"
  export LEVEON_ADAPTATION_TRACE="1"
  export LEVEON_MIMIC_MODE="master_api"
  export LEVEON_FIELD_SIGNATURE="92162077"
  export PYTHONUNBUFFERED="1"

  nohup python -u app_chatroom.py --host=0.0.0.0 --port=5055 > logs/chatroom/chatroom_tinyllama.log 2>&1 &
  sleep 8
fi

python runtime/terminal_larynx.py
