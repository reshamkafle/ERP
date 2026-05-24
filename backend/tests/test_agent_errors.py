from app.core.agent_errors import public_agent_error_message


def test_public_agent_error_message_none_when_no_error() -> None:
    assert public_agent_error_message(None) is None
    assert public_agent_error_message("") is None


def test_public_agent_error_message_generic_when_stored() -> None:
    msg = public_agent_error_message("psycopg2.OperationalError: connection refused")
    assert msg is not None
    assert "server logs" in msg
    assert "psycopg2" not in msg
