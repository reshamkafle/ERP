from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import inventory as inventory_crud
from app.crud import supplier as supplier_crud
from app.dependencies.auth import require_permission
from app.models.enums import ItemLifecycleStatus, ItemType
from app.models.purchase import PurchaseItem
from app.models.sale import SaleItem
from app.crud import tax_rate as tax_rate_crud
from app.schemas.tax import TaxRateRead
from app.models.user import User
from app.crud import warehouse as warehouse_crud
from app.models.tax_rate import TaxRate
from app.schemas.inventory import (
    CategoryCreate,
    CategoryRead,
    InventoryAnalyticsRead,
    InventoryBomUsageListResponse,
    InventoryBomUsageRead,
    InventoryItemCreate,
    InventoryItemRead,
    InventoryItemUpdate,
    InventoryListResponse,
    InventoryTransactionListResponse,
)
from app.services.inventory_bom_usage import get_bom_usages_for_product

router = APIRouter(prefix="/inventory")

InventoryReadRoles = require_permission("warehouse.inventory.read")
InventoryWriteRoles = require_permission("warehouse.inventory.write")


async def _ensure_default_supplier(db: AsyncSession, supplier_id: int | None) -> None:
    if supplier_id is None:
        return
    sup = await supplier_crud.get_supplier(db, supplier_id)
    if sup is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Default supplier not found")


async def _ensure_tax_rate(db: AsyncSession, tax_rate_id: int | None) -> None:
    if tax_rate_id is None:
        return
    result = await db.execute(select(TaxRate).where(TaxRate.id == tax_rate_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Tax rate not found")


async def _ensure_warehouse_refs(
    db: AsyncSession,
    warehouse_id: int | None,
    location_id: int | None,
) -> None:
    if warehouse_id is not None:
        wh = await warehouse_crud.get_warehouse(db, warehouse_id)
        if wh is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Default warehouse not found")
    if location_id is not None:
        loc = await warehouse_crud.get_storage_location(db, location_id)
        if loc is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Default location not found")


@router.get("", response_model=InventoryListResponse)
async def list_items(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryReadRoles)],
    search: str | None = None,
    category_id: int | None = None,
    item_type: ItemType | None = None,
    lifecycle_status: ItemLifecycleStatus | None = None,
    template_id: int | None = None,
    style_code: str | None = None,
    color: str | None = None,
    size: str | None = None,
    variants_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    include_sales_insight: bool = False,
) -> InventoryListResponse:
    items, total = await inventory_crud.list_inventory_items(
        db,
        search=search,
        category_id=category_id,
        item_type=item_type.value if item_type else None,
        lifecycle_status=lifecycle_status.value if lifecycle_status else None,
        template_id=template_id,
        style_code=style_code,
        color=color,
        size=size,
        variants_only=variants_only or None,
        skip=skip,
        limit=limit,
    )
    reads = await inventory_crud.products_to_inventory_reads(
        db,
        items,
        include_sales_insight=include_sales_insight,
    )
    return InventoryListResponse(items=reads, total=total)


@router.get("/tax-rates", response_model=list[TaxRateRead])
async def list_tax_rates_for_inventory(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryReadRoles)],
    limit: int = Query(200, ge=1, le=200),
) -> list[TaxRateRead]:
    items, _ = await tax_rate_crud.list_tax_rates(db, is_active=True, skip=0, limit=limit)
    return [TaxRateRead.model_validate(i) for i in items]


@router.get("/categories", response_model=list[CategoryRead])
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryReadRoles)],
) -> list[CategoryRead]:
    categories = await inventory_crud.list_categories(db)
    return [CategoryRead.model_validate(c) for c in categories]


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    body: CategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("warehouse.inventory.delete"))],
) -> CategoryRead:
    category = await inventory_crud.create_category(db, body.name)
    return CategoryRead.model_validate(category)


@router.get("/{item_id}", response_model=InventoryItemRead)
async def get_item(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryReadRoles)],
) -> InventoryItemRead:
    item = await inventory_crud.get_inventory_item(db, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return await inventory_crud.product_to_inventory_read(
        db, item, include_analytics=True,
    )


@router.get("/{item_id}/transactions", response_model=InventoryTransactionListResponse)
async def list_item_transactions(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryReadRoles)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> InventoryTransactionListResponse:
    item = await inventory_crud.get_inventory_item(db, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    txns, total = await inventory_crud.list_product_transactions(
        db, item_id, skip=skip, limit=limit,
    )
    return InventoryTransactionListResponse(
        items=[inventory_crud.transaction_to_read(t) for t in txns],
        total=total,
    )


@router.get("/{item_id}/analytics", response_model=InventoryAnalyticsRead)
async def get_item_analytics(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryReadRoles)],
) -> InventoryAnalyticsRead:
    item = await inventory_crud.get_inventory_item(db, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    from app.services.inventory_analytics import compute_product_analytics

    return await compute_product_analytics(db, item)


@router.get("/{item_id}/bom-usages", response_model=InventoryBomUsageListResponse)
async def list_item_bom_usages(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryReadRoles)],
) -> InventoryBomUsageListResponse:
    item = await inventory_crud.get_inventory_item(db, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    rows = await get_bom_usages_for_product(db, item)
    return InventoryBomUsageListResponse(
        usages=[
            InventoryBomUsageRead(
                parent_sku=r.parent_sku,
                parent_name=r.parent_name,
                parent_category=r.parent_category,
                required_qty=r.required_qty,
                on_hand_stock=r.on_hand_stock,
                is_short=r.is_short,
            )
            for r in rows
        ],
    )


@router.post("", response_model=InventoryItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: InventoryItemCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(InventoryWriteRoles)],
) -> InventoryItemRead:
    if body.category_id is not None:
        category = await inventory_crud.get_category(db, body.category_id)
        if category is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Category not found")
    await _ensure_default_supplier(db, body.default_supplier_id)
    await _ensure_tax_rate(db, body.tax_rate_id)
    await _ensure_warehouse_refs(db, body.default_warehouse_id, body.default_location_id)
    for ps in body.product_suppliers:
        await _ensure_default_supplier(db, ps.supplier_id)
    existing = await inventory_crud.get_by_sku(db, body.sku)
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="SKU already exists")
    try:
        item = await inventory_crud.create_inventory_item(db, body, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return await inventory_crud.product_to_inventory_read(db, item)


@router.patch("/{item_id}", response_model=InventoryItemRead)
async def update_item(
    item_id: int,
    body: InventoryItemUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(InventoryWriteRoles)],
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
    if body.tax_rate_id is not None:
        await _ensure_tax_rate(db, body.tax_rate_id)
    if body.default_warehouse_id is not None or body.default_location_id is not None:
        await _ensure_warehouse_refs(
            db,
            body.default_warehouse_id if body.default_warehouse_id is not None else item.default_warehouse_id,
            body.default_location_id if body.default_location_id is not None else item.default_location_id,
        )
    if body.product_suppliers is not None:
        for ps in body.product_suppliers:
            await _ensure_default_supplier(db, ps.supplier_id)
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
    try:
        updated = await inventory_crud.update_inventory_item(
            db, item, body, user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return await inventory_crud.product_to_inventory_read(db, updated)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("warehouse.inventory.delete"))],
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
