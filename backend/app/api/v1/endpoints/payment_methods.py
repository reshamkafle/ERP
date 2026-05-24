from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import payment as payment_crud
from app.dependencies.auth import require_permission
from app.models.user import User
from app.schemas.payments import PaymentMethodListResponse, PaymentMethodRead

router = APIRouter(prefix="/payment-methods")

PaymentRead = require_permission("finance.payments.read", "finance.records.read")


@router.get("", response_model=PaymentMethodListResponse)
async def list_payment_methods(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PaymentRead)],
) -> PaymentMethodListResponse:
    items = await payment_crud.list_payment_methods(db)
    return PaymentMethodListResponse(
        items=[PaymentMethodRead.model_validate(i) for i in items],
    )
