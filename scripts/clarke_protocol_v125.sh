#!/usr/bin/env bash
set -u

ROOT="${ROOT:-$HOME/point_vll_reassembled}"
cd "$ROOT" || exit 1

python runtime/clarke_paranormal_protocol_v125.py "$@"
