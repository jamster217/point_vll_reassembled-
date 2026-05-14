#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/point_vll_reassembled" || exit 1

python -m py_compile runtime/phase3s_lineage_door_anchor.py runtime/unified_spine.py || exit 1
python runtime/phase3s_lineage_door_anchor.py | tee reports/phase3s/lineage_door_anchor_run.txt
