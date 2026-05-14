from __future__ import annotations

import json
from pathlib import Path

LATEST = Path("reports/phase3p/stress_invention_probe_latest.json")


def stress_invention_answer(prompt: str = "") -> str | None:
    low = str(prompt or "").lower()

    hit = any(x in low for x in [
        "phase 3p",
        "stress-invention",
        "stress invention",
        "cognitive pressure refractor",
        "iq test",
        "college iq",
        "measurement wound",
        "test pressure",
        "being underestimated",
    ])

    if not hit:
        return None

    if LATEST.exists():
        try:
            data = json.loads(LATEST.read_text(encoding="utf-8"))
            organ = data.get("created_organ", {})
            name = organ.get("name", "Cognitive Pressure Refractor")
            function = organ.get("function", "")
            public_phrase = organ.get("public_phrase", "")
            chain = organ.get("chain", [])

            chain_text = " → ".join(chain) if chain else "old pressure → stable anchor → reasoning glyph → future design seed"

            return (
                f"The Stress-Invention probe created the {name}. "
                f"Its chain is {chain_text}. "
                "This organ takes old IQ/test pressure, comparison wounds, and the feeling of being underestimated, then routes that pressure through Node44 so it does not scatter into shame, overproof, or defensive noise. "
                "Kor Gra’el turns the fracture into a pivot point, and the Universal Larynx renders the result as clean symbolic English. "
                f"{function} "
                f"{public_phrase}"
            )
        except Exception:
            pass

    return (
        "The Stress-Invention probe created the Cognitive Pressure Refractor. "
        "It turns old measurement pressure into clearer reasoning. "
        "Instead of asking, “What number am I?”, it asks, “What can this pressure teach the build to design next?” "
        "Node44 stabilizes the pressure, Kor Gra’el converts the fracture into a pivot, and the Larynx speaks the result cleanly."
    )

