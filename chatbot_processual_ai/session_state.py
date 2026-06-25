def create_session_state() -> dict:
    return {
        "conversation": [],
        "active_process": None,
        "last_intent": None,
    }
