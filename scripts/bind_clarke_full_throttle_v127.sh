#!/usr/bin/env bash
set -u

ROOT="${ROOT:-$HOME/point_vll_reassembled}"
cd "$ROOT" || exit 1

python runtime/clarke_wind_tunnel_full_throttle_v127.py "$@"
