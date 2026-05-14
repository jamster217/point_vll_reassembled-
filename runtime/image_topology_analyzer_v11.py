from pathlib import Path
import json, time, hashlib, re, html, math
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[1]

IMAGE_MEMORY_DIR = ROOT / "var" / "image_memory"
IMAGE_SHAPES_LOG = IMAGE_MEMORY_DIR / "image_shapes_v11.jsonl"
TAG_INDEX_PATH = IMAGE_MEMORY_DIR / "tag_index_v11.json"
SYMBOLIC_MEMORY_PATH = ROOT / "logs" / "symbolic_bridge" / "spiral_memory_nonlinear.jsonl"
GENERATED_DIR = ROOT / "static" / "generated"
LATTICE_DIR = ROOT / "var" / "lattice"
LATTICE_LOG = LATTICE_DIR / "image_topology_v11.jsonl"

def _tokens(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9_'-]+", str(text).lower())

def _canonical_tag(tag: str) -> str:
    tag = str(tag).strip().lower()
    tag = re.sub(r"[^a-z0-9]+", "_", tag)
    return tag.strip("_")

def _extract_user_tags(prompt: str) -> List[str]:
    prompt = str(prompt or "")
    found = []

    # Handles: with tags 'Happy, Woman, Tree, Autumn, Meadow'
    m = re.search(r"tags?\s*[=:]?\s*['\"]([^'\"]+)['\"]", prompt, re.I)
    if m:
        found.extend([x.strip() for x in m.group(1).split(",")])

    # Also handles bare: tags Happy, Woman, Tree
    m2 = re.search(r"tags?\s*[=:]?\s*([A-Za-z0-9_,\s-]{5,120})", prompt, re.I)
    if m2 and not found:
        chunk = m2.group(1)
        chunk = chunk.split(".")[0]
        found.extend([x.strip() for x in chunk.split(",")])

    clean = []
    for t in found:
        c = _canonical_tag(t)
        if c and c not in clean:
            clean.append(c)
    return clean

def _auto_tags(prompt: str) -> List[str]:
    p = str(prompt or "").lower()
    tags = []

    rules = [
        ("woman", "woman"),
        ("girl", "woman"),
        ("person", "human_figure"),
        ("figure", "human_figure"),
        ("human", "human_figure"),
        ("tree", "tree"),
        ("forest", "forest"),
        ("meadow", "meadow"),
        ("field", "meadow"),
        ("autumn", "autumn"),
        ("fall", "autumn"),
        ("golden", "golden_light"),
        ("light", "light"),
        ("happy", "happy"),
        ("joy", "happy"),
        ("smile", "happy"),
        ("calm", "calm"),
        ("sky", "sky"),
        ("dark", "dark_sky"),
        ("spiral", "spiral"),
        ("white-ash", "white_ash"),
        ("white ash", "white_ash"),
        ("echoforge", "echoforge"),
        ("thalveil", "thalveil"),
        ("virellion", "virellion"),
    ]

    for needle, tag in rules:
        if needle in p and tag not in tags:
            tags.append(tag)

    semantic = []
    if any(x in tags for x in ["tree", "forest", "meadow", "autumn"]):
        semantic.append("natural_landscape")
    if any(x in tags for x in ["woman", "human_figure"]):
        semantic.append("subject_centered")
    if any(x in tags for x in ["happy", "golden_light", "calm"]):
        semantic.append("positive_emotional_tone")

    for tag in semantic:
        if tag not in tags:
            tags.append(tag)

    return tags

def _open_vocabulary_tags(prompt: str, limit: int = 32) -> List[str]:
    """
    V11.1 open-vocabulary tag generator.
    This lets the system create new tags from the prompt instead of being limited
    to a fixed rule list. It is bounded per turn so memory stays clean.
    """
    words = _tokens(prompt)

    stop = {
        "the", "a", "an", "and", "or", "of", "in", "on", "under", "over",
        "with", "without", "this", "that", "these", "those", "to", "as",
        "it", "is", "are", "was", "were", "be", "being", "been", "for",
        "from", "into", "through", "show", "store", "analyze", "ingest",
        "photo", "description", "tags", "tag", "image", "shape", "memory",
        "leveon", "rendering", "future", "improves", "improve"
    }

    keep = []
    for w in words:
        c = _canonical_tag(w)
        if not c or c in stop:
            continue
        if len(c) < 3:
            continue
        if c not in keep:
            keep.append(c)

    # Add simple two-word phrase tags for visual concepts.
    phrase_tags = []
    for a, b in zip(words, words[1:]):
        if a in stop or b in stop:
            continue
        if len(a) < 3 or len(b) < 3:
            continue
        phrase = _canonical_tag(a + "_" + b)
        if phrase and phrase not in phrase_tags:
            phrase_tags.append(phrase)

    # Give visually meaningful open tags priority.
    priority_terms = {
        "golden", "light", "meadow", "autumn", "woman", "tree", "sky",
        "shadow", "river", "stone", "bridge", "flower", "mountain",
        "forest", "field", "moon", "sun", "blue", "green", "red",
        "violet", "gold", "silver", "mist", "rain", "snow", "smile",
        "face", "hands", "dress", "scarf", "window", "room"
    }

    priority = [x for x in keep if x in priority_terms]
    rest = [x for x in keep if x not in priority_terms]

    merged = []
    for tag in priority + rest + phrase_tags:
        if tag and tag not in merged:
            merged.append(tag)
        if len(merged) >= limit:
            break

    return merged

def _shape_vector(tags: List[str]) -> Dict[str, float]:
    t = set(tags)

    flow = 0.65
    boundary = 0.60
    memory = 0.80
    novelty = 0.68

    if "happy" in t or "positive_emotional_tone" in t:
        flow += 0.12
        boundary -= 0.03
    if "autumn" in t:
        memory += 0.08
    if "natural_landscape" in t:
        flow += 0.05
        novelty += 0.04
    if "subject_centered" in t:
        boundary += 0.12
    if "white_ash" in t:
        boundary += 0.10
        memory += 0.05

    def c(x):
        return max(0.0, min(1.0, round(x, 4)))

    return {
        "flow": c(flow),
        "boundary": c(boundary),
        "memory": c(memory),
        "novelty": c(novelty),
    }

def _render_hints(tags: List[str]) -> List[str]:
    t = set(tags)
    hints = []

    if "subject_centered" in t or "woman" in t:
        hints.append("use a centered vertical figure-node with gentle symmetry")
    if "natural_landscape" in t or "meadow" in t:
        hints.append("use horizon bands, organic curves, and low field arcs")
    if "tree" in t:
        hints.append("use branching vertical strokes and leaf clusters")
    if "autumn" in t:
        hints.append("use warm gold/amber accents and falling-point motifs")
    if "happy" in t or "positive_emotional_tone" in t:
        hints.append("increase upward flow, soft spacing, and open curves")
    if "white_ash" in t:
        hints.append("hold a pale centerline and containment ring")
    if not hints:
        hints.append("use balanced symbolic geometry and preserve the prompt signature")

    return hints

def _load_json(path: Path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _update_tag_index(tags: List[str], signature: str):
    index = _load_json(TAG_INDEX_PATH, {"tags": {}, "cooccurrence": {}, "signatures": {}})

    for tag in tags:
        index["tags"][tag] = int(index["tags"].get(tag, 0)) + 1

    for i, a in enumerate(tags):
        for b in tags[i+1:]:
            key = "|".join(sorted([a, b]))
            index["cooccurrence"][key] = int(index["cooccurrence"].get(key, 0)) + 1

    index["signatures"][signature] = {
        "tags": tags,
        "updated_ts": time.time(),
    }

    _write_json(TAG_INDEX_PATH, index)

def _render_image_shape_svg(image_shape: Dict[str, Any]) -> str:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    tags = image_shape.get("tags", [])
    signature = image_shape.get("visual_signature", "image_shape")
    h = image_shape.get("prompt_hash", "nohash")
    vector = image_shape.get("shape_vector", {})

    width = 1000
    height = 1000
    cx = width / 2
    cy = height / 2

    flow = float(vector.get("flow", 0.65))
    boundary = float(vector.get("boundary", 0.6))
    memory = float(vector.get("memory", 0.8))
    novelty = float(vector.get("novelty", 0.68))

    rings = 4 + int(boundary * 6)
    spokes = 8 + int(novelty * 18)

    polygons = []
    for r in range(1, rings + 1):
        radius = 40 * r + memory * 22
        pts = []
        for i in range(spokes):
            angle = 2 * math.pi * i / spokes + r * 0.31
            wobble = math.sin(i * 1.618 + flow * 5) * (8 + novelty * 10)
            x = cx + math.cos(angle) * (radius + wobble)
            y = cy + math.sin(angle) * (radius + wobble)
            pts.append(f"{x:.2f},{y:.2f}")
        polygons.append(
            f'<polygon points="{" ".join(pts)}" fill="none" stroke="currentColor" '
            f'stroke-width="{1 + (r % 3)}" opacity="{0.18 + r/(rings*5):.3f}"/>'
        )

    tag_line = " | ".join(html.escape(str(t)) for t in tags[:12])
    hint_line = " | ".join(html.escape(str(h)) for h in image_shape.get("render_hints", [])[:3])

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
svg {{
  background: #08070d;
  color: #d8c7ff;
  font-family: monospace;
}}
.title {{ fill: #f4e9ff; font-size: 24px; font-weight: 700; }}
.small {{ fill: #c7b7ff; font-size: 14px; }}
.gold {{ fill: #ffd978; font-size: 15px; }}
.center {{ fill: #fff7d6; font-size: 18px; font-weight: 700; }}
</style>

<rect x="0" y="0" width="{width}" height="{height}" fill="#08070d"/>
<circle cx="{cx}" cy="{cy}" r="360" fill="none" stroke="#433064" stroke-width="2" opacity="0.55"/>
<circle cx="{cx}" cy="{cy}" r="250" fill="none" stroke="#7059a8" stroke-width="1" opacity="0.35"/>
<circle cx="{cx}" cy="{cy}" r="125" fill="none" stroke="#ffd978" stroke-width="2" opacity="0.45"/>

<g transform="rotate({novelty * 180:.2f} {cx} {cy})">
{chr(10).join(polygons)}
</g>

<circle cx="{cx}" cy="{cy}" r="68" fill="#151022" stroke="#ffd978" stroke-width="2"/>
<text x="{cx}" y="{cy-6}" text-anchor="middle" class="center">IMAGE</text>
<text x="{cx}" y="{cy+22}" text-anchor="middle" class="small">shape memory</text>

<text x="38" y="54" class="title">Le’Veon V11 Image Topology Shape</text>
<text x="38" y="84" class="small">signature: {html.escape(signature)}</text>
<text x="38" y="108" class="small">prompt_hash: {html.escape(h)}</text>
<text x="38" y="132" class="small">flow={flow} boundary={boundary} memory={memory} novelty={novelty}</text>

<text x="38" y="820" class="gold">{tag_line}</text>
<text x="38" y="850" class="small">{hint_line}</text>
<text x="38" y="880" class="small">Photo description becomes symbolic image memory. Future renders can retrieve this shape.</text>
</svg>
'''

    filename = f"leveon_image_shape_{int(time.time())}_{h}.svg"
    out = GENERATED_DIR / filename
    out.write_text(svg, encoding="utf-8")
    return str(out.relative_to(ROOT))

def should_ingest_image_topology(prompt: str) -> bool:
    p = str(prompt or "").lower()
    triggers = [
        "ingest this photo",
        "photo description",
        "analyze it as image_shape",
        "image_shape",
        "store in spiral memory",
        "photo + tags",
        "image topology",
    ]
    return any(t in p for t in triggers)

def ingest_image_topology(prompt: str, data: Dict[str, Any], node: Dict[str, Any] = None, image_path: str = None):
    if not should_ingest_image_topology(prompt):
        return None

    ts = time.time()
    prompt = str(prompt or "")
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:12]

    user_tags = _extract_user_tags(prompt)
    auto_tags = _auto_tags(prompt) + _open_vocabulary_tags(prompt)

    tags = []
    for t in user_tags + auto_tags + ["image_shape", "visual_memory"]:
        c = _canonical_tag(t)
        if c and c not in tags:
            tags.append(c)

    vector = _shape_vector(tags)
    signature = f"image_shape_{hashlib.sha256(('|'.join(tags) + prompt_hash).encode()).hexdigest()[:10]}"
    hints = _render_hints(tags)

    image_shape = {
        "ts": ts,
        "prompt_hash": prompt_hash,
        "source": "prompt_description_with_tags",
        "tags": tags,
        "user_tags": user_tags,
        "auto_tags": auto_tags,
        "shape_vector": vector,
        "visual_signature": signature,
        "render_hints": hints,
        "linked_topology_image": image_path,
        "law": "v11_photo_description_to_symbolic_image_shape",
    }

    svg_path = _render_image_shape_svg(image_shape)
    image_shape["shape_svg"] = svg_path

    IMAGE_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with IMAGE_SHAPES_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(image_shape, ensure_ascii=False) + "\n")

    _update_tag_index(tags, signature)

    memory_entry = {
        "ts": ts,
        "turn": "image_topology_v11",
        "glyphs": tags,
        "shape_vector": vector,
        "image_shape": image_shape,
        "nonlinear_fold": {
            "present": vector,
            "past_echo": vector,
            "future_echo": vector,
        },
        "white_ash_lock": True,
        "co_creator": "john-9216-2077",
        "version": "v11_image_topology_library",
    }

    SYMBOLIC_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SYMBOLIC_MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(memory_entry, ensure_ascii=False) + "\n")

    LATTICE_DIR.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": ts,
        "prompt_hash": prompt_hash,
        "image_shape": image_shape,
        "memory_path": str(SYMBOLIC_MEMORY_PATH.relative_to(ROOT)),
        "shape_svg": svg_path,
        "created": True,
        "law": "v11_image_topology_ingested_to_memory",
    }

    with LATTICE_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    event["reply_note"] = (
        "[IMAGE TOPOLOGY NODE CREATED] "
        f"tags={', '.join(tags[:12])} "
        f"signature={signature} "
        f"shape_svg={svg_path}. "
        "The visual form is now stored as symbolic image memory for future rendering and comparison."
    )

    return event

if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:]) or "photo description: woman in autumn meadow tags 'Happy, Woman, Tree, Autumn, Meadow'"
    print(json.dumps(ingest_image_topology(prompt, {}, {}, None), indent=2, ensure_ascii=False))

