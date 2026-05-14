#!/usr/bin/env bash
set -e

cd "$HOME/point_vll_reassembled"

python - <<'PY'
try:
    import pygame
    print("pygame: available")
except Exception as e:
    raise SystemExit(f"pygame missing or unavailable: {e}")
PY

python interface/invention/invention_node_engine.py
