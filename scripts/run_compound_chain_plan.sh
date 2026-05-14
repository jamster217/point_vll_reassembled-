#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/point_vll_reassembled" || exit 1
python runtime/compound_chain_planner.py
bash scripts/run_active_build.sh
bash scripts/run_reinforcement_decay.sh
