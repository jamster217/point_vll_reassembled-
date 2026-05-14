#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/point_vll_reassembled" || exit 1

python -m py_compile runtime/phase3s_lineage_thread_probe.py runtime/unified_spine.py || exit 1
python runtime/phase3s_lineage_thread_probe.py | tee reports/phase3s/lineage_thread_probe_run.txt
