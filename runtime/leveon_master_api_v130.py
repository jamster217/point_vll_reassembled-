
--- runtime/leveon_master_api_v130.py:163-172 ---
  163: def _layer5_final_mouth(prompt: str, answer: str, parsed: Dict[str, Any], routed: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
  164:     """
  165:     Final-mouth handoff.
  166:     Does not invent content.
  167:     It only lets Layer5 preserve a real final_shape if one exists.
  168:     """
  169:     shape_debug = parsed.get("_shape_debug") or {}
  170: 
  171:     packet = {
  172:         "core_meaning": prompt,

--- runtime/leveon_master_api_v130.py:168-177 ---
  168:     """
  169:     shape_debug = parsed.get("_shape_debug") or {}
  170: 
  171:     packet = {
  172:         "core_meaning": prompt,
  173:         "answer": answer,
  174:         "symbols": parsed.get("symbols") or [],
  175:         "phenome_stream": shape_debug.get("phenome_stream") or [],
  176:         "shape_vector": shape_debug.get("shape_vector"),
  177:         "vector_field": shape_debug.get("vector_field"),

--- runtime/leveon_master_api_v130.py:174-183 ---
  174:         "symbols": parsed.get("symbols") or [],
  175:         "phenome_stream": shape_debug.get("phenome_stream") or [],
  176:         "shape_vector": shape_debug.get("shape_vector"),
  177:         "vector_field": shape_debug.get("vector_field"),
  178:         "shape_packet": {},
  179:     }
  180: 
  181:     # Carry only an already-rendered meaningful surface.
  182:     for key in ("final_shape", "veilweil_surface", "weilveil_surface", "gravity_well_surface", "final_english"):
  183:         val = shape_debug.get(key)

--- runtime/leveon_master_api_v130.py:178-187 ---
  178:         "shape_packet": {},
  179:     }
  180: 
  181:     # Carry only an already-rendered meaningful surface.
  182:     for key in ("final_shape", "veilweil_surface", "weilveil_surface", "gravity_well_surface", "final_english"):
  183:         val = shape_debug.get(key)
  184:         if val:
  185:             packet["shape_packet"][key] = val
  186: 
  187:     # If no real final_shape exists, do not pretend the weak answer is one.

--- runtime/leveon_master_api_v130.py:181-190 ---
  181:     # Carry only an already-rendered meaningful surface.
  182:     for key in ("final_shape", "veilweil_surface", "weilveil_surface", "gravity_well_surface", "final_english"):
  183:         val = shape_debug.get(key)
  184:         if val:
  185:             packet["shape_packet"][key] = val
  186: 
  187:     # If no real final_shape exists, do not pretend the weak answer is one.
  188:     if not packet["shape_packet"]:
  189:         return answer, {
  190:             "layer5_final_mouth": "skipped_no_final_shape",

--- runtime/leveon_master_api_v130.py:183-192 ---
  183:         val = shape_debug.get(key)
  184:         if val:
  185:             packet["shape_packet"][key] = val
  186: 
  187:     # If no real final_shape exists, do not pretend the weak answer is one.
  188:     if not packet["shape_packet"]:
  189:         return answer, {
  190:             "layer5_final_mouth": "skipped_no_final_shape",
  191:             "reason": "no final_shape/veilweil_surface/gravity_well_surface present",
  192:         }

--- runtime/leveon_master_api_v130.py:184-193 ---
  184:         if val:
  185:             packet["shape_packet"][key] = val
  186: 
  187:     # If no real final_shape exists, do not pretend the weak answer is one.
  188:     if not packet["shape_packet"]:
  189:         return answer, {
  190:             "layer5_final_mouth": "skipped_no_final_shape",
  191:             "reason": "no final_shape/veilweil_surface/gravity_well_surface present",
  192:         }
  193: 

--- runtime/leveon_master_api_v130.py:186-195 ---
  186: 
  187:     # If no real final_shape exists, do not pretend the weak answer is one.
  188:     if not packet["shape_packet"]:
  189:         return answer, {
  190:             "layer5_final_mouth": "skipped_no_final_shape",
  191:             "reason": "no final_shape/veilweil_surface/gravity_well_surface present",
  192:         }
  193: 
  194:     rendered = _layer5_render(packet)
  195:     return rendered, {

--- runtime/leveon_master_api_v130.py:187-196 ---
  187:     # If no real final_shape exists, do not pretend the weak answer is one.
  188:     if not packet["shape_packet"]:
  189:         return answer, {
  190:             "layer5_final_mouth": "skipped_no_final_shape",
  191:             "reason": "no final_shape/veilweil_surface/gravity_well_surface present",
  192:         }
  193: 
  194:     rendered = _layer5_render(packet)
  195:     return rendered, {
  196:         "layer5_final_mouth": "active",

--- runtime/leveon_master_api_v130.py:194-203 ---
  194:     rendered = _layer5_render(packet)
  195:     return rendered, {
  196:         "layer5_final_mouth": "active",
  197:         "packet_keys": sorted(packet.keys()),
  198:         "shape_packet_keys": sorted(packet["shape_packet"].keys()),
  199:     }
  200: 
  201: def run(prompt: str) -> Dict[str, Any]:
  202:     parsed = parse_prompt(prompt)
  203:     routed = route(parsed)

--- runtime/leveon_master_api_v130.py:220-229 ---
  220:             "symbols": parsed.get("symbols"),
  221:             "field_signature": parsed.get("field_signature"),
  222:             "law": "english_is_final_interpreter_not_primary_generator",
  223:         },
  224:         "debug_shape_packet": parsed.get("_shape_debug"),
  225:         "layer5_meta": layer5_meta,
  226:     }
  227: 
  228:     try:
  229:         LOG.parent.mkdir(parents=True, exist_ok=True)

--- runtime/leveon_master_api_v130.py:235-244 ---
  235:     return packet
  236: 
  237: # === V13.1 KERNEL SHAPE BRIDGE FIRST ===
  238: # Live law:
  239: # /api/chat must try real kernel -> shape_packet -> Layer5 before old v130 mouth logic.
  240: 
  241: try:
  242:     _V131_PREV_RUN = run
  243: except NameError:
  244:     _V131_PREV_RUN = None

--- runtime/leveon_master_api_v130.py:246-255 ---
  246: def run(prompt: str):
  247:     bridge_error = None
  248: 
  249:     try:
  250:         from runtime.kernel_shape_bridge_v131 import answer as _v131_kernel_answer
  251:         out = _v131_kernel_answer(prompt)
  252: 
  253:         bridge_meta = {}
  254:         if isinstance(out, dict):
  255:             bridge_meta = out.get("kernel_shape_bridge_v131") or {}

--- runtime/leveon_master_api_v130.py:251-260 ---
  251:         out = _v131_kernel_answer(prompt)
  252: 
  253:         bridge_meta = {}
  254:         if isinstance(out, dict):
  255:             bridge_meta = out.get("kernel_shape_bridge_v131") or {}
  256: 
  257:         if (
  258:             isinstance(out, dict)
  259:             and out.get("ok") is True
  260:             and bridge_meta.get("kernel_called") is True

--- runtime/leveon_master_api_v130.py:264-273 ---
  264:                 "active": True,
  265:                 "phase": "v131_kernel_shape_bridge_first",
  266:                 "node": "44_SPIRAL_CORE",
  267:                 "intent": "kernel_shape",
  268:                 "symbols": ["kernel_called", "shape_packet", "layer5"],
  269:                 "field_signature": "92162077",
  270:                 "law": "kernel_first_shape_then_english",
  271:             }
  272:             return out
  273: 
====================================================================================================
