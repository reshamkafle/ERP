from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.purchase import Purchase, PurchaseItem
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _purchase_total_expr():
    return func.coalesce(func.sum(PurchaseItem.quantity * PurchaseItem.unit_cost), 0)


async def list_suppliers(
    db: AsyncSession,
    *,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[tuple[Supplier, Decimal, int]], int]:
    total_spent_subq = (
        select(
            Purchase.supplier_id.label("supplier_id"),
            _purchase_total_expr().label("total_spent"),
            func.count(func.distinct(Purchase.id)).label("purchase_count"),
        )
        .join(PurchaseItem, PurchaseItem.purchase_id == Purchase.id)
        .where(Purchase.supplier_id.is_not(None))
        .group_by(Purchase.supplier_id)
        .subquery()
    )

    stmt = (
        select(
            Supplier,
            func.coalesce(total_spent_subq.c.total_spent, 0).label("total_spent"),
            func.coalesce(total_spent_subq.c.purchase_count, 0).label("purchase_count"),
        )
        .outerjoin(total_spent_subq, Supplier.id == total_spent_subq.c.supplier_id)
    )
    count_stmt = select(func.count()).select_from(Supplier)

    if search:
        pattern = f"%{search.strip()}%"
        filter_expr = or_(
            Supplier.name.ilike(pattern),
            Supplier.phone.ilike(pattern),
            Supplier.email.ilike(pattern),
        )
        stmt = stmt.where(filter_expr)
        count_stmt = count_stmt.where(filter_expr)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.order_by(Supplier.name).offset(skip).limit(limit))
    rows = [(row[0], row[1], int(row[2])) for row in result.all()]
    return rows, total


async def get_supplier(db: AsyncSession, supplier_id: int) -> Supplier | None:
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    return result.scalar_one_or_none()


async def get_supplier_totals(
    db: AsyncSession,
    supplier_id: int,
) -> tuple[Decimal, int]:
    result = await db.execute(
        select(
            _purchase_total_expr(),
            func.count(func.distinct(Purchase.id)),
        )
        .join(PurchaseItem, PurchaseItem.purchase_id == Purchase.id)
        .where(Purchase.supplier_id == supplier_id),
    )
    row = result.one()
    return Decimal(str(row[0] or 0)), int(row[1] or 0)


async def get_supplier_with_recent_purchases(
    db: AsyncSession,
    supplier_id: int,
    *,
    purchases_limit: int = 10,
) -> tuple[Supplier | None, Decimal, int, list[tuple[Purchase, int, Decimal]]]:
    supplier = await get_supplier(db, supplier_id)
    if supplier is None:
        return None, Decimal("0"), 0, []

    total_spent, purchase_count = await get_supplier_totals(db, supplier_id)

    purchases_result = await db.execute(
        select(Purchase)
        .options(selectinload(Purchase.items))
        .where(Purchase.supplier_id == supplier_id)
        .order_by(Purchase.created_at.desc())
        .limit(purchases_limit),
    )
    purchases = list(purchases_result.scalars().all())
    summaries: list[tuple[Purchase, int, Decimal]] = []
    for purchase in purchases:
        item_count = len(purchase.items)
        total = sum(item.quantity * item.unit_cost for item in purchase.items)
        summaries.append((purchase, item_count, total))
    return supplier, total_spent, purchase_count, summaries


async def create_supplier(db: AsyncSession, payload: SupplierCreate) -> Supplier:
    supplier = Supplier(
        name=payload.name.strip(),
        phone=_normalize_optional(payload.phone),
        email=_normalize_optional(str(payload.email) if payload.email else None),
        notes=_normalize_optional(payload.notes),
    )
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return supplier


async def update_supplier(
    db: AsyncSession,
    supplier: Supplier,
    payload: SupplierUpdate,
) -> Supplier:
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        data["name"] = data["name"].strip()
    if "phone" in data:
        data["phone"] = _normalize_optional(data["phone"])
    if "email" in data:
        email = data["email"]
        data["email"] = _normalize_optional(str(email) if email else None)
    if "notes" in data:
        data["notes"] = _normalize_optional(data["notes"])
    for key, value in data.items():
        setattr(supplier, key, value)
    await db.commit()
    await db.refresh(supplier)
    return supplier


async def delete_supplier(db: AsyncSession, supplier: Supplier) -> None:
    await db.delete(supplier)
    await db.commit()


async def count_supplier_purchases(db: AsyncSession, supplier_id: int) -> int:
    result = await db.execute(
        select(func.count()).select_from(Purchase).where(Purchase.supplier_id == supplier_id),
    )
    return result.scalar_one()
