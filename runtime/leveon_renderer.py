#!/usr/bin/env python3
"""
runtime/leveon_renderer.py — Kernel-aware semantic algebra renderer

Purpose:
- Accepts proto packets from the current Leveon path
- Builds a semantic schema from route + kernel + shape
- Renders cleaner English than the old proto/debug renderer
- Exposes compatibility aliases for older callers

Compatible proto example:
{
  "input_text": "what is memory",
  "shape": {"keywords": ["memory"], "length": 42},
  "kernel": {"tendency": "compress", "vector": 0.34},
  "route": {
    "primarynode": "NODE_MEMORY",
    "secondarynode": "NODE_OUTPUT",
    "contextnode": "CTX_GENERAL"
  }
}
"""

from __future__ import annotations

print("[TRACE] entering runtime/leveon_renderer.py", flush=True)
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from core.schema_mutator import choose_schema


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

DEFAULT_GLYPH_PATHS = [
    Path.home() / "point_vll_reassembled" / "symbolic_layers" / "glyph_definitions.json",
    Path.home() / "point_vll_reassembled" / "symbolic_memory" / "glyph_definitions.json",
    Path.home() / "point_vll_reassembled" / "assets" / "glyphs" / "glyph_definitions.json",
    Path.home() / "point_vll_reassembled" / "assets" / "glyphs" / "glyph_registry_21_60.json",
]


LEXICON_PATH = Path.home() / "point_vll_reassembled" / "core" / "lexicon.json"


