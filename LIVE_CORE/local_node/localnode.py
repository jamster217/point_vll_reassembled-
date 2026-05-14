from __future__ import annotations

import sys

from local_node.controller import controller_cycle


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m local_node.localnode 'your prompt here'")
        raise SystemExit(1)

    user_text = " ".join(sys.argv[1:]).strip()
    reply, packet = controller_cycle(user_text)
    print(reply)


if __name__ == "__main__":
    main()

