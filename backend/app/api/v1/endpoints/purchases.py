from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import purchase as purchase_crud
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
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

PurchaseRoles = require_roles(UserRole.ADMIN, UserRole.MANAGER)


@router.get("/products", response_model=PurchaseProductListResponse)
async def list_purchase_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PurchaseRoles)],
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
    _: Annotated[User, Depends(PurchaseRoles)],
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
            )
            for purchase, supplier_name, item_count, total_cost in rows
        ],
        total=total,
    )


@router.get("/{purchase_id}", response_model=PurchaseRead)
async def get_purchase(
    purchase_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PurchaseRoles)],
) -> PurchaseRead:
    purchase = await purchase_crud.get_purchase(db, purchase_id)
    if purchase is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Purchase not found")
    if purchase.supplier is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Purchase not found")
    return _purchase_to_read(purchase)


@router.post("", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    body: PurchaseCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PurchaseRoles)],
) -> PurchaseRead:
    purchase = await purchase_crud.create_purchase(db, body, created_by_id=user.id)
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
        items=items,
        total=total,
    )
