"""Public-safe agent run error messages (no internal exception text)."""

_AGENT_FAILURE_PUBLIC = "Agent run failed. Check server logs for details."


def public_agent_error_message(stored: str | None) -> str | None:
    """Return a generic message when a run failed; never expose stored exception text."""
    if not stored:
        return None
    return _AGENT_FAILURE_PUBLIC
