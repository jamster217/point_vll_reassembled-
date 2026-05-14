#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/point_vll_reassembled" || exit 1
python runtime/flashback_shape_reasoner.py "$@"