def load_lexicon(path: Optional[str] = None) -> Dict[str, str]:
    p = Path(path) if path else LEXICON_PATH
    if not p.exists():
        return {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


LEXICON = load_lexicon()


def lex(key: str, fallback: str) -> str:
    return str(LEXICON.get(str(key), fallback))


# ------------------------------------------------------------
# Semantic algebra hints
# ------------------------------------------------------------

TENDENCY_TO_RELATION = {
    "compress": "binding",
    "expand": "change",
    "probe": "influence",
    "stabilize": "continuity",
    "recurse": "return",
    "mirror": "reflection",
    "default": "shaping",
}

TENDENCY_TO_VERB = {
    "compress": "binds",
    "expand": "unfolds",
    "probe": "tests",
    "stabilize": "anchors",
    "recurse": "returns through",
    "mirror": "reflects through",
    "default": "shapes",
}

DOMAIN_KEYWORD_HINTS = {
    "emotional": {
        "love", "grief", "loss", "sad", "hurt", "care", "feeling", "father",
        "mother", "child", "home", "trust", "anger", "lonely", "relationship"
    },
    "memory": {"memory", "remember", "trace", "imprint", "recall", "archive"},
    "time": {"time", "past", "future", "before", "after", "sequence", "history"},
    "systems": {"system", "feedback", "signal", "network", "stability", "collapse", "lattice"},
    "field": {"field", "influence", "resonance", "pressure", "distribution", "coherence"},
    "technical": {"python", "function", "code", "kernel", "schema", "renderer", "module", "api"},
}

FIELD_TO_DOMAIN = {
    "general_space": "general",
    "system_space": "systems",
    "systems_space": "systems",
    "memory_space": "memory",
    "emotional_space": "emotional",
    "relational_space": "emotional",
    "field_space": "field",
    "technical_space": "technical",
    "code_space": "technical",
}

DOMAIN_TO_ROLE = {
    "emotional": "relational center",
    "memory": "retained trace",
    "time": "ordering frame",
    "systems": "stabilizing node",
    "field": "influence medium",
    "technical": "active component",
    "general": "active center",
}

ROLE_BY_NODE = {
    "NODE_MEMORY": "retained trace",
    "NODE_TIME": "ordering frame",
    "NODE_IDENTITY": "persistent center",
    "NODE_GRIEF": "rupture process",
    "NODE_LOVE": "binding force",
    "NODE_TRUST": "stabilizing bond",
    "NODE_HOME": "stabilizing container",
    "NODE_FIELD": "influence medium",
    "NODE_CHILD": "developing center",
}

PRIMITIVE_TRACE_HINTS = {
    "binding": ["binding", "continuity"],
    "change": ["change", "distribution"],
    "influence": ["influence", "pressure"],
    "continuity": ["continuity", "return"],
    "return": ["return", "continuity"],
    "reflection": ["difference", "return"],
    "shaping": ["influence", "boundary"],
}


# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

def _clean_token(x: str) -> str:
    s = str(x or "").strip()
    s = re.sub(r"^[A-Z]+_", "", s)
    s = s.replace("__", "_")
    s = s.replace("_", " ")
    s = s.lower().strip()
    return s or "generic"


def _first_existing(paths: List[Path]) -> Optional[Path]:
    for p in paths:
        if p.exists():
            return p
    return None


def _safe_keywords(shape: Dict[str, Any], input_text: str) -> List[str]:
    kws = shape.get("keywords", [])
    if isinstance(kws, list):
        out = [str(x).strip().lower() for x in kws if str(x).strip()]
        if out:
            return out
    text = str(input_text or "").lower()
    return re.findall(r"[a-z0-9]{3,}", text)[:6]


def _temporal_from_length(n: int) -> Tuple[str, str]:
    if n < 40:
        return ("present", "quickly")
    if n < 120:
        return ("present", "over time")
    return ("present", "across an extended span")


# ------------------------------------------------------------
# Glyph loading
# ------------------------------------------------------------

def load_glyphs(path: Optional[str] = None) -> List[Dict[str, Any]]:
    if path:
        paths = [Path(path)]
    else:
        paths = DEFAULT_GLYPH_PATHS

    chosen = _first_existing(paths)
    if not chosen:
        return []

    try:
        raw = json.loads(chosen.read_text(encoding="utf-8"))
    except Exception:
        return []

    entries: List[Dict[str, Any]] = []

    if isinstance(raw, list):
        entries = raw
    elif isinstance(raw, dict):
        if isinstance(raw.get("glyphs"), list):
            entries = raw["glyphs"]
        else:
            all_dicts = all(isinstance(v, dict) for v in raw.values())
            if all_dicts:
                for k, v in raw.items():
                    ent = dict(v)
                    ent.setdefault("name", k)
                    entries.append(ent)
            else:
                entries = [raw]

    out: List[Dict[str, Any]] = []
    for e in entries:
        name = e.get("name") or e.get("id") or e.get("label") or ""
        symbol = e.get("emoji") or e.get("symbol") or e.get("sigil") or e.get("glyph") or ""
        keywords: List[str] = []

        if isinstance(e.get("keywords"), list):
            keywords = [str(x).lower() for x in e["keywords"]]
        elif isinstance(e.get("tags"), list):
            keywords = [str(x).lower() for x in e["tags"]]
        else:
            keywords = re.findall(r"[a-z0-9]{3,}", str(name).lower())
            if "description" in e:
                keywords += re.findall(r"[a-z0-9]{3,}", str(e["description"]).lower())[:4]

        out.append(
            {
                "name": str(name),
                "symbol": str(symbol),
                "keywords": list(dict.fromkeys(k for k in keywords if k)),
                "raw": e,
            }
        )

    return out


def find_glyph_for_token(token: str, glyphs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    t = str(token or "").lower().strip()
    if not t:
        return None

    for g in glyphs:
        if g["name"].lower() == t:
            return g

    for g in glyphs:
        if t in g["keywords"]:
            return g

    for g in glyphs:
        if t in g["name"].lower():
            return g

    for g in glyphs:
        for kw in g["keywords"]:
            if kw.startswith(t[:3]):
                return g

    return None


# ------------------------------------------------------------
# Schema inference
# ------------------------------------------------------------

def node_to_label(node: str) -> str:
    return _clean_token(node)


def context_to_field(ctx: str) -> str:
    c = str(ctx or "CTX_GENERAL").strip()
    if c.startswith("CTX_"):
        c = c[4:]
    return _clean_token(c) + "_space"


def infer_domain(field: str, keywords: List[str], entity: str, obj: str) -> str:
    if field in FIELD_TO_DOMAIN:
        return FIELD_TO_DOMAIN[field]

    score = {k: 0 for k in DOMAIN_KEYWORD_HINTS.keys()}
    hay = set(keywords + [entity, obj, field.replace("_space", "")])

    for domain, hints in DOMAIN_KEYWORD_HINTS.items():
        score[domain] = len(hints.intersection(hay))

    best = max(score.items(), key=lambda kv: kv[1])
    return best[0] if best[1] > 0 else "general"


def infer_role(domain: str, relation: str, entity: str, obj: str, entity_node: str = "") -> str:
    node_key = str(entity_node or "").strip().upper()
    if node_key in ROLE_BY_NODE:
        return ROLE_BY_NODE[node_key]
    if entity == "field":
        return "influence medium"
    if entity == "memory":
        return "retained trace"
    if entity == "time":
        return "ordering frame"
    if entity in {"father", "mother"}:
        return "relational origin"
    if entity == "home":
        return "stabilizing container"
    if relation == "binding":
        return "binding center"
    if relation == "return":
        return "recursive anchor"
    return DOMAIN_TO_ROLE.get(domain, "active center")


def infer_transformation(
    relation: str,
    domain: str,
    tendency: str,
    keywords: List[str],
    entity: str,
) -> Dict[str, str]:
    # tighter than the old hardcoded generic pair
    if domain == "emotional":
        if "grief" in keywords or "loss" in keywords:
            return {
                "from": "an intact bond",
                "to": "a reconfigured bond under loss",
                "operator": "integration",
            }
        if "love" in keywords:
            return {
                "from": "separation",
                "to": "sustained mutual influence",
                "operator": "binding",
            }

    if domain == "memory":
        return {
            "from": "latent trace",
            "to": "reactivated pattern",
            "operator": "return",
        }

    if domain == "time":
        return {
            "from": "one state",
            "to": "the next ordered state",
            "operator": "change",
        }

    if domain == "systems":
        return {
            "from": "drift",
            "to": "coherence",
            "operator": "stabilization",
        }

    if domain == "technical":
        if tendency == "probe":
            return {
                "from": "uncertainty",
                "to": "diagnosed structure",
                "operator": "inspection",
            }
        return {
            "from": "unstructured state",
            "to": "coherent structure",
            "operator": "integration",
        }

    if relation == "binding":
        return {
            "from": "separation",
            "to": "coherence",
            "operator": "integration",
        }
    if relation == "change":
        return {
            "from": "one form",
            "to": "an altered form",
            "operator": "change",
        }
    if relation == "influence":
        return {
            "from": "relative stillness",
            "to": "directed response",
            "operator": "pressure",
        }
    if relation == "continuity":
        return {
            "from": "instability",
            "to": "stability",
            "operator": "anchoring",
        }
    if relation == "return":
        return {
            "from": "dispersion",
            "to": "re-entry into pattern",
            "operator": "recurrence",
        }

    return {
        "from": "a less organized state",
        "to": "a more coherent pattern",
        "operator": "change",
    }


def build_schema(proto: Dict[str, Any]) -> Dict[str, Any]:
    route = proto.get("route", {}) or {}
    kernel = proto.get("kernel", {}) or {}
    shape = proto.get("shape", {}) or {}
    input_text = str(proto.get("input_text", "") or "")

    entity_node = route.get("primarynode", "NODE_GENERIC")
    object_node = route.get("secondarynode", "NODE_AUX")

    entity = node_to_label(entity_node)
    obj = node_to_label(object_node)
    field = context_to_field(route.get("contextnode", "CTX_GENERAL"))

    tendency = str(kernel.get("tendency", "default")).lower()
    relation = TENDENCY_TO_RELATION.get(tendency, TENDENCY_TO_RELATION["default"])
    verb = TENDENCY_TO_VERB.get(tendency, TENDENCY_TO_VERB["default"])

    keywords = _safe_keywords(shape, input_text)
    domain = infer_domain(field, keywords, entity, obj)
    role = infer_role(domain, relation, entity, obj, entity_node)
    transformation = infer_transformation(relation, domain, tendency, keywords, entity)

    temporal_position, temporal_structure = _temporal_from_length(int(shape.get("length", 0) or 0))
    resonance = kernel.get("vector", None)

    primitive_trace = list(dict.fromkeys(PRIMITIVE_TRACE_HINTS.get(relation, ["influence"])))

    return {
        "entity": entity,
        "object": obj,
        "role": role,
        "relation": relation,
        "verb": verb,
        "field": field,
        "domain": domain,
        "transformation": transformation,
        "temporal": {
            "position": temporal_position,
            "structure": temporal_structure,
        },
        "keywords": keywords,
        "resonance": resonance,
        "primitive_trace": primitive_trace,
        "source_input": input_text,
    }


# ------------------------------------------------------------
# Rendering
# ------------------------------------------------------------

def _decorate(token: str, glyphs: List[Dict[str, Any]]) -> str:
    g = find_glyph_for_token(token, glyphs)
    if g and g.get("symbol"):
        return f"{g['symbol']} {token}"
    return token


def _maybe_resonance_tail(resonance: Any) -> str:
    if not isinstance(resonance, (int, float)):
        return ""
    if resonance >= 0.75:
        return " The resonance is high, so the pattern holds strongly."
    if resonance >= 0.45:
        return " The resonance is moderate, so the pattern remains active."
    return " The resonance is light, so the pattern stays present but less dense."


def render_from_schema(schema: Dict[str, Any], glyphs: List[Dict[str, Any]]) -> str:
    source_input = (schema.get("source_input") or "").lower().strip()

    raw_entity = schema["entity"]
    raw_obj = schema["object"]

    entity = _decorate(raw_entity, glyphs)

    if raw_obj in {"aux", "generic"}:
        if raw_entity == "memory":
            raw_obj = "the present state"
        elif raw_entity == "grief":
            raw_obj = "a living bond"
        elif raw_entity == "love":
            raw_obj = "another life"
        elif raw_entity == "time":
            raw_obj = "memory"
        else:
            raw_obj = "the field"

    obj = _decorate(raw_obj, glyphs)

    field_key = schema["field"]
    field = lex(field_key, field_key.replace("_", " "))

    relation_key = schema["relation"]
    relation = lex(relation_key, relation_key)

    verb_key = schema["verb"]
    verb = lex(verb_key, verb_key)

    trans = dict(schema["transformation"])
    trans["operator"] = lex(trans.get("operator", ""), trans.get("operator", ""))

    temporal = schema["temporal"]["structure"]
    temporal = lex(temporal, temporal)

    # semantic pair overrides
    if "time" in source_input and "memory" in source_input:
        field = "temporal space"
        relation = "influence"
        verb = "shapes"
        obj = "memory"
        trans = {
            "from": "earlier states",
            "to": "later availability",
            "operator": "change",
        }
        temporal = "over time"

    elif "past" in source_input and "present" in source_input and "memory" in source_input:
        field = "memory space"
        relation = "continuity"
        verb = "carries into"
        obj = "the present"
        trans = {
            "from": "past states",
            "to": "present continuity",
            "operator": "return",
        }
        temporal = "over time"

    elif raw_entity == "grief":
        field = "emotional space"
        relation = "binding"
        verb = "holds to"
        trans = {
            "from": "an intact bond",
            "to": "a reconfigured bond under loss",
            "operator": "integration",
        }
        temporal = "over time"

    elif raw_entity == "love":
        field = "emotional space"
        relation = "binding"
        verb = "binds"
        trans = {
            "from": "separation",
            "to": "sustained mutual influence",
            "operator": "binding",
        }
        temporal = "over time"

    if temporal in {"quickly", "across an extended span"}:
        temporal = lex("over time", "over time")

    obj = lex(raw_obj, obj)

    return (
        f"In {field}, {entity} {verb} {obj}, "
        f"moving from {trans['from']} to {trans['to']} "
        f"through {trans['operator']} {temporal}."
    )




def render_from_proto(proto: Dict[str, Any], glyph_path: Optional[str] = None) -> str:
    glyphs = load_glyphs(glyph_path)
    schema = build_schema(proto)
    schema = choose_schema(schema, proto.get("input_text", ""))
    return render_from_schema(schema, glyphs)


def render(proto: Dict[str, Any], glyph_path: Optional[str] = None) -> Dict[str, Any]:
    glyphs = load_glyphs(glyph_path)
    schema = build_schema(proto)
    schema = choose_schema(schema, proto.get("input_text", ""))
    text = render_from_schema(schema, glyphs)
    return {
        "text": text,
        "schema": schema,
        "trace": {
            "entity": schema["entity"],
            "object": schema["object"],
            "relation": schema["relation"],
            "field": schema["field"],
            "domain": schema["domain"],
            "primitive_trace": schema["primitive_trace"],
            "score": schema.get("_score"),
            "alternatives": schema.get("_alternatives", []),
        },
    }


def extract_renderer_rules() -> Dict[str, Any]:
    return {
        "semantic_algebra": {
            "tendency_to_relation": TENDENCY_TO_RELATION,
            "tendency_to_verb": TENDENCY_TO_VERB,
        },
        "schema_fields": [
            "entity",
            "object",
            "role",
            "relation",
            "verb",
            "field",
            "domain",
            "transformation",
            "temporal",
            "keywords",
            "resonance",
            "primitive_trace",
        ],
        "template_family": "kernel-aware semantic algebra renderer",
    }


# ------------------------------------------------------------
# Backward-compatible aliases
# ------------------------------------------------------------

renderfromproto = render_from_proto
renderfromschema = render_from_schema
extractrendererrules = extract_renderer_rules


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if p.exists():
            try:
                proto = json.loads(p.read_text(encoding="utf-8"))
                print(json.dumps(render(proto), ensure_ascii=False))
            except Exception as e:
                print(json.dumps({"error": "failed_to_render_proto", "detail": str(e)}, ensure_ascii=False))
                sys.exit(2)
        else:
            print(json.dumps({"error": f"Proto file not found: {p}"}, ensure_ascii=False))
            sys.exit(2)
    else:
        print(json.dumps(extract_renderer_rules(), indent=2, ensure_ascii=False))

