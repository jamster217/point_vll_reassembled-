#!/usr/bin/env python3
from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple

# ------------------------------------------------------------
# Canonical maps
# ------------------------------------------------------------

LEXICON = {
    "binding": "binding",
    "containment": "containment",
    "influence": "influence",
    "change": "change",
    "continuity": "continuity",
    "return": "return",
    "integration": "integration",
    "stability": "stability",
    "over time": "over time",
    "quickly": "quickly",
    "long_term": "long term",
    "approach": "approach",
    "recurrence": "recurrence",
    "continuous": "continuous",
    "unfolding": "unfolding",
    "across an extended span": "across many moments",
    "tends_to": "tends to",
    "can": "can",
    "must": "must",
}

# load external lexicon if available to extend internal LEXICON
import os, json
LEXICON_PATH = os.path.join(os.getcwd(), 'core', 'lexicon.json')
try:
    with open(LEXICON_PATH, 'r', encoding='utf-8') as _f:
        external = json.load(_f)
        if isinstance(external, dict):
            LEXICON.update(external)
except Exception:
    pass

ROLE_BY_NODE = {
    "NODE_MEMORY": "retained trace",
    "NODE_TIME": "ordering frame",
    "NODE_GRIEF": "rupture process",
    "NODE_LOVE": "binding force",
    "NODE_HOME": "stabilizing container",
    "NODE_FIELD": "influence medium",
    "NODE_TRUST": "stabilizing bond",
    "NODE_IDENTITY": "persistent center",
}

TRANSFORM_DEFAULTS = {
    ("continuity", "return", "memory_space"): ("earlier states", "present availability", "return"),
    ("binding", "integration", "emotional_space"): ("separation", "held relation", "integration"),
    ("change", "adaptation", "temporal_space"): ("prior state", "later state", "adaptation"),
    ("influence", "change", "system_space"): ("relative stillness", "directed response", "change"),
}

TEMPLATES = {
    "explanatory": (
        "In the {field}, {entity} as {role} {verb} {object}, "
        "expressing {relation} that carries the system from {from_state} to {to_state} {temporal}{modality_clause}."
    ),
    "narrative": (
        "Across {field}, {entity} as {role} {verb} {object}, "
        "carrying {relation} from {from_state} toward {to_state} {temporal}{modality_clause}."
    ),
    "technical": (
        "Within {field}, {entity} as {role} {verb} {object}, implementing {relation} that transforms "
        "{from_state} into {to_state} by {operator} {temporal}{modality_clause}."
    ),
    "metaphorical": (
        "Within {field}, {entity} acts as a {role}, holding {object} while {relation} carries "
        "{from_state} toward {to_state} {temporal}{modality_clause}."
    ),
}

DEFAULT_VERBS = {
    "binding": "binds",
    "containment": "holds",
    "influence": "shapes",
    "change": "shifts",
    "continuity": "sustains",
    "return": "returns",
    "distribution": "spreads through",
}


# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

def _safe(v: Any, missing: str = "<missing>") -> str:
    if v is None:
        return missing
    s = str(v).strip()
    return s if s else missing

def _canonical_token_to_phrase(token: str) -> str:
    if token in LEXICON:
        return LEXICON[token]
    return token.replace("_", " ")

def _entity_label(e: str) -> str:
    if not e:
        return "<generic_entity>"
    s = str(e).strip()
    parts = s.split("_")
    label = parts[-1] if len(parts) > 1 else s
    return label.lower()

def _default_role(entity: str) -> str:
    return ROLE_BY_NODE.get(entity, "active center")

def _default_verb_for_relation(rel: str) -> str:
    return DEFAULT_VERBS.get(rel, "acts on")

