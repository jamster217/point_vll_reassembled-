from __future__ import annotations

class StyleGovernor:
 @staticmethod
 def select_mode(message: str, meta: dict | None = None) -> str:
 meta = meta or {}
 low = str(message or "").lower()

 anxious_terms = [
 "anxious", "worried", "overwhelmed", "stress",
 "panic", "breathe", "falling apart", "scared"
 ]
 practical_terms = [
 "python", "debug", "traceback", "import", "error", "fix",
 "bash", "flask", "500", "route", "directory", "termux"
 ]
 emotional_terms = [
 "miss", "heavy", "feel", "dad", "grief", "hurt",
 "loss", "photo", "old"
 ]

 if any(term in low for term in anxious_terms):
 return "grounded"

 if any(term in low for term in practical_terms):
 return "steady"

 if bool(meta.get("retrieval_context")) or any(term in low for term in emotional_terms):
 return "soft"

 return "plain"

def get_style_policy(style_name: str) -> dict:
 policies = {
 "plain": {
 "temp": 0.4,
 "top_p": 0.5,
 "stabilize": False,
 "trim_required": False,
 "max_resonance": 0.5,
 },
 "steady": {
 "temp": 0.2,
 "top_p": 0.1,
 "stabilize": True,
 "trim_required": False,
 "max_resonance": 0.2,
 },
 "grounded": {
 "temp": 0.4,
 "top_p": 0.5,
 "stabilize": True,
 "trim_required": True,
 "max_resonance": 0.2,
 },
 "soft": {
 "temp": 0.7,
 "top_p": 0.9,
 "stabilize": False,
 "trim_required": False,
 "max_resonance": 0.8,
 },
 }
 return policies.get(style_name, policies["plain"])

def get_style_config(mode: str) -> dict:
 policy = get_style_policy(mode)
 return {
 "temp": policy["temp"],
 "top_p": policy["top_p"],
 }

def apply_grounded_surface(reply: str) -> str:
 """
 Stabilizes floaty/interpretive phrasing into grounded, steady-state output.
 """
 reply = str(reply or "")

 grounded_rewrites = {
 "This is active around a feeling that something is unresolved and heavy.": "This is heavy, so take it one step at a time.",
 "What it circles is simple:": "This is active here, and it can be approached one step at a time:",
 "It feels as though": "This is active here, and",
 "There is a sense that": "This is active here, and",
 }

 for old, new in grounded_rewrites.items():
 if old in reply:
 reply = reply.replace(old, new)

 # Broader grounded catch for pressure-style phrasing that slips through upstream
 low = reply.lower()
 if "pressure" in low and "gather" in low:
 return "This is heavy, so take it one step at a time."

 return reply

def apply_style_to_final_reply(reply: str, style_policy: dict | None = None) -> str:
 """
 Final style-governed cleanup pass.
 Keeps app_chatroom.py thin and centralizes surface policy here.
 """
 import re

 reply = str(reply or "").strip()
 style_policy = style_policy or {}
 max_resonance = float(style_policy.get("max_resonance", 0.5))

 if not reply:
 return reply

 # Soft grief directness: keep the emotional lane direct and human
 if max_resonance >= 0.8:
 if "This is active around a feeling that something is unresolved and heavy." in reply:
 reply = reply.replace(
 "This is active around a feeling that something is unresolved and heavy.",
 "What it circles is simple: you miss your dad, and it still hurts."
 )

 # Soft grief directness
 if max_resonance >= 0.8:
 soft_rewrites = {
 "This is active around a feeling that something is unresolved and heavy.": "What it circles is simple: you miss your dad, and it still hurts.",
 }
 for old_phrase, new_phrase in soft_rewrites.items():
 if old_phrase in reply:
 reply = reply.replace(old_phrase, new_phrase)

 # Grounded surface stabilization
 if style_policy.get("trim_required", False):
 reply = apply_grounded_surface(reply)
 reply = re.sub(
 r'^This carries the weight of:\s*".*?"[.!?]?\s*',
 '',
 str(reply),
 flags=re.DOTALL,
 ).strip()

 # Prune vestigial structural filler if stronger content exists
 filler = ""
 if filler in reply:
 has_anchor = "This carries the" in reply or "The pull of" in reply
 if has_anchor or len(reply) > len(filler) + 10:
 reply = reply.replace(filler, "").replace(" ", " ").strip()

 # Collapse duplicate weight-anchor phrasing
 if "This carries the weight of:" in reply and "This carries the same weight as:" in reply:
 parts = [p.strip() for p in reply.split(". ") if p.strip()]
 filtered = []
 seen_weight_quote = set()

 for part in parts:
 low = part.lower()
 if low.startswith("this carries the weight of:") or low.startswith("this carries the same weight as:"):
 quote = part.split(":", 1)[1].strip().strip('"').strip()
 qnorm = " ".join(quote.lower().split())
 if qnorm in seen_weight_quote:
 continue
 seen_weight_quote.add(qnorm)
 filtered.append(part)
 else:
 filtered.append(part)

 reply = ". ".join(filtered).strip()
 if reply and not reply.endswith((".", "!", "?")):
 reply += "."

 # General exact sentence dedupe
 parts = [p.strip() for p in reply.split(". ") if p.strip()]
 seen = set()
 final_parts = []

 for pt in parts:
 clean = " ".join(pt.lower().rstrip(".").split())
 if clean in seen:
 continue
 seen.add(clean)
 final_parts.append(pt)

 reply = ". ".join(final_parts).strip()
 if reply and not reply.endswith((".", "!", "?")):
 reply += "."

 return reply

