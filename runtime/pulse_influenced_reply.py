from runtime.compound_reasoning_api import compound_reply

def reply_with_latest_pulse(user_text):
    out = compound_reply(user_text)
    return {
        "reply": out["reply"],
        "pulse_context": "",
        "packet": out,
    }

