#!/usr/bin/env python3
def apply_safe_future_pull(payload):
    payload = payload if isinstance(payload, dict) else {}
    prompt = str(payload.get("prompt") or payload.get("text") or payload.get("message") or "")
    low = prompt.lower()

    if any(x in low for x in ["future-pull", "future pull", "birthpoint", "accelerator trigger", "bridge mutation"]):
        final_shape = (
            "The future-pull birthpoint is stable when it remains a pure shape helper: "
            "it may sharpen final_shape, but it does not mutate the bridge, trigger the accelerator, "
            "or override the core route."
        )
        return {
            "final_shape": final_shape,
            "meta": {
                "future_pull_status": "anchored_v41_safe",
                "future_pull_source": "runtime.future_pull_anchor_safe_v41",
            },
        }

    return None

