from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.inventory_transaction import InventoryTransaction
from app.models.manufacturing import ManufacturingItem
from app.models.product import Product
from app.models.product_supplier import ProductSupplier
from app.models.stock_balance import StockBalance
from app.models.user import User
from app.models.warehouse import StorageLocation, Warehouse
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemRead,
    InventoryItemUpdate,
    InventorySalesDailyPoint,
    InventorySalesInsight,
    InventoryTransactionRead,
    ProductSupplierInput,
    ProductSupplierRead,
    StockBalanceRead,
)
from app.services.inventory_analytics import compute_product_analytics
from app.services.inventory_bom_usage import batch_bom_usage_summaries
from app.services.inventory_sales_insights import (
    LOOKBACK_DAYS,
    batch_inventory_sales_insights,
)


async def get_manufacturing_item_sku_map(
    db: AsyncSession,
    product_ids: list[int],
) -> dict[int, str]:
    if not product_ids:
        return {}
    result = await db.execute(
        select(ManufacturingItem.product_id, ManufacturingItem.sku).where(
            ManufacturingItem.product_id.in_(product_ids),
        ),
    )
    return {int(row[0]): row[1] for row in result.all() if row[0] is not None}


async def set_product_manufacturing_link(
    db: AsyncSession,
    product_id: int,
    manufacturing_item_sku: str | None,
) -> None:
    await db.execute(
        update(ManufacturingItem)
        .where(ManufacturingItem.product_id == product_id)
        .values(product_id=None),
    )
    sku = (manufacturing_item_sku or "").strip()
    if not sku:
        return
    result = await db.execute(
        select(ManufacturingItem).where(ManufacturingItem.sku == sku),
    )
    mfg = result.scalar_one_or_none()
    if mfg is None:
        raise ValueError(f"Manufacturing item not found: {manufacturing_item_sku}")
    if mfg.product_id is not None and mfg.product_id != product_id:
        await db.execute(
            update(ManufacturingItem)
            .where(ManufacturingItem.id == mfg.id)
            .values(product_id=None),
        )
    mfg.product_id = product_id


async def _upsert_product_suppliers(
    db: AsyncSession,
    product_id: int,
    suppliers: list[ProductSupplierInput] | None,
) -> None:
    if suppliers is None:
        return
    await db.execute(
        ProductSupplier.__table__.delete().where(ProductSupplier.product_id == product_id),
    )
    for row in suppliers:
        db.add(
            ProductSupplier(
                product_id=product_id,
                supplier_id=row.supplier_id,
                vendor_code=row.vendor_code,
                is_preferred=row.is_preferred,
            ),
        )


def _product_load_options():
    return (
        selectinload(Product.template),
        selectinload(Product.category),
        selectinload(Product.default_supplier),
        selectinload(Product.tax_rate),
        selectinload(Product.default_warehouse),
        selectinload(Product.default_location),
        selectinload(Product.created_by),
        selectinload(Product.updated_by),
        selectinload(Product.product_suppliers).selectinload(ProductSupplier.supplier),
        selectinload(Product.stock_balances).selectinload(StockBalance.warehouse),
        selectinload(Product.stock_balances).selectinload(StockBalance.location),
    )


def _stock_balance_reads(product: Product) -> list[StockBalanceRead]:
    reads: list[StockBalanceRead] = []
    for bal in product.stock_balances or []:
        reads.append(
            StockBalanceRead(
                id=bal.id,
                warehouse_id=bal.warehouse_id,
                warehouse_code=bal.warehouse.code if bal.warehouse else None,
                warehouse_name=bal.warehouse.name if bal.warehouse else None,
                location_id=bal.location_id,
                location_code=bal.location.code if bal.location else None,
                on_hand=bal.on_hand,
                available=bal.available,
                reserved=bal.reserved,
                in_transit=bal.in_transit,
                quality_status=bal.quality_status,
                valuation_method=bal.valuation_method,
                last_transaction_at=bal.last_transaction_at,
                expiry_date=bal.expiry_date.isoformat() if bal.expiry_date else None,
                lot_number=bal.lot_number,
            ),
        )
    return reads


def _supplier_links_read(product: Product) -> list[ProductSupplierRead]:
    links: list[ProductSupplierRead] = []
    for ps in product.product_suppliers or []:
        links.append(
            ProductSupplierRead(
                id=ps.id,
                supplier_id=ps.supplier_id,
                vendor_code=ps.vendor_code,
                is_preferred=ps.is_preferred,
                supplier_name=ps.supplier.name if ps.supplier else None,
            ),
        )
    return links