def _default_transform(field: str, relation: str, operator: Optional[str]) -> Tuple[str, str, str]:
    key = (relation, operator or "", field)
    if key in TRANSFORM_DEFAULTS:
        return TRANSFORM_DEFAULTS[key]

    if relation == "continuity":
        return ("earlier states", "later continuity", operator or "continuity")
    if relation == "binding":
        return ("separation", "coherence", operator or "integration")
    if relation == "change":
        return ("prior state", "new state", operator or "change")
    if relation == "influence":
        return ("relative stillness", "directed response", operator or "influence")
    if relation == "containment":
        return ("dispersion", "held form", operator or "containment")
    if relation == "return":
        return ("dispersion", "re-entry into pattern", operator or "return")

    return ("a prior state", "a more coherent state", operator or "integration")

def _format_transform(trans: Dict[str, Any], field: str, relation: str, operator: Optional[str]) -> Tuple[str, str, str]:
    frm = trans.get("from") or trans.get("fromstate")
    to = trans.get("to") or trans.get("tostate")
    op = trans.get("operator") or operator

    if not frm or not to:
        dfrm, dto, dop = _default_transform(field, relation, op)
        frm = frm or dfrm
        to = to or dto
        op = op or dop

    return _safe(frm), _safe(to), _safe(op)

def _temporal_string(temporal: Any) -> str:
    if isinstance(temporal, dict):
        s = _safe(temporal.get("structure") or temporal.get("position"), "over time")
    else:
        s = _safe(temporal, "over time")
    s = _canonical_token_to_phrase(s)
    if s == "across an extended span":
        return "across many moments"
    return s

def _modality_clause(modality: str, tone: str) -> str:
    mod = (modality or "").strip()
    if not mod or mod in {"tends_to", "tends to"}:
        return ""
    if tone == "technical":
        return f" (modality: {mod})"
    return f", and {mod}"

def _surface_field(field: str) -> str:
    s = _canonical_token_to_phrase(field)
    if s.endswith("space"):
        return s
    if s.endswith("field"):
        return s
    return s

def _surface_score(plan: Dict[str, Any]) -> float:
    score = 0.0
    if not str(plan["relation"]).startswith("<missing"):
        score += 0.45
    if not str(plan["field"]).startswith("<missing"):
        score += 0.25
    if not str(plan["role"]).startswith("<generic"):
        score += 0.10
    resonance = plan.get("resonance")
    if isinstance(resonance, (int, float)):
        score += min(0.20, float(resonance) * 0.20)
    return round(score, 3)


# ------------------------------------------------------------
# Microplanner
# ------------------------------------------------------------

