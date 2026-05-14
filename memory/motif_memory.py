from __future__ import annotations
from collections import Counter
from typing import Dict, List, Tuple
import re

_WORD_RE = re.compile(r"[A-Za-z']+")

class MotifMemory:
    def __init__(self) -> None:
        self.tokens: Counter[str] = Counter()
        self.bigrams: Counter[Tuple[str, str]] = Counter()

    def _tokenize(self, text: str) -> List[str]:
        return [t.lower() for t in _WORD_RE.findall(text or "")]

    def observe(self, text: str) -> None:
        toks = self._tokenize(text)
        if not toks:
            return
        self.tokens.update(toks)
        self.bigrams.update(zip(toks, toks[1:]))

    def decay(self, factor: float = 0.995) -> None:
        if factor <= 0 or factor >= 1:
            return
        for k in list(self.tokens):
            self.tokens[k] *= factor
            if self.tokens[k] < 0.5:
                del self.tokens[k]
        for k in list(self.bigrams):
            self.bigrams[k] *= factor
            if self.bigrams[k] < 0.5:
                del self.bigrams[k]

    def top_tokens(self, n: int = 10) -> List[str]:
        return [w for w, _ in self.tokens.most_common(n)]

    def top_bigrams(self, n: int = 10) -> List[str]:
        return [" ".join(bg) for bg, _ in self.bigrams.most_common(n)]

    def bias_score(self, token: str) -> float:
        total = float(sum(self.tokens.values()) or 1.0)
        return float(self.tokens[token.lower()]) / total

    def snapshot(self) -> Dict[str, object]:
        return {
            "top_tokens": self.top_tokens(10),
            "top_bigrams": self.top_bigrams(10),
            "token_total": int(sum(self.tokens.values())),
            "bigram_total": int(sum(self.bigrams.values())),
        }

