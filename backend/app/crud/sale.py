from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import customer as customer_crud
from app.models.enums import ItemLifecycleStatus
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.schemas.sale import SaleCreate


async def search_pos_products(
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


async def create_sale(
    db: AsyncSession,
    payload: SaleCreate,
    *,
    created_by_id: int,
) -> Sale:
    # Aggregate duplicate product lines in one request.
    qty_by_product: dict[int, int] = defaultdict(int)
    for line in payload.items:
        qty_by_product[line.product_id] += line.quantity

    if payload.customer_id is not None:
        customer = await customer_crud.get_customer(db, payload.customer_id)
        if customer is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Customer not found")

    product_ids = list(qty_by_product.keys())
    result = await db.execute(
        select(Product)
        .where(Product.id.in_(product_ids))
        .with_for_update(),
    )
    products = {p.id: p for p in result.scalars().all()}

    if len(products) != len(product_ids):
        missing = set(product_ids) - set(products.keys())
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Product(s) not found: {sorted(missing)}",
        )

    for product_id, quantity in qty_by_product.items():
        product = products[product_id]
        if product.lifecycle_status != ItemLifecycleStatus.ACTIVE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.sku} is not available for sale",
            )
        if product.stock < quantity:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock for {product.sku}: "
                    f"requested {quantity}, available {product.stock}"
                ),
            )

    sale = Sale(customer_id=payload.customer_id, created_by_id=created_by_id)
    db.add(sale)
    await db.flush()

    for product_id, quantity in qty_by_product.items():
        product = products[product_id]
        price_at_sale = product.price
        db.add(
            SaleItem(
                sale_id=sale.id,
                product_id=product_id,
                quantity=quantity,
                price_at_sale=price_at_sale,
            ),
        )
        product.stock -= quantity

    await db.commit()

    loaded = await db.execute(
        select(Sale)
        .options(selectinload(Sale.items).selectinload(SaleItem.product))
        .where(Sale.id == sale.id),
    )
    return loaded.scalar_one()


async def list_sales(
    db: AsyncSession,
    *,
    customer_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[tuple[Sale, str | None, str | None, int, Decimal]], int]:
    stmt = (
        select(Sale)
        .options(
            selectinload(Sale.items),
            selectinload(Sale.customer),
            selectinload(Sale.created_by_user),
        )
        .order_by(Sale.created_at.desc())
    )
    count_stmt = select(func.count()).select_from(Sale)

    if customer_id is not None:
        stmt = stmt.where(Sale.customer_id == customer_id)
        count_stmt = count_stmt.where(Sale.customer_id == customer_id)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.offset(skip).limit(limit))
    sales = list(result.scalars().all())

    rows: list[tuple[Sale, str | None, str | None, int, Decimal]] = []
    for sale in sales:
        customer_name = sale.customer.name if sale.customer else None
        cashier_email = sale.created_by_user.email if sale.created_by_user else None
        item_count = len(sale.items)
        sale_total = sum(item.quantity * item.price_at_sale for item in sale.items)
        rows.append((sale, customer_name, cashier_email, item_count, sale_total))
    return rows, total


async def get_sale(db: AsyncSession, sale_id: int) -> Sale | None:
    result = await db.execute(
        select(Sale)
        .options(
            selectinload(Sale.items).selectinload(SaleItem.product),
            selectinload(Sale.customer),
            selectinload(Sale.created_by_user),
        )
        .where(Sale.id == sale_id),
    )
    return result.scalar_one_or_none()
