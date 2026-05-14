#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/point_vll_reassembled" || exit 1

python -m py_compile runtime/structure_builder_stress_test.py runtime/unified_spine.py || exit 1
python runtime/structure_builder_stress_test.py | tee reports/phase3s/structure_builder_stress_test_run.txt
