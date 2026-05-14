from __future__ import annotations

import logging
import os
import sqlite3
import string
from collections import Counter, deque
from importlib import import_module
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np


LOGGER = logging.getLogger(__name__)
DB_PATH = Path(os.getenv("LEVEON_CACHE", str(Path.home() / ".leveon" / "knowledge.db")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def tokenize(text: str) -> List[str]:
    trans = str.maketrans("", "", string.punctuation)
    return text.lower().translate(trans).split()


def ngrams(tokens: Sequence[str], n: int = 3) -> List[Tuple[str, ...]]:
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def random_embedding(dim: int = 64, seed: int | None = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(0, 1, dim)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


class KnowledgeGraph:
    def __init__(self, db_path: Path = DB_PATH, dim: int = 64):
        self.dim = dim
        self.conn = sqlite3.connect(db_path)
        self._prepare()

    def _prepare(self):
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phrase TEXT UNIQUE,
                embedding BLOB
            );
            """
        )
        self.conn.commit()

    def upsert(self, phrase: str, emb: np.ndarray):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO concepts (phrase, embedding)
            VALUES (?, ?)
            ON CONFLICT(phrase) DO UPDATE SET embedding=excluded.embedding
            """,
            (phrase, emb.astype(np.float64).tobytes()),
        )
        self.conn.commit()

    def query(self, emb: np.ndarray, top_k: int = 5) -> List[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT phrase, embedding FROM concepts")
        scored: List[Tuple[float, str]] = []

        for phrase, blob in cur.fetchall():
            vec = np.frombuffer(blob, dtype=np.float64)
            if len(vec) != len(emb):
                continue
            scored.append((cosine(emb, vec), phrase))

        scored.sort(reverse=True)
        return [p for _, p in scored[:top_k]]


class SelfLearningCore:
    DIM = 64

    def __init__(self, kg: KnowledgeGraph | None = None):
        self.kg = kg or KnowledgeGraph(dim=self.DIM)
        self.recent_phrases: deque[str] = deque(maxlen=256)

        try:
            from runtime.still_turn_scheduler import register_still_turn_callback
            register_still_turn_callback(self.compact_and_distill)
        except ModuleNotFoundError:
            LOGGER.debug("StillTurnScheduler missing; distill will run only manual")

    def observe(self, shape_vec: Dict[str, float], english_out: str):
        vec = np.array(
            [
                shape_vec.get("flow", 0.0),
                shape_vec.get("boundary", 0.0),
                shape_vec.get("memory", 0.0),
                shape_vec.get("novelty", 0.0),
            ],
            dtype=np.float64,
        )

        rng_seed = hash(english_out) & 0xFFFF
        emb = np.concatenate([vec, random_embedding(self.DIM - len(vec), seed=rng_seed)])

        tokens = tokenize(english_out)
        grams = Counter(ngrams(tokens, 3))

        for gram, _ in grams.most_common(5):
            phrase = " ".join(gram)
            if phrase not in self.recent_phrases:
                self.kg.upsert(phrase, emb)
                self.recent_phrases.append(phrase)

    def enrich(self, shape_vec: Dict[str, float]) -> List[str]:
        vec = np.array(
            [
                shape_vec.get("flow", 0.0),
                shape_vec.get("boundary", 0.0),
                shape_vec.get("memory", 0.0),
                shape_vec.get("novelty", 0.0),
            ],
            dtype=np.float64,
        )
        emb = np.concatenate([vec, np.zeros(self.DIM - len(vec), dtype=np.float64)])
        return self.kg.query(emb, top_k=5)

    def compact_and_distill(self):
        cur = self.kg.conn.cursor()
        cur.execute("SELECT phrase FROM concepts ORDER BY id DESC LIMIT 100")
        phrases = [p for (p,) in cur.fetchall()]
        distilled = [p.capitalize() + "." for p in phrases]
        LOGGER.info("Distilled %d concepts for articulation cache", len(distilled))

    @classmethod
    def patch_kernel(cls):
        organ_spine = import_module("runtime.organ_spine")
        original = organ_spine._run_spine
        slc = cls()

        def _patched_run_spine(*args, **kwargs):
            shape_vec = kwargs.get("shape_vec") or {}
            result = original(*args, **kwargs)

            if isinstance(result, str):
                english_out = result
            elif isinstance(result, dict):
                english_out = str(result.get("text", ""))
            else:
                english_out = str(result)

            slc.observe(shape_vec, english_out)
            organ_spine._slc_enrich = slc.enrich(shape_vec)
            return result

        organ_spine._run_spine = _patched_run_spine
        LOGGER.info("SelfLearningCore patched into runtime.organ_spine._run_spine")
        return slc

