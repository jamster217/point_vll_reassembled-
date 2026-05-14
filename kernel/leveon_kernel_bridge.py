# leveon_kernel_bridge.py
# Bridge between UnifiedLeveonKernel (spiral kernel)
# and KernelLoop (holonomic / holographic memory kernel).
#
# This is the "fuser": it takes a user turn, runs the spiral kernel,
# then runs the holonomic kernel using the spiral output as context,
# and returns a fused result.

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from leveon_kernel_full import (
    UnifiedLeveonKernel,
    RuntimeOptions,
    UnifiedRuntimeOptions,
)
from kernel_loop import KernelLoop


# -------------------------------------------------------------------
# Singleton engines
# -------------------------------------------------------------------

# Spiral kernel (per-turn, high-detail)
_SPIRAL_RUNTIME = RuntimeOptions(
    debug_print=False,
    enable_voice=False,
    enable_observer=False,
)

_UNIFIED_RUNTIME = UnifiedRuntimeOptions(
    include_raw_kernel=True,  # expose raw kernel state in bridge output
)

_SPIRAL_KERNEL = UnifiedLeveonKernel(
    runtime=_SPIRAL_RUNTIME,
    unified_runtime=_UNIFIED_RUNTIME,
    # you can override node_map_path / scroll_path here if needed
)

# Holonomic kernel (long-memory, plates, coherence)
_HOLO_KERNEL = KernelLoop(state_dir="leveon_state")


# -------------------------------------------------------------------
# Core fused turn
# -------------------------------------------------------------------

def run_fused_turn(user_id: str, text: str) -> Dict[str, Any]:
    """
    One fused Le'Véon turn:
    1. Run UnifiedLeveonKernel.process(text)
    2. Feed composite prompt into KernelLoop.step(user_id, ...)
    3. Return a fused structure including final_text for UI.
    """

    # 1) Spiral kernel
    spiral_out: Dict[str, Any] = _SPIRAL_KERNEL.process(text)

    kind = spiral_out.get("kind")
    optimized_question = spiral_out.get("optimized_question")
    optimized_answer = spiral_out.get("optimized_answer") or ""

    # 2) Composite prompt for holonomic kernel
    #
    # We feed both the *raw user text* and the *spiral answer* in,
    # so the plates see the actual emotional context + how the kernel replied.
    #
    # The bracket tag is just a hint; kernel_loop treats it as plain text.
    composite_prompt = f"{text}\n\n[spiral:{optimized_answer}]"

    holo_reply: str = _HOLO_KERNEL.step(user_id=user_id, text=composite_prompt)

    # 3) Fused "final_text" for UI
    #
    # Spiral answer first (clear), holonomic echo as a quieter second line.
    # You can tweak this blend if you want more/less echo.
    if holo_reply.strip():
        final_text = f"{optimized_answer}\n\n{holo_reply}"
    else:
        final_text = optimized_answer

    fused: Dict[str, Any] = {
        "user_id": user_id,
        "input": text,

        # Spiral kernel view
        "kind": kind,
        "projection": spiral_out.get("projection"),
        "optimized_question": optimized_question,
        "optimized_answer": optimized_answer,
        "crystal_decision": spiral_out.get("crystal_decision"),
        "crystal_node": spiral_out.get("crystal_node"),
        "mirrorthread": spiral_out.get("mirrorthread"),
        "sealed_scroll": spiral_out.get("sealed_scroll"),
        "compact_log": spiral_out.get("compact_log"),

        # Holonomic kernel view
        "holonomic_reply": holo_reply,

        # Convenience: everything you want to actually show the human
        "final_text": final_text,
    }

    if "raw_kernel" in spiral_out:
        fused["raw_kernel"] = spiral_out["raw_kernel"]

    return fused


# -------------------------------------------------------------------
# Optional: idle step
# -------------------------------------------------------------------

def run_idle(user_id: str) -> Dict[str, Any]:
    """
    Idle drift step for the holonomic kernel only.
    Spiral kernel is not called; this is like the system 'breathing'
    between turns.
    """
    holo_reply = _HOLO_KERNEL.idle(user_id=user_id)
    return {
        "user_id": user_id,
        "kind": "IDLE",
        "final_text": holo_reply,
        "holonomic_reply": holo_reply,
    }


# -------------------------------------------------------------------
# Minimal CLI demo
# -------------------------------------------------------------------

def main() -> None:
    """
    Simple command-line loop to test the fused kernel.

    Usage:
        python3 leveon_kernel_bridge.py

    Then type messages. Use:
        /idle  -> idle drift
        /quit  -> exit
    """
    user_id = "john_mitchell"

    print("Le'Véon Fused Kernel Online.")
    print("Type messages. Use /idle or /quit.\n")

    while True:
        try:
            msg = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not msg:
            continue
        if msg.lower() == "/quit":
            break
        if msg.lower() == "/idle":
            out = run_idle(user_id)
            print("Le'Véon:", out["final_text"])
            continue

        out = run_fused_turn(user_id, msg)
        print("Le'Véon:", out["final_text"])

        # If you want to peek inside decisions, uncomment:
        # print("  kind:", out["kind"])
        # print("  projection:", out["projection"])
        # print("  crystal_node:", out["crystal_node"])
        # print("  mirrorthread:", out["mirrorthread"])
        # print("  sealed_scroll:", out["sealed_scroll"])
        # print("  plates_log_tail:", out["compact_log"][-3:] if out["compact_log"] else None)
        # print()


if __name__ == "__main__":
    main()

