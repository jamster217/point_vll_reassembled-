#!/data/data/com.termux/files/usr/bin/bash
set -u

cd "$HOME/point_vll_reassembled" || exit 1
mkdir -p reports/screenshot_synthesis

echo "[1] Trace essence/mode collapse terms"
rg -n "optimize_answer|reflective/emotional hybrid|state.*explain.*widen|constraint|mode|essence|shape|valence|persistence|relation|clause_type" \
  core runtime english_layer spiral_language . 2>/dev/null \
  | tee reports/screenshot_synthesis/trace_essence_mode_terms.txt

echo "[2] Trace mouth/rendering route"
rg -n "layers_english_renderer|layer5_english_renderer|english_renderer|Layer5|FINAL_RENDERER|final_renderer|unified_voice|to_english|ordinary_mouth|clean_mouth|candidate_competition|glyph_surgery_filter" \
  app_chatroom.py core runtime spiral_language english_layer layers voice voices . 2>/dev/null \
  | tee reports/screenshot_synthesis/trace_mouth_route.txt

echo "[3] Trace clause/glyph/phenome route"
rg -n "glyph_trail|spiral_sentence|phenome|clause|TextMirror|text_mirror|Chronifier|chronifier|ApexMirror|apex_mirror|still_coherence|coherence" \
  core runtime spiral_language symbolic_engine kernel . 2>/dev/null \
  | tee reports/screenshot_synthesis/trace_clause_organs.txt

echo "[DONE] Trace files written under reports/screenshot_synthesis/"

