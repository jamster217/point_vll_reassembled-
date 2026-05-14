from pathlib import Path

LATTICE_DIR = Path(__file__).resolve().parent

LATTICE_SLOTS_NDJSON = LATTICE_DIR / "lattice_slots.ndjson"
LATTICE_INDEX_SQLITE = LATTICE_DIR / "lattice_index.sqlite3"

LEGACY_LATTICE_SLOTS = LATTICE_DIR / "lattice_slots.md"
LEGACY_LATTICE_INDEX = LATTICE_DIR / "lattice_index.py"

def get_lattice_slots_path() -> Path:
    if LATTICE_SLOTS_NDJSON.exists():
        return LATTICE_SLOTS_NDJSON
    return LEGACY_LATTICE_SLOTS

def get_lattice_index_path() -> Path:
    if LATTICE_INDEX_SQLITE.exists():
        return LATTICE_INDEX_SQLITE
    return LEGACY_LATTICE_INDEX

