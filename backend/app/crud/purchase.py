from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import supplier as supplier_crud
from app.models.enums import DocumentPaymentStatus, ItemLifecycleStatus, PurchaseStatus
from app.models.product import Product
from app.models.purchase import Purchase, PurchaseItem  # noqa: F401 — PurchaseItem used in select
from app.schemas.purchase import PurchaseCreate
from app.services.tax_calculation import get_company_settings


def _purchase_total(items: list) -> Decimal:
    return sum(item.quantity * item.unit_cost for item in items)


async def search_purchase_products(
    db: AsyncSession,
    *,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Product], int]:
    stmt = select(Product).where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE)
    count_stmt = (
        select(func.count())
        .select_from(Product)
        .where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE)
    )

    if search:
        pattern = f"%{search.strip()}%"
        filter_expr = or_(
            Product.sku.ilike(pattern),
            Product.name.ilike(pattern),
            Product.barcode.ilike(pattern),
        )
        stmt = stmt.where(filter_expr)
        count_stmt = count_stmt.where(filter_expr)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.order_by(Product.name).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def list_purchases(
    db: AsyncSession,
    *,
    supplier_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[tuple[Purchase, str, int, Decimal]], int]:
    stmt = (
        select(Purchase)
        .options(selectinload(Purchase.items), selectinload(Purchase.supplier))
        .order_by(Purchase.created_at.desc())
    )
    count_stmt = select(func.count()).select_from(Purchase)

    if supplier_id is not None:
        stmt = stmt.where(Purchase.supplier_id == supplier_id)
        count_stmt = count_stmt.where(Purchase.supplier_id == supplier_id)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.offset(skip).limit(limit))
    purchases = list(result.scalars().all())

    rows: list[tuple[Purchase, str, int, Decimal]] = []
    for purchase in purchases:
        supplier_name = purchase.supplier.name if purchase.supplier else "—"
        item_count = len(purchase.items)
        total_cost = sum(item.quantity * item.unit_cost for item in purchase.items)
        rows.append((purchase, supplier_name, item_count, total_cost))
    return rows, total


async def get_purchase(db: AsyncSession, purchase_id: int) -> Purchase | None:
    result = await db.execute(
        select(Purchase)
        .options(
            selectinload(Purchase.items).selectinload(PurchaseItem.product),
            selectinload(Purchase.supplier),
        )
        .where(Purchase.id == purchase_id),
    )
    return result.scalar_one_or_none()


async def create_purchase(
    db: AsyncSession,
    payload: PurchaseCreate,
    *,
    created_by_id: int,
    purchase_status: PurchaseStatus = PurchaseStatus.RECEIVED,
    procurement_run_id: int | None = None,
    agent_metadata: dict | None = None,
    commit: bool = True,
) -> Purchase:
    supplier = await supplier_crud.get_supplier(db, payload.supplier_id)
    if supplier is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Supplier not found")

    # Aggregate duplicate product lines; unit_cost always comes from product master data.
    line_by_product: dict[int, int] = {}
    for line in payload.items:
        line_by_product[line.product_id] = line_by_product.get(line.product_id, 0) + line.quantity

    product_ids = list(line_by_product)
    result = await db.execute(
        select(Product).where(Product.id.in_(product_ids)).with_for_update(),
    )
    products = {p.id: p for p in result.scalars().all()}

    if len(products) != len(product_ids):
        missing = set(product_ids) - set(products.keys())
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Product(s) not found: {sorted(missing)}",
        )

    for product_id, quantity in line_by_product.items():
        product = products[product_id]
        if product.lifecycle_status != ItemLifecycleStatus.ACTIVE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.sku} is not available for purchasing",
            )
        if quantity < 1:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid quantity for {product.sku}",
            )

    settings = await get_company_settings(db)
    purchase = Purchase(
        supplier_id=payload.supplier_id,
        created_by_id=created_by_id,
        status=purchase_status,
        procurement_run_id=procurement_run_id,
        agent_metadata=agent_metadata,
        currency_code=settings.default_currency,
        payment_status=DocumentPaymentStatus.UNPAID,
    )
    db.add(purchase)
    await db.flush()

    for product_id, quantity in line_by_product.items():
        product = products[product_id]
        unit_cost = product.cost_price
        db.add(
            PurchaseItem(
                purchase_id=purchase.id,
                product_id=product_id,
                quantity=quantity,
                unit_cost=unit_cost,
            ),
        )
        if purchase_status == PurchaseStatus.RECEIVED:
            from app.models.enums import InventoryTransactionType
            from app.services.inventory_posting import adjust_product_stock

            product.cost_price = unit_cost
            await adjust_product_stock(
                db,
                product,
                quantity,
                transaction_type=InventoryTransactionType.RECEIPT,
                reference_document=f"PURCHASE-{purchase.id}",
                user_id=created_by_id,
            )

    loaded_items = (
        await db.execute(
            select(PurchaseItem).where(PurchaseItem.purchase_id == purchase.id),
        )
    ).scalars().all()
    purchase.total = _purchase_total(list(loaded_items))

    if commit:
        await db.commit()
    else:
        await db.flush()

    loaded = await db.execute(
        select(Purchase)
        .options(
            selectinload(Purchase.items).selectinload(PurchaseItem.product),
            selectinload(Purchase.supplier),
        )
        .where(Purchase.id == purchase.id),
    )
    return loaded.scalar_one()


