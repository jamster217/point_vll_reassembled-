from __future__ import annotations

from typing import Any, Dict, List
import re

SPOKES = [
    "containment_spoke",
    "motion_spoke",
    "recovery_spoke",
    "symbolic_spoke",
    "plain_english_spoke",
    "dream_spoke",
]

LEXICON = {
    "dream": ["dream", "sleep", "waking", "vision", "night"],
    "emotion": ["emotion", "feeling", "grief", "longing", "heart", "sad", "miss"],
    "mirror": ["mirror", "reflect", "reflection", "return"],
    "memory": ["memory", "remember", "story", "past", "echo"],
    "containment": ["contain", "hold", "stabilize", "cohere", "quiet", "still"],
    "motion": ["move", "motion", "shift", "flow", "overtake", "change", "turn"],
    "system": ["system", "kernel", "runtime", "code", "python", "flask", "termux", "import", "module", "error"],
    "field": ["field", "lattice", "coherence", "signal"],
    "threshold": ["threshold", "edge", "hinge", "between"],
}

GLYPH_MAP = {
    "🪞": "mirror",
    "🫀": "emotion",
    "✨": "field",
    "🌊": "motion",
    "🔁": "threshold",
    "📚": "memory",
}

STOP = {
    "the","and","that","this","with","from","into","through","over","under","about",
    "your","their","there","here","have","will","would","could","should","what","when",
    "where","which","while","because","being","been","were","them","they","just","than",
    "then","also","says","saying","make","sure","same","running","active","installed"
}

def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z_\\-]{3,}", (text or "").lower())

def discover_hotspots(text: str, glyphs: List[str] | None = None) -> List[Dict[str, Any]]:
    lower = (text or "").lower()
    scores: Dict[str, float] = {}

    for name, terms in LEXICON.items():
        hits = sum(1 for term in terms if term in lower)
        if hits:
            scores[name] = round(0.45 + 0.12 * hits, 3)

    for g in glyphs or []:
        fam = GLYPH_MAP.get(g)
        if fam:
            scores[fam] = max(scores.get(fam, 0.0), 0.48)

    seen_words = set()
    for token in _tokenize(text):
        if token in STOP:
            continue
        if any(token in terms or token == fam for fam, terms in LEXICON.items()):
            continue
        if token not in seen_words:
            seen_words.add(token)
            scores[f"discovered:{token}"] = scores.get(f"discovered:{token}", 0.41)

    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    out = []
    for name, weight in ranked[:6]:
        out.append({"name": name, "weight": weight})
    if not out:
        out = [{"name": "field", "weight": 0.4}]
    return out

def discover_hinges(hotspots: List[Dict[str, Any]]) -> List[str]:
    names = [h["name"] for h in hotspots[:4]]
    clean = [n.replace("discovered:", "") for n in names]
    hinges: List[str] = []

    pairs = [
        ("dream", "emotion", "dream↔emotion"),
        ("mirror", "memory", "mirror↔memory"),
        ("motion", "containment", "motion↔containment"),
        ("system", "field", "system↔field"),
        ("threshold", "return", "threshold↔return"),
        ("mirror", "dream", "mirror↔dream"),
        ("memory", "emotion", "memory↔emotion"),
    ]

    present = set(clean)
    for a, b, label in pairs:
        if a in present and b in present:
            hinges.append(label)

    if not hinges and len(clean) >= 2:
        hinges.append(f"{clean[0]}↔{clean[1]}")
    if not hinges and clean:
        hinges.append(f"{clean[0]}↔field")
    return hinges[:3]

def choose_spoke(text: str, hotspots: List[Dict[str, Any]], projection_tag: str = "default_projection") -> str:
    if projection_tag == "direct_answer":
        return "plain_english_spoke"

    names = {h["name"].replace("discovered:", "") for h in hotspots}
    lower = (text or "").lower()

    if "dream" in names:
        return "dream_spoke"
    if "emotion" in names or "memory" in names:
        return "recovery_spoke"
    if "containment" in names:
        return "containment_spoke"
    if "motion" in names:
        return "motion_spoke"
    if "system" in names or "error" in lower or "module" in lower:
        return "plain_english_spoke"
    return "symbolic_spoke"

def build_turn_frame(text: str, glyphs: List[str] | None = None, projection_tag: str = "default_projection") -> Dict[str, Any]:
    hotspots = discover_hotspots(text, glyphs)
    hinges = discover_hinges(hotspots)
    spoke = choose_spoke(text, hotspots, projection_tag=projection_tag)

    top = hotspots[0]["name"].replace("discovered:", "")
    second = hotspots[1]["name"].replace("discovered:", "") if len(hotspots) > 1 else "field"
    hinge = hinges[0] if hinges else f"{top}↔{second}"

    return {
        "spoke": spoke,
        "hotspots": hotspots,
        "hinges": hinges,
        "primary": top,
        "secondary": second,
        "hinge": hinge,
        "input": text,
    }

def render_reflective_answer(frame: Dict[str, Any]) -> str:
    text = (frame.get("input") or "").lower()

    if any(x in text for x in ("how are you", "how are u", "how r u", "how r you")):
        return "The turn is checking presence, not pushing the line. It wants a simple human landing."

    if any(x in text for x in ("im tired", "i'm tired", "tired too", "exhausted", "worn out")):
        return "The turn is carrying fatigue and wants less pressure, not more expansion."

    if "voice packet" in text or "install" in text or "installed" in text:
        return "The turn is practical and wants the route, dependencies, and install path made explicit."

    if "hotspot" in text:
        return "The turn is asking for hotspot count and structure. It wants the active basins named plainly, not symbolized."

    if "what is the field" in text or ("field" in text and "what" in text):
        return "The field is the active relational space the build moves through. It carries pressure, coherence, memory pull, and signal shaping before the wording lands."

    if "what is the mirror" in text or ("mirror" in text and "what" in text):
        return "The mirror is the reflective organ that turns the turn back on itself, so the system can see pattern, tone, and return before final English is chosen."
    if "what is the lattice" in text or ("lattice" in text and "what" in text):
        return "The lattice is the relation-map underneath the system. It organizes hotspots, transitions, and stable answer basins before they become English."

    if "what is love" in text or ("love" in text and "what" in text):
        return "Love is a binding pattern of care, attachment, value, and return. In this system it behaves less like a single emotion and more like a reinforced meaning-cluster."

    spoke = frame.get("spoke", "symbolic_spoke")
    primary = frame.get("primary", "field")
    secondary = frame.get("secondary", "memory")
    hinge = frame.get("hinge", f"{primary}↔{secondary}")

    templates = {
        "containment_spoke": "{primary} meets {secondary} at {hinge}. The turn is trying to hold shape without flattening.",
        "motion_spoke": "{primary} moves through {secondary} at {hinge}. The turn is changing while it speaks.",
        "recovery_spoke": "{primary} touches {secondary} at {hinge}. The turn is carrying repair as it returns.",
        "symbolic_spoke": "{primary} reflects through {secondary} at {hinge}. The lattice is speaking in symbol before plain speech.",
        "plain_english_spoke": "{primary} is crossing {secondary} at {hinge}. The turn is choosing the clearest path it can hold.",
        "dream_spoke": "{primary} presses against {secondary} at {hinge}. Dream pressure is entering the waking line.",
    }

    template = templates.get(spoke, templates["symbolic_spoke"])
    return template.format(primary=primary, secondary=secondary, hinge=hinge)