async def product_to_inventory_read(
    db: AsyncSession,
    product: Product,
    *,
    mfg_sku: str | None = None,
    bom_parent_count: int | None = None,
    has_bom_shortage: bool | None = None,
    include_sales_insight: bool = False,
    include_analytics: bool = False,
) -> InventoryItemRead:
    if mfg_sku is None:
        sku_map = await get_manufacturing_item_sku_map(db, [product.id])
        mfg_sku = sku_map.get(product.id)
    if bom_parent_count is None or has_bom_shortage is None:
        summaries = await batch_bom_usage_summaries(db, [product])
        summary = summaries.get(product.id)
        if summary:
            bom_parent_count = summary.bom_parent_count
            has_bom_shortage = summary.has_bom_shortage
        else:
            bom_parent_count = 0
            has_bom_shortage = False

    base = InventoryItemRead.model_validate(product)
    sales_insight = None
    if include_sales_insight:
        sales_map = await batch_inventory_sales_insights(db, [product.id])
        raw = sales_map.get(product.id)
        if raw is not None:
            sales_insight = _sales_insight_schema(raw)
        else:
            sales_insight = InventorySalesInsight(lookback_days=LOOKBACK_DAYS)

    analytics = None
    if include_analytics:
        analytics = await compute_product_analytics(db, product)

    return base.model_copy(
        update={
            "manufacturing_item_sku": mfg_sku,
            "bom_parent_count": bom_parent_count,
            "has_bom_shortage": has_bom_shortage,
            "product_supplier_links": _supplier_links_read(product),
            "stock_balances": _stock_balance_reads(product),
            "sales_insight": sales_insight,
            "analytics": analytics,
        },
    )


def _sales_insight_schema(insight) -> InventorySalesInsight:
    return InventorySalesInsight(
        lookback_days=LOOKBACK_DAYS,
        quantity_sold=insight.quantity_sold,
        revenue=insight.revenue,
        top_buyer_name=insight.top_buyer_name,
        top_seller_name=insight.top_seller_name,
        daily_chart=[
            InventorySalesDailyPoint(
                date=p.date,
                quantity_sold=p.quantity_sold,
                revenue=p.revenue,
            )
            for p in insight.daily_chart
        ],
    )


async def products_to_inventory_reads(
    db: AsyncSession,
    products: list[Product],
    *,
    include_sales_insight: bool = False,
) -> list[InventoryItemRead]:
    if not products:
        return []
    ids = [p.id for p in products]
    sku_map = await get_manufacturing_item_sku_map(db, ids)
    summaries = await batch_bom_usage_summaries(db, products)
    sales_map = (
        await batch_inventory_sales_insights(db, ids) if include_sales_insight else {}
    )
    reads: list[InventoryItemRead] = []
    for product in products:
        summary = summaries.get(product.id)
        base = InventoryItemRead.model_validate(product)
        sales_insight = None
        if include_sales_insight:
            raw = sales_map.get(product.id)
            if raw is not None:
                sales_insight = _sales_insight_schema(raw)
            else:
                sales_insight = InventorySalesInsight(lookback_days=LOOKBACK_DAYS)
        reads.append(
            base.model_copy(
                update={
                    "manufacturing_item_sku": sku_map.get(product.id),
                    "bom_parent_count": summary.bom_parent_count if summary else 0,
                    "has_bom_shortage": summary.has_bom_shortage if summary else False,
                    "product_supplier_links": _supplier_links_read(product),
                    "stock_balances": _stock_balance_reads(product),
                    "sales_insight": sales_insight,
                },
            ),
        )
    return reads


async def list_inventory_items(
    db: AsyncSession,
    *,
    search: str | None = None,
    category_id: int | None = None,
    item_type: str | None = None,
    lifecycle_status: str | None = None,
    template_id: int | None = None,
    style_code: str | None = None,
    color: str | None = None,
    size: str | None = None,
    variants_only: bool | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Product], int]:
    stmt = select(Product).options(*_product_load_options())
    count_stmt = select(func.count()).select_from(Product)

    if search:
        pattern = f"%{search.strip()}%"
        filter_expr = or_(
            Product.sku.ilike(pattern),
            Product.name.ilike(pattern),
            Product.barcode.ilike(pattern),
            Product.alternate_codes.ilike(pattern),
            Product.style_code.ilike(pattern),
            Product.color.ilike(pattern),
            Product.size.ilike(pattern),
            Product.variant.ilike(pattern),
        )
        stmt = stmt.where(filter_expr)
        count_stmt = count_stmt.where(filter_expr)
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
        count_stmt = count_stmt.where(Product.category_id == category_id)
    if item_type is not None:
        stmt = stmt.where(Product.item_type == item_type)
        count_stmt = count_stmt.where(Product.item_type == item_type)
    if lifecycle_status is not None:
        stmt = stmt.where(Product.lifecycle_status == lifecycle_status)
        count_stmt = count_stmt.where(Product.lifecycle_status == lifecycle_status)
    if template_id is not None:
        stmt = stmt.where(Product.template_id == template_id)
        count_stmt = count_stmt.where(Product.template_id == template_id)
    if style_code:
        sc = style_code.strip()
        stmt = stmt.where(Product.style_code.ilike(f"%{sc}%"))
        count_stmt = count_stmt.where(Product.style_code.ilike(f"%{sc}%"))
    if color:
        c = color.strip()
        stmt = stmt.where(Product.color.ilike(f"%{c}%"))
        count_stmt = count_stmt.where(Product.color.ilike(f"%{c}%"))
    if size:
        s = size.strip()
        stmt = stmt.where(Product.size.ilike(f"%{s}%"))
        count_stmt = count_stmt.where(Product.size.ilike(f"%{s}%"))
    if variants_only:
        stmt = stmt.where(Product.template_id.isnot(None))
        count_stmt = count_stmt.where(Product.template_id.isnot(None))

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(Product.name).offset(skip).limit(limit),
    )
    return list(result.scalars().all()), total