async def confirm_draft_purchase(
    db: AsyncSession,
    purchase_id: int,
    *,
    confirmed_by_id: int,
) -> Purchase:
    purchase_result = await db.execute(
        select(Purchase)
        .options(selectinload(Purchase.items))
        .where(Purchase.id == purchase_id)
        .with_for_update(),
    )
    purchase = purchase_result.scalar_one_or_none()
    if purchase is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Purchase not found")
    if purchase.status != PurchaseStatus.DRAFT:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Only draft purchases can be confirmed",
        )
    if purchase.supplier_id is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Draft purchase has no supplier",
        )

    product_ids = [item.product_id for item in purchase.items]
    if not product_ids:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Purchase has no lines")

    pr_result = await db.execute(
        select(Product).where(Product.id.in_(product_ids)).with_for_update(),
    )
    products = {p.id: p for p in pr_result.scalars().all()}
    if len(products) != len(set(product_ids)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Product missing for purchase line")

    for item in purchase.items:
        product = products[item.product_id]
        if product.lifecycle_status != ItemLifecycleStatus.ACTIVE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.sku} is not available for receiving",
            )
        from app.models.enums import InventoryTransactionType
        from app.services.inventory_posting import adjust_product_stock

        product.cost_price = item.unit_cost
        await adjust_product_stock(
            db,
            product,
            item.quantity,
            transaction_type=InventoryTransactionType.RECEIPT,
            reference_document=f"PURCHASE-{purchase.id}",
            user_id=confirmed_by_id,
        )

    purchase.status = PurchaseStatus.RECEIVED
    purchase.created_by_id = confirmed_by_id
    purchase.total = _purchase_total(purchase.items)
    purchase.payment_status = DocumentPaymentStatus.UNPAID
    await db.commit()

    loaded = await db.execute(
        select(Purchase)
        .options(
            selectinload(Purchase.items).selectinload(PurchaseItem.product),
            selectinload(Purchase.supplier),
        )
        .where(Purchase.id == purchase.id),
    )
    return loaded.scalar_one()


async def discard_draft_purchase(db: AsyncSession, purchase_id: int) -> None:
    purchase_result = await db.execute(
        select(Purchase).where(Purchase.id == purchase_id).with_for_update(),
    )
    purchase = purchase_result.scalar_one_or_none()
    if purchase is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Purchase not found")
    if purchase.status != PurchaseStatus.DRAFT:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Only draft purchases can be discarded",
        )
    await db.delete(purchase)
    await db.commit()
