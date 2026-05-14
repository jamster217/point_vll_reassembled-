#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/point_vll_reassembled" || exit 1

grep -R "temporal_flashback_larynx\|SavarielMouth\|temporal_mirror" \
  assets/memory memory var/memory logs/symbolic_bridge 2>/dev/null | tail -50