async def get_inventory_item(db: AsyncSession, item_id: int) -> Product | None:
    result = await db.execute(
        select(Product).options(*_product_load_options()).where(Product.id == item_id),
    )
    return result.scalar_one_or_none()


async def get_by_sku(db: AsyncSession, sku: str, *, exclude_id: int | None = None) -> Product | None:
    stmt = select(Product).where(Product.sku == sku)
    if exclude_id is not None:
        stmt = stmt.where(Product.id != exclude_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _ensure_default_stock_balance(
    db: AsyncSession,
    product: Product,
    *,
    initial_qty: int,
) -> None:
    wh_result = await db.execute(
        select(Warehouse).where(Warehouse.is_default.is_(True)).limit(1),
    )
    warehouse = wh_result.scalar_one_or_none()
    if warehouse is None:
        wh_result = await db.execute(select(Warehouse).limit(1))
        warehouse = wh_result.scalar_one_or_none()
    if warehouse is None or initial_qty <= 0:
        return
    bal = StockBalance(
        product_id=product.id,
        warehouse_id=warehouse.id,
        location_id=None,
        on_hand=initial_qty,
        available=initial_qty,
    )
    db.add(bal)


async def create_inventory_item(
    db: AsyncSession,
    payload: InventoryItemCreate,
    *,
    user_id: int | None = None,
) -> Product:
    data = payload.model_dump(
        exclude={"initial_stock", "manufacturing_item_sku", "product_suppliers"},
    )
    item = Product(**data, stock=payload.initial_stock, created_by_id=user_id, updated_by_id=user_id)
    db.add(item)
    await db.flush()
    await _upsert_product_suppliers(db, item.id, payload.product_suppliers)
    if payload.manufacturing_item_sku:
        await set_product_manufacturing_link(db, item.id, payload.manufacturing_item_sku)
    if payload.initial_stock > 0:
        await _ensure_default_stock_balance(db, item, initial_qty=payload.initial_stock)
    await db.commit()
    loaded = await get_inventory_item(db, item.id)
    assert loaded is not None
    return loaded


async def update_inventory_item(
    db: AsyncSession,
    item: Product,
    payload: InventoryItemUpdate,
    *,
    user_id: int | None = None,
) -> Product:
    data = payload.model_dump(exclude_unset=True)
    mfg_sku = data.pop("manufacturing_item_sku", None)
    suppliers = data.pop("product_suppliers", None)
    has_mfg_update = "manufacturing_item_sku" in payload.model_fields_set
    for key, value in data.items():
        setattr(item, key, value)
    if user_id is not None:
        item.updated_by_id = user_id
    if suppliers is not None or "product_suppliers" in payload.model_fields_set:
        await _upsert_product_suppliers(db, item.id, suppliers or [])
    if has_mfg_update:
        await set_product_manufacturing_link(db, item.id, mfg_sku)
    await db.commit()
    loaded = await get_inventory_item(db, item.id)
    assert loaded is not None
    return loaded


async def delete_inventory_item(db: AsyncSession, item: Product) -> None:
    await db.delete(item)
    await db.commit()


async def list_product_transactions(
    db: AsyncSession,
    product_id: int,
    *,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[InventoryTransaction], int]:
    count_stmt = (
        select(func.count())
        .select_from(InventoryTransaction)
        .where(InventoryTransaction.product_id == product_id)
    )
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        select(InventoryTransaction)
        .options(selectinload(InventoryTransaction.user))
        .where(InventoryTransaction.product_id == product_id)
        .order_by(InventoryTransaction.transaction_at.desc())
        .offset(skip)
        .limit(limit),
    )
    return list(result.scalars().all()), total


def transaction_to_read(txn: InventoryTransaction) -> InventoryTransactionRead:
    return InventoryTransactionRead(
        id=txn.id,
        transaction_type=txn.transaction_type,
        transaction_at=txn.transaction_at,
        reference_document=txn.reference_document,
        from_warehouse_id=txn.from_warehouse_id,
        from_location_id=txn.from_location_id,
        to_warehouse_id=txn.to_warehouse_id,
        to_location_id=txn.to_location_id,
        quantity=txn.quantity,
        lot_number=txn.lot_number,
        serial_number=txn.serial_number,
        unit_cost=txn.unit_cost,
        reason_code=txn.reason_code,
        user_id=txn.user_id,
        user_email=txn.user.email if txn.user else None,
        remarks=txn.remarks,
    )


async def list_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category).order_by(Category.name))
    return list(result.scalars().all())


async def create_category(db: AsyncSession, name: str) -> Category:
    category = Category(name=name.strip())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def get_category(db: AsyncSession, category_id: int) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()
