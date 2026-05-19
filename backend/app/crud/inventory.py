from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.product import Product
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate


async def list_inventory_items(
    db: AsyncSession,
    *,
    search: str | None = None,
    category_id: int | None = None,
    item_type: str | None = None,
    lifecycle_status: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Product], int]:
    stmt = select(Product).options(
        selectinload(Product.category),
        selectinload(Product.default_supplier),
    )
    count_stmt = select(func.count()).select_from(Product)

    if search:
        pattern = f"%{search.strip()}%"
        filter_expr = or_(
            Product.sku.ilike(pattern),
            Product.name.ilike(pattern),
            Product.barcode.ilike(pattern),
            Product.alternate_codes.ilike(pattern),
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

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(Product.name).offset(skip).limit(limit),
    )
    return list(result.scalars().all()), total


async def get_inventory_item(db: AsyncSession, item_id: int) -> Product | None:
    result = await db.execute(
        select(Product)
        .options(
            selectinload(Product.category),
            selectinload(Product.default_supplier),
        )
        .where(Product.id == item_id),
    )
    return result.scalar_one_or_none()


async def get_by_sku(db: AsyncSession, sku: str, *, exclude_id: int | None = None) -> Product | None:
    stmt = select(Product).where(Product.sku == sku)
    if exclude_id is not None:
        stmt = stmt.where(Product.id != exclude_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_inventory_item(db: AsyncSession, payload: InventoryItemCreate) -> Product:
    data = payload.model_dump(exclude={"initial_stock"})
    item = Product(**data, stock=payload.initial_stock)
    db.add(item)
    await db.commit()
    loaded = await get_inventory_item(db, item.id)
    assert loaded is not None
    return loaded


async def update_inventory_item(
    db: AsyncSession,
    item: Product,
    payload: InventoryItemUpdate,
) -> Product:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    loaded = await get_inventory_item(db, item.id)
    assert loaded is not None
    return loaded


async def delete_inventory_item(db: AsyncSession, item: Product) -> None:
    await db.delete(item)
    await db.commit()


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
