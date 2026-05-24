from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import supplier as supplier_crud
from app.dependencies.auth import require_permission
from app.models.user import User
from app.schemas.supplier import (
    SupplierCreate,
    SupplierDetailRead,
    SupplierListItem,
    SupplierListResponse,
    SupplierPurchaseSummary,
    SupplierRead,
    SupplierUpdate,
)

router = APIRouter(prefix="/suppliers")

SupplierReadRoles = require_permission("warehouse.suppliers.read")
SupplierManageRoles = require_permission("warehouse.suppliers.write")


def _supplier_read(supplier) -> SupplierRead:
    return SupplierRead.model_validate(supplier)


@router.get("", response_model=SupplierListResponse)
async def list_suppliers(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(SupplierManageRoles)],
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> SupplierListResponse:
    rows, total = await supplier_crud.list_suppliers(
        db,
        search=search,
        skip=skip,
        limit=limit,
    )
    return SupplierListResponse(
        items=[
            SupplierListItem(
                **_supplier_read(supplier).model_dump(),
                total_spent=total_spent,
                purchase_count=purchase_count,
            )
            for supplier, total_spent, purchase_count in rows
        ],
        total=total,
    )


@router.get("/{supplier_id}", response_model=SupplierDetailRead)
async def get_supplier(
    supplier_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(SupplierManageRoles)],
) -> SupplierDetailRead:
    supplier, total_spent, purchase_count, purchases = (
        await supplier_crud.get_supplier_with_recent_purchases(db, supplier_id)
    )
    if supplier is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return SupplierDetailRead(
        **_supplier_read(supplier).model_dump(),
        total_spent=total_spent,
        purchase_count=purchase_count,
        recent_purchases=[
            SupplierPurchaseSummary(
                id=purchase.id,
                created_at=purchase.created_at,
                item_count=item_count,
                total=total,
            )
            for purchase, item_count, total in purchases
        ],
    )


@router.post("", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    body: SupplierCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(SupplierManageRoles)],
) -> SupplierRead:
    try:
        supplier = await supplier_crud.create_supplier(db, body)
    except ValueError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _supplier_read(supplier)


@router.patch("/{supplier_id}", response_model=SupplierRead)
async def update_supplier(
    supplier_id: int,
    body: SupplierUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(SupplierManageRoles)],
) -> SupplierRead:
    supplier = await supplier_crud.get_supplier(db, supplier_id)
    if supplier is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    try:
        updated = await supplier_crud.update_supplier(db, supplier, body)
    except ValueError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _supplier_read(updated)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("warehouse.suppliers.delete"))],
) -> None:
    supplier = await supplier_crud.get_supplier(db, supplier_id)
    if supplier is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    purchase_count = await supplier_crud.count_supplier_purchases(db, supplier_id)
    if purchase_count:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Cannot delete supplier with purchase history",
        )
    await supplier_crud.delete_supplier(db, supplier)
