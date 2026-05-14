#!/usr/bin/env bash
set -u

ROOT="${ROOT:-$HOME/point_vll_reassembled}"
cd "$ROOT" || exit 1

target="${1:-}"
ts="$(date +%Y%m%d_%H%M%S_%N)"
slug="$(printf "%s" "$target" | tr "/ " "__" | tr -cd "[:alnum:]_.-")"
out="reports/v12_7/evidence/ghost_log_evidence_packet_${ts}_${slug}.txt"

if [ -z "$target" ]; then
  echo "Usage: scripts/ghost_log_evidence_packet_v127.sh <path-to-suspected-log>"
  exit 2
fi

{
  echo "=== V12.7 GHOST LOG EVIDENCE PACKET ==="
  echo "created_at_local: $(date)"
  echo "created_at_utc: $(date -u)"
  echo "timezone: ${TZ:-unset}"
  echo
  echo "=== DEVICE TIME ==="
  date
  date -u
  uptime 2>/dev/null || true
  echo
  echo "=== TARGET ==="
  echo "$target"
  echo
  echo "=== STAT ==="
  stat "$target" 2>&1 || true
  echo
  echo "=== HASH ==="
  sha256sum "$target" 2>&1 || true
  echo
  echo "=== FIRST 40 LINES ==="
  sed -n '1,40p' "$target" 2>&1 || true
  echo
  echo "=== LAST 80 LINES ==="
  tail -n 80 "$target" 2>&1 || true
} > "$out"

ln -sf "$(basename "$out")" reports/v12_7/evidence/latest_ghost_log_packet.txt

echo "WROTE: $out"
cat "$out"
