#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Dict, Any

LAW = "compress_truth_without_losing_signal"

def compress(text: str, max_sentences: int = 3) -> Dict[str, Any]:

    original = text.strip()

    # remove source clutter
    original = re.sub(r'Source:\s*https?://\S+', '', original)

    parts = re.split(r'(?<=[.!?])\s+', original)

    compact = " ".join(parts[:max_sentences]).strip()

    compact = re.sub(r'\s+', ' ', compact)

    return {
        "law": LAW,
        "original_length": len(text),
        "compressed_length": len(compact),
        "compressed": compact
    }

if __name__ == "__main__":
    demo = compress(
        "Leaves change color because chlorophyll breaks down in autumn. Trees recover nutrients before winter. Different pigments become visible."
    )
    print(demo["compressed"])

