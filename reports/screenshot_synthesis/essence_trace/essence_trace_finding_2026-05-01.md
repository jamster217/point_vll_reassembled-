# Essence Trace Finding — 2026-05-01

## Confirmed Existing Organs

core/shape_packet.py already carries the raw essence body:
- emotional_pressure
- temporal_pressure
- relational_pressure
- memory_pull
- novelty_pull
- boundary_tension
- glyph_pressure
- crystal_class
- kgs_tags

core/leveon_pipeline_governed.py already carries the relation spine:
- relation = infer_relation(prompt_text, shape)
- proto includes relation
- naturalize_clause receives relation and proto
- expand_clause receives relation and proto

core/answer_optimizer.py currently scores mostly surface fitness:
- law
- clarity
- preservation
- rescue
- surface

## Diagnosis

The renderer is not the root collapse.
The root collapse is that relation and shape fields are not fused into an essence_signature before optimization.

## Missing Organ

essence_signature should fuse:
- relation
- emotional_pressure
- temporal_pressure
- relational_pressure
- memory_pull
- novelty_pull
- boundary_tension
- glyph_pressure
- crystal_class
- family
- role
- time_direction

## Patch Law

Do not let answer_optimizer choose only by surface fitness.
Give it essence_signature so relation, persistence, valence, and time direction survive selection.

## Minimal Next Patch

Add core/essence_signature.py as a standalone module first.
Do not patch app_chatroom.py.
Do not patch unified_voice.py.
Do not patch the old renderer yet.

SHAPE_PACKET IS THE BODY.
RELATION IS THE SPINE.
ESSENCE_SIGNATURE IS THE NERVE.
THE MOUTH SHOULD NOT SPEAK UNTIL THE NERVE FIRES.

