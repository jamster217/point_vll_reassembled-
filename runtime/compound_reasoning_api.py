from runtime.algorithm_selector import select_best_reply
from runtime.birth_to_compound_bridge import save_birth_compound, retrieve_compound_links
from runtime.thought_topology import topology_trace

def _law_from_item(item):
    if isinstance(item, dict):
        return (
            item.get("compressed_law")
            or item.get("shape_answer")
            or item.get("final_point")
            or item.get("thesis")
            or ""
        )

    if isinstance(item, list):
        parts = []
        for x in item[:6]:
            if isinstance(x, dict):
                parts.append(
                    x.get("compressed_law")
                    or x.get("shape_answer")
                    or x.get("final_point")
                    or x.get("thesis")
                    or x.get("subject")
                    or ""
                )
            else:
                parts.append(str(x))
        return " -> ".join([p for p in parts if p])

    return str(item)

def _best_law_from_links(links):
    for link in links:
        item = link.get("item")
        law = _law_from_item(item)
        if law and len(law) > 10:
            return law
    return ""

def compound_reply(prompt):
    selected = select_best_reply(prompt)
    birth = selected.get("birth_packet", {})
    winner = selected.get("winner", {})
    base_reply = winner.get("reply", "")

    links = retrieve_compound_links(birth, limit=5)
    topology = topology_trace(birth, limit=5)

    saved = save_birth_compound(prompt, birth, base_reply)

    reply = base_reply

    law = _best_law_from_links(links)
    if law:
        reply += f"\n\nCarried thought-link: {law}"

    topo_law = topology.get("topology_law", "")
    family = topology.get("dominant_family", "")
    pull = topology.get("family_pull", {})

    if topo_law:
        if family:
            reply += f"\n\nTopology family: {family}"
            reply += f"\nTopology pull: {pull}"
            reply += f"\nTopology path: {topo_law}"
        else:
            reply += f"\n\nTopology path: {topo_law}"

    return {
        "reply": reply,
        "birth_packet": birth,
        "winner": winner,
        "retrieved_links": links,
        "topology": topology,
        "saved_link": saved,
    }

