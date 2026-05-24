from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.customer_audit_log import CustomerAuditLog


def _serialize(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "value"):
        return value.value
    if hasattr(value, "__float__"):
        return str(value)
    return value


async def log_customer_changes(
    db: AsyncSession,
    customer: Customer,
    old_data: dict[str, Any],
    new_data: dict[str, Any],
    *,
    user_id: int | None = None,
) -> None:
    skip = {"updated_at", "created_at"}
    for key in set(old_data) | set(new_data):
        if key in skip:
            continue
        old_val = _serialize(old_data.get(key))
        new_val = _serialize(new_data.get(key))
        if old_val == new_val:
            continue
        db.add(
            CustomerAuditLog(
                customer_id=customer.id,
                user_id=user_id,
                field_name=key,
                old_value={"value": old_val} if old_val is not None else None,
                new_value={"value": new_val} if new_val is not None else None,
                change_summary=f"{key}: {old_val!r} → {new_val!r}",
            ),
        )
