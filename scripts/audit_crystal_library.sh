#!/usr/bin/env bash
set -u

OUT="reports/crystal_library_audit_$(date +%Y%m%d_%H%M%S).txt"

{
  echo "=== CRYSTAL LIBRARY AUDIT ==="
  date
  echo

  echo "=== candidate files ==="
  find . -type f \( \
    -name "crystal_library.py" -o \
    -name "*crystallibrary*.py" -o \
    -name "liquid_crystal_core.py" -o \
    -name "*crystal*.json" \
  \) | sort

  echo
  echo "=== kernel/crystal_library.py exists? ==="
  ls -lah kernel/crystal_library.py 2>/dev/null || true

  echo
  echo "=== first 240 lines: kernel/crystal_library.py ==="
  sed -n '1,240p' kernel/crystal_library.py 2>/dev/null || true

  echo
  echo "=== function/class map via AST, no import execution ==="
  python - <<'PY'
import ast
from pathlib import Path

for path in [
    Path("kernel/crystal_library.py"),
    Path("runtime/crystal_library.py"),
    Path("symbolic_engine/crystal_library.py"),
    Path("kernel/liquid_crystal_core.py"),
]:
    if not path.exists():
        continue

    print(f"\n--- {path} ---")
    src = path.read_text(encoding="utf-8", errors="ignore")
    tree = ast.parse(src)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            print(f"{type(node).__name__}: {node.name} @ line {node.lineno}")

    print("imports:")
    for node in tree.body:
        if isinstance(node, ast.Import):
            print(" ", ", ".join(a.name for a in node.names))
        elif isinstance(node, ast.ImportFrom):
            print(" ", f"from {node.module} import", ", ".join(a.name for a in node.names))
PY

  echo
  echo "=== crystal terms ==="
  grep -RInE "anchor|sigil|glyph|family|role|transformative|diagnostic|pattern|resonance|definition|meaning|weight|crystal" \
    kernel/crystal_library.py kernel/liquid_crystal_core.py runtime/crystal_* symbolic_engine/*crystal* 2>/dev/null | head -n 220

  echo
  echo "=== import side-effect danger scan ==="
  grep -RInE "print\\(|open\\(|write_text|jsonl|STATE_FILE|evolve|mutat|accelerat|heartbeat|generation|while True|time.sleep|subprocess|os.system" \
    kernel/crystal_library.py kernel/liquid_crystal_core.py runtime/crystal_* symbolic_engine/*crystal* 2>/dev/null | head -n 220

  echo
  echo "=== py_compile only ==="
  python -m py_compile kernel/crystal_library.py 2>&1 || true
  [ -f kernel/liquid_crystal_core.py ] && python -m py_compile kernel/liquid_crystal_core.py 2>&1 || true

  echo
  echo "=== done ==="
} | tee "$OUT"

echo
echo "saved: $OUT"
