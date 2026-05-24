from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import payment as payment_crud
from app.crud import purchase as purchase_crud
from app.schemas.payments import OpenBalanceRead
from app.dependencies.auth import require_permission
from app.models.user import User
from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseItemRead,
    PurchaseListItem,
    PurchaseListResponse,
    PurchaseProductListResponse,
    PurchaseProductRead,
    PurchaseRead,
)

router = APIRouter(prefix="/purchases")

PurchaseReadPerm = require_permission("warehouse.purchases.read")
PurchaseWritePerm = require_permission("warehouse.purchases.write")
PurchaseDeletePerm = require_permission("warehouse.purchases.delete")


def _agent_summary(meta: dict | None) -> str | None:
    if not meta:
        return None
    notes = meta.get("merge_notes")
    if isinstance(notes, str) and notes.strip():
        return notes[:500]
    return None


@router.get("/products", response_model=PurchaseProductListResponse)
async def list_purchase_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PurchaseReadPerm)],
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
) -> PurchaseProductListResponse:
    items, total = await purchase_crud.search_purchase_products(
        db,
        search=search,
        skip=skip,
        limit=limit,
    )
    return PurchaseProductListResponse(
        items=[PurchaseProductRead.model_validate(i) for i in items],
        total=total,
    )


@router.get("", response_model=PurchaseListResponse)
async def list_purchases(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PurchaseReadPerm)],
    supplier_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> PurchaseListResponse:
    rows, total = await purchase_crud.list_purchases(
        db,
        supplier_id=supplier_id,
        skip=skip,
        limit=limit,
    )
    return PurchaseListResponse(
        items=[
            PurchaseListItem(
                id=purchase.id,
                supplier_id=purchase.supplier_id or 0,
                supplier_name=supplier_name,
                created_at=purchase.created_at,
                item_count=item_count,
                total=total_cost,
                status=purchase.status.value,
                procurement_run_id=purchase.procurement_run_id,
                agent_summary=_agent_summary(purchase.agent_metadata),
            )
            for purchase, supplier_name, item_count, total_cost in rows
        ],
        total=total,
    )


@router.post("", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    body: PurchaseCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PurchaseWritePerm)],
) -> PurchaseRead:
    purchase = await purchase_crud.create_purchase(db, body, created_by_id=user.id)
    return _purchase_to_read(purchase)


@router.post("/{purchase_id}/confirm", response_model=PurchaseRead)
async def confirm_purchase(
    purchase_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PurchaseWritePerm)],
) -> PurchaseRead:
    purchase = await purchase_crud.confirm_draft_purchase(
        db,
        purchase_id,
        confirmed_by_id=user.id,
    )
    return _purchase_to_read(purchase)


@router.delete("/{purchase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def discard_draft_purchase(
    purchase_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PurchaseDeletePerm)],
) -> None:
    await purchase_crud.discard_draft_purchase(db, purchase_id)


@router.get("/{purchase_id}/open-balance", response_model=OpenBalanceRead)
async def get_purchase_open_balance(
    purchase_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PurchaseReadPerm)],
) -> OpenBalanceRead:
    purchase = await purchase_crud.get_purchase(db, purchase_id)
    if purchase is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Purchase not found")
    total = purchase.total or sum(item.quantity * item.unit_cost for item in purchase.items)
    paid = purchase.amount_paid or Decimal("0")
    return OpenBalanceRead(
        document_id=purchase.id,
        total=total,
        amount_paid=paid,
        open_balance=payment_crud.purchase_open_balance(purchase),
        payment_status=purchase.payment_status.value,
        currency_code=purchase.currency_code,
    )


@router.get("/{purchase_id}", response_model=PurchaseRead)
async def get_purchase(
    purchase_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PurchaseReadPerm)],
) -> PurchaseRead:
    purchase = await purchase_crud.get_purchase(db, purchase_id)
    if purchase is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Purchase not found")
    if purchase.supplier is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Purchase not found")
    return _purchase_to_read(purchase)


def _purchase_to_read(purchase) -> PurchaseRead:
    items: list[PurchaseItemRead] = []
    total = Decimal("0")
    for item in purchase.items:
        line_total = item.unit_cost * item.quantity
        total += line_total
        items.append(
            PurchaseItemRead(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                product_sku=item.product.sku,
                quantity=item.quantity,
                unit_cost=item.unit_cost,
                line_total=line_total,
            ),
        )
    return PurchaseRead(
        id=purchase.id,
        supplier_id=purchase.supplier_id or 0,
        supplier_name=purchase.supplier.name,
        created_at=purchase.created_at,
        status=purchase.status.value,
        procurement_run_id=purchase.procurement_run_id,
        agent_summary=_agent_summary(purchase.agent_metadata),
        items=items,
        total=total,
    )
