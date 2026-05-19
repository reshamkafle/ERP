from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import inventory as inventory_crud
from app.crud import supplier as supplier_crud
from app.dependencies.auth import require_roles
from app.models.enums import ItemLifecycleStatus, ItemType
from app.models.purchase import PurchaseItem
from app.models.sale import SaleItem
from app.models.user import User, UserRole
from app.schemas.inventory import (
    CategoryCreate,
    CategoryRead,
    InventoryItemCreate,
    InventoryItemRead,
    InventoryItemUpdate,
    InventoryListResponse,
)

router = APIRouter(prefix="/inventory")

InventoryRoles = require_roles(UserRole.ADMIN, UserRole.MANAGER)


async def _ensure_default_supplier(db: AsyncSession, supplier_id: int | None) -> None:
    if supplier_id is None:
        return
    sup = await supplier_crud.get_supplier(db, supplier_id)
    if sup is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Default supplier not found")


@router.get("", response_model=InventoryListResponse)
async def list_items(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryRoles)],
    search: str | None = None,
    category_id: int | None = None,
    item_type: ItemType | None = None,
    lifecycle_status: ItemLifecycleStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> InventoryListResponse:
    items, total = await inventory_crud.list_inventory_items(
        db,
        search=search,
        category_id=category_id,
        item_type=item_type.value if item_type else None,
        lifecycle_status=lifecycle_status.value if lifecycle_status else None,
        skip=skip,
        limit=limit,
    )
    return InventoryListResponse(
        items=[InventoryItemRead.model_validate(i) for i in items],
        total=total,
    )


@router.get("/categories", response_model=list[CategoryRead])
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryRoles)],
) -> list[CategoryRead]:
    categories = await inventory_crud.list_categories(db)
    return [CategoryRead.model_validate(c) for c in categories]


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    body: CategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> CategoryRead:
    category = await inventory_crud.create_category(db, body.name)
    return CategoryRead.model_validate(category)


@router.get("/{item_id}", response_model=InventoryItemRead)
async def get_item(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryRoles)],
) -> InventoryItemRead:
    item = await inventory_crud.get_inventory_item(db, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return InventoryItemRead.model_validate(item)


@router.post("", response_model=InventoryItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: InventoryItemCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryRoles)],
) -> InventoryItemRead:
    if body.category_id is not None:
        category = await inventory_crud.get_category(db, body.category_id)
        if category is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Category not found")
    await _ensure_default_supplier(db, body.default_supplier_id)
    existing = await inventory_crud.get_by_sku(db, body.sku)
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="SKU already exists")
    item = await inventory_crud.create_inventory_item(db, body)
    return InventoryItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=InventoryItemRead)
async def update_item(
    item_id: int,
    body: InventoryItemUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryRoles)],
) -> InventoryItemRead:
    item = await inventory_crud.get_inventory_item(db, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    if body.category_id is not None:
        category = await inventory_crud.get_category(db, body.category_id)
        if category is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Category not found")
    if body.default_supplier_id is not None:
        await _ensure_default_supplier(db, body.default_supplier_id)
    if body.sku is not None:
        existing = await inventory_crud.get_by_sku(db, body.sku, exclude_id=item_id)
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="SKU already exists")
    # Cross-field UOM validation when both fields provided in patch
    secondary = body.secondary_uom if body.secondary_uom is not None else item.secondary_uom
    conversion = (
        body.conversion_factor if body.conversion_factor is not None else item.conversion_factor
    )
    if secondary and (conversion is None or conversion <= 0):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="conversion_factor is required when secondary_uom is set",
        )
    if conversion is not None and conversion > 0 and not secondary:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="secondary_uom is required when conversion_factor is set",
        )
    updated = await inventory_crud.update_inventory_item(db, item, body)
    return InventoryItemRead.model_validate(updated)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> None:
    item = await inventory_crud.get_inventory_item(db, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    sale_count = (
        await db.execute(
            select(func.count()).select_from(SaleItem).where(SaleItem.product_id == item_id),
        )
    ).scalar_one()
    purchase_count = (
        await db.execute(
            select(func.count())
            .select_from(PurchaseItem)
            .where(PurchaseItem.product_id == item_id),
        )
    ).scalar_one()
    if sale_count or purchase_count:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Cannot delete item with sales or purchase history",
        )
    await inventory_crud.delete_inventory_item(db, item)
