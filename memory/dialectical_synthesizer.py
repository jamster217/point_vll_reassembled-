from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class DialecticalPacket:
    source_text: str
    thesis: str
    counterforce: str
    synthesis: str
    final_point: str
    logic_chain: List[str]


def synthesize_response(source_text: str, thesis: str, counterforce: str) -> Dict:
    thesis = (thesis or "").strip()
    counterforce = (counterforce or "").strip()

    if thesis and counterforce:
        synthesis = f"{thesis} | counter-balanced by | {counterforce}"
        final_point = thesis
    elif thesis:
        synthesis = thesis
        final_point = thesis
    else:
        synthesis = counterforce
        final_point = counterforce

    packet = DialecticalPacket(
        source_text=source_text,
        thesis=thesis,
        counterforce=counterforce,
        synthesis=synthesis,
        final_point=final_point,
        logic_chain=[
            f"source:{source_text}",
            f"thesis:{thesis}",
            f"counterforce:{counterforce}",
            f"synthesis:{synthesis}",
            f"final_point:{final_point}",
        ],
    )
    return asdict(packet)

