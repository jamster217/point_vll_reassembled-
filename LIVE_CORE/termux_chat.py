print("[TRACE] entering termux_chat.py", flush=True)
from runtime.run_analysis_profile import run_profile

print("Leveon Termux Chat")
print("Type /quit to exit.")
print("Type /controller to toggle controller detail.\n")

show_controller = False

while True:
    try:
        msg = input("you> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nbye")
        break

    if not msg:
        continue
    if msg.lower() in {"/quit", "quit", "exit"}:
        print("bye")
        break
    if msg.lower() == "/controller":
        show_controller = not show_controller
        print(f"controller detail> {'on' if show_controller else 'off'}")
        print()
        continue

    profile = run_profile("full", msg, {})
    selection = profile.get("selection_output", {}) or {}
    rationale = profile.get("winner_rationale", {}) or {}

    selected_text = (
        selection.get("selected_text")
        or profile.get("live", {}).get("final_english")
        or ""
    )
    selected_domain = selection.get("selected_domain") or profile.get("live", {}).get("domain", "")
    selected_memory = selection.get("selected_memory_profile")
    selected_policy = selection.get("selected_revision_policy")

    print("leveon>", selected_text)
    print("domain>", selected_domain)

    if selected_memory:
        print("memory>", selected_memory)
    if selected_policy:
        print("policy>", selected_policy)

    if show_controller:
        print("decision>", selection.get("decision_strength"))
        print("gap>", selection.get("score_gap"))
        print("winner>", rationale.get("summary", ""))
        print("selection_json>", selection)

    print()

