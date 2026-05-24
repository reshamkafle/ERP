import pytest

from app.services.permission_service import assert_can_delegate


def test_assert_can_delegate_allows_subset() -> None:
    assert_can_delegate({"a", "b", "c"}, {"a", "b"})


def test_assert_can_delegate_rejects_escalation() -> None:
    with pytest.raises(ValueError, match="Cannot grant"):
        assert_can_delegate({"a"}, {"a", "b"})
