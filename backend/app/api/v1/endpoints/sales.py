from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import sale as sale_crud
from app.dependencies.auth import require_roles
from app.models.sale import Sale
from app.models.user import User, UserRole
from app.schemas.sale import (
    PosProductListResponse,
    PosProductRead,
    SaleCreate,
    SaleItemRead,
    SaleListItem,
    SaleListResponse,
    SaleRead,
)

router = APIRouter(prefix="/sales")

PosRoles = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER)


def _sale_to_read(sale: Sale) -> SaleRead:
    items: list[SaleItemRead] = []
    subtotal = Decimal("0")
    for item in sale.items:
        line_total = item.price_at_sale * item.quantity
        subtotal += line_total
        items.append(
            SaleItemRead(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                product_sku=item.product.sku,
                quantity=item.quantity,
                price_at_sale=item.price_at_sale,
                line_total=line_total,
            ),
        )
    tax = Decimal("0")
    customer_name = sale.customer.name if sale.customer else None
    cashier_email = sale.created_by_user.email if sale.created_by_user else None
    return SaleRead(
        id=sale.id,
        customer_id=sale.customer_id,
        customer_name=customer_name,
        cashier_email=cashier_email,
        created_at=sale.created_at,
        items=items,
        subtotal=subtotal,
        tax=tax,
        total=subtotal + tax,
    )


@router.get("", response_model=SaleListResponse)
async def list_sales(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PosRoles)],
    customer_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> SaleListResponse:
    rows, total = await sale_crud.list_sales(
        db,
        customer_id=customer_id,
        skip=skip,
        limit=limit,
    )
    return SaleListResponse(
        items=[
            SaleListItem(
                id=sale.id,
                customer_id=sale.customer_id,
                customer_name=customer_name,
                cashier_email=cashier_email,
                created_at=sale.created_at,
                item_count=item_count,
                total=sale_total,
            )
            for sale, customer_name, cashier_email, item_count, sale_total in rows
        ],
        total=total,
    )


@router.get("/products", response_model=PosProductListResponse)
async def list_pos_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PosRoles)],
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
) -> PosProductListResponse:
    items, total = await sale_crud.search_pos_products(
        db,
        search=search,
        skip=skip,
        limit=limit,
    )
    return PosProductListResponse(
        items=[PosProductRead.model_validate(i) for i in items],
        total=total,
    )


@router.get("/{sale_id}", response_model=SaleRead)
async def get_sale(
    sale_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PosRoles)],
) -> SaleRead:
    sale = await sale_crud.get_sale(db, sale_id)
    if sale is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return _sale_to_read(sale)


@router.post("", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
async def checkout_sale(
    body: SaleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PosRoles)],
) -> SaleRead:
    sale = await sale_crud.create_sale(db, body, created_by_id=user.id)
    loaded = await sale_crud.get_sale(db, sale.id)
    if loaded is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sale not found after checkout")
    return _sale_to_read(loaded)