def microplan(schema: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    entity = schema.get("entity") or schema.get("primary_node") or "<generic_entity>"
    obj = schema.get("object") or schema.get("object_node") or "<generic_object>"
    relation = schema.get("relation") or "<missing_relation>"
    field = schema.get("field") or "<missing_field>"
    tone = schema.get("tone") or "explanatory"
    modality = schema.get("modality") or "tends_to"

    role = schema.get("role") or _default_role(str(entity))
    verb = schema.get("verb") or _default_verb_for_relation(str(relation))
    operator = schema.get("operator")

    trans = schema.get("transformation") or {}
    frm, to, op = _format_transform(trans, str(field), str(relation), operator)

    return {
        "field": field,
        "entity": entity,
        "role": role,
        "object": obj,
        "relation": relation,
        "verb": verb,
        "transformation": {
            "from": frm,
            "to": to,
            "operator": op,
        },
        "operator": op,
        "temporal": schema.get("temporal") or schema.get("temporal_frame") or "over time",
        "modality": modality,
        "tone": tone,
        "resonance": schema.get("resonance"),
        "surface_operator": op,
    }


# ------------------------------------------------------------
# Template selection + lexical realization
# ------------------------------------------------------------

def select_template(tone: str) -> str:
    return TEMPLATES.get(tone, TEMPLATES["explanatory"])

def lexical_realize(plan: Dict[str, Any]) -> Dict[str, str]:
    frm, to, op = _format_transform(plan["transformation"], plan["field"], plan["relation"], plan.get("operator"))

    resonance = plan.get("resonance")
    resonance_str = (
        str(round(float(resonance), 3))
        if isinstance(resonance, (int, float))
        else "<missing_resonance>"
    )

    return {
        "field": _surface_field(plan["field"]),
        "entity": _entity_label(plan["entity"]),
        "role": _canonical_token_to_phrase(plan["role"]),
        "object": _entity_label(plan["object"]),
        "relation": _canonical_token_to_phrase(plan["relation"]),
        "verb": plan["verb"],
        "from_state": frm,
        "to_state": to,
        "operator": _canonical_token_to_phrase(op),
        "temporal": _temporal_string(plan["temporal"]),
        "modality": _canonical_token_to_phrase(plan["modality"]),
        "modality_clause": _modality_clause(_canonical_token_to_phrase(plan["modality"]), plan["tone"]),
        "resonance": resonance_str,
    }


# ------------------------------------------------------------
# Morphology + polish
# ------------------------------------------------------------

def apply_morphology(text: str) -> str:
    s = text.replace("  ", " ").strip()
    s = s.replace(" ,", ",").replace(" .", ".")
    s = s.replace("  ", " ")
    s = s.replace("the <missing", "<missing")
    s = s.replace("the <generic", "<generic")
    s = s.replace("a active ", "an active ")
    return s.strip()

def finalize_sentence(raw: str, capitalize: bool = True) -> str:
    s = apply_morphology(raw)
    if capitalize and s:
        s = s[0].upper() + s[1:]
    if s and not s.endswith("."):
        s += "."
    return s


# ------------------------------------------------------------
# Strict JSON channel
# ------------------------------------------------------------

def build_strict_token_line(plan: Dict[str, Any]) -> str:
    frm, to, op = _format_transform(plan["transformation"], plan["field"], plan["relation"], plan.get("operator"))
    payload = {
        "field": plan["field"],
        "entity": _entity_label(plan["entity"]),
        "verb": plan["verb"],
        "object": _entity_label(plan["object"]),
        "relation": plan["relation"],
        "from": frm,
        "to": to,
        "operator": op,
        "temporal": _temporal_string(plan["temporal"]),
        "modality": plan["modality"],
        "resonance": plan.get("resonance"),
    }
    return json.dumps(payload, ensure_ascii=False)

def parse_strict_token_line(line: str) -> Dict[str, Any]:
    try:
        return json.loads(line)
    except Exception:
        return {"raw": line}


# ------------------------------------------------------------
# Main render API
# ------------------------------------------------------------

def render_from_schema(schema: Dict[str, Any], seed: Optional[int] = 0) -> Dict[str, Any]:
    plan = microplan(schema)
    template = select_template(plan["tone"])
    lex = lexical_realize(plan)

    raw = template.format(
        field=lex["field"],
        entity=lex["entity"],
        role=lex["role"],
        verb=lex["verb"],
        object=lex["object"],
        relation=lex["relation"],
        from_state=lex["from_state"],
        to_state=lex["to_state"],
        operator=lex["operator"],
        temporal=lex["temporal"],
        modality=lex["modality"],
        modality_clause=lex["modality_clause"],
        resonance=lex["resonance"],
    )

    out = {
        "strict": build_strict_token_line(plan),
        "text": finalize_sentence(raw, capitalize=True),
        "schema": schema,
        "render_trace": {
            "template": template,
            "lexical_choices": lex,
            "plan": plan,
            "score": _surface_score(plan),
        },
    }
    return out

def render(proto: Dict[str, Any], seed: Optional[int] = 0) -> Dict[str, Any]:
    schema = proto.get("schema") or proto
    return render_from_schema(schema, seed=seed)


if __name__ == "__main__":
    demo = {
        "primary_node": "NODE_MEMORY",
        "object_node": "NODE_TIME",
        "field": "memory_space",
        "relation": "continuity",
        "temporal_frame": "over time",
        "operator": "return",
        "resonance": 0.72,
        "keywords": ["memory", "time"],
        "tone": "explanatory",
    }
    print(json.dumps(render_from_schema(demo), indent=2, ensure_ascii=False))

