from runtime.pulse_influenced_reply import reply_with_latest_pulse

print("🌕 SOVEREIGN CO-CREATOR CONSOLE OPEN")
print("Type 'exit' to quit. Every reply pulls the live lattice pulse.\n")

while True:
    try:
        user_input = input("You> ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Closing sovereign channel...")
            break

        if not user_input:
            continue

        out = reply_with_latest_pulse(user_input)

        print("\nLeveon>")
        print(out["reply"])
        print("-" * 80)

    except KeyboardInterrupt:
        print("\nClosing sovereign channel...")
        break

    except Exception as e:
        print("Error:", e)

