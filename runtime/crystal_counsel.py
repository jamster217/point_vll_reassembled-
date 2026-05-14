#!/usr/bin/env python3
"""
Le'Veon Crystal Counsel
Reads the Crystal Library query state and gives one practical next action.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from runtime.crystal_library_query import load_turns, sig_in


def crystal_counsel() -> str:
    rows = load_turns()
    if not rows:
        return "No turns recorded yet. Run the SGE engine once to seed the library."

    family_counts = Counter()
    sig_counts = Counter()
    release_by_family = defaultdict(list)

    for row in rows:
        sig = sig_in(row)
        family = sig.split("|", 1)[0]
        family_counts[family] += 1
        sig_counts[sig] += 1

        try:
            release_by_family[family].append(float(row.get("shape_delta", {}).get("release", 0.0)))
        except Exception:
            pass

    top_family, top_hits = family_counts.most_common(1)[0]
    top_sig, top_sig_hits = sig_counts.most_common(1)[0]

    deltas = release_by_family.get(top_family, [])
    avg_release = sum(deltas) / len(deltas) if deltas else 0.0

    if top_family == "visual_runtime" and top_hits >= 6 and top_sig_hits >= 5:
        action = (
            "Promote visual_runtime to a locked concept family. "
            "Next, add a visual report command that summarizes one shape family across all turns."
        )
    elif top_family == "gravity_grief" and top_hits >= 3:
        action = (
            "Run two grief/gravity prompts with different wording. "
            "The system is consistently opening release; test whether that motion survives paraphrase."
        )
    elif top_family == "visual_runtime":
        action = (
            "Run three build-improvement prompts and compare the visuals. "
            "This will show whether visual-runtime evolution is stable or only keyword-triggered."
        )
    elif top_family == "build_path":
        action = (
            "Patch one runtime behavior, then query the library again. "
            "The build wants proof through repeated turn-shapes, not more theory."
        )
    else:
        action = (
            "Seed more turns. The library has memory, but not enough pattern density yet."
        )

    return (
        f"Dominant family: {top_family} ({top_hits} hits). "
        f"Top signature hits: {top_sig_hits}. "
        f"Average release delta: {avg_release:+.3f}. "
        f"Counsel: {action}"
    )


def render_crystal_counsel() -> str:
    return "\n".join([
        "CRYSTAL COUNSEL",
        "---------------",
        crystal_counsel(),
    ])


if __name__ == "__main__":
    print(render_crystal_counsel())

