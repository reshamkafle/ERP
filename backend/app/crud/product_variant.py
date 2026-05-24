from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.product_variant import AttributeValue, ProductAttribute, ProductTemplate
from app.schemas.product_variant import (
    AttributeValueCreate,
    AttributeValueRead,
    MatrixGenerateRequest,
    MatrixGenerateResult,
    ProductAttributeCreate,
    ProductAttributeRead,
    ProductTemplateCreate,
    ProductTemplateRead,
    ProductTemplateUpdate,
    TemplateVariantsResponse,
    VariantBriefRead,
)
from app.services.inventory_variant_matrix import generate_variant_matrix


def _template_read(
    template: ProductTemplate,
    *,
    variant_count: int = 0,
    total_stock: int = 0,
) -> ProductTemplateRead:
    base = ProductTemplateRead.model_validate(template)
    return base.model_copy(update={"variant_count": variant_count, "total_stock": total_stock})


async def _template_stats(db: AsyncSession, template_id: int) -> tuple[int, int]:
    result = await db.execute(
        select(func.count(Product.id), func.coalesce(func.sum(Product.stock), 0)).where(
            Product.template_id == template_id,
        ),
    )
    row = result.one()
    return int(row[0]), int(row[1])


async def list_templates(
    db: AsyncSession,
    *,
    search: str | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[ProductTemplateRead], int]:
    stmt = select(ProductTemplate).options(selectinload(ProductTemplate.category))
    count_stmt = select(func.count()).select_from(ProductTemplate)
    if search:
        pattern = f"%{search.strip()}%"
        filt = (ProductTemplate.style_code.ilike(pattern)) | (ProductTemplate.name.ilike(pattern))
        stmt = stmt.where(filt)
        count_stmt = count_stmt.where(filt)
    if is_active is not None:
        stmt = stmt.where(ProductTemplate.is_active.is_(is_active))
        count_stmt = count_stmt.where(ProductTemplate.is_active.is_(is_active))
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(ProductTemplate.style_code).offset(skip).limit(limit),
    )
    templates = list(result.scalars().all())
    reads: list[ProductTemplateRead] = []
    for t in templates:
        vc, ts = await _template_stats(db, t.id)
        reads.append(_template_read(t, variant_count=vc, total_stock=ts))
    return reads, total


async def get_template(db: AsyncSession, template_id: int) -> ProductTemplate | None:
    result = await db.execute(
        select(ProductTemplate)
        .options(selectinload(ProductTemplate.category))
        .where(ProductTemplate.id == template_id),
    )
    return result.scalar_one_or_none()


async def get_template_read(db: AsyncSession, template_id: int) -> ProductTemplateRead | None:
    template = await get_template(db, template_id)
    if template is None:
        return None
    vc, ts = await _template_stats(db, template_id)
    return _template_read(template, variant_count=vc, total_stock=ts)


async def get_template_by_style_code(db: AsyncSession, style_code: str) -> ProductTemplate | None:
    result = await db.execute(
        select(ProductTemplate).where(ProductTemplate.style_code == style_code),
    )
    return result.scalar_one_or_none()


async def create_template(db: AsyncSession, payload: ProductTemplateCreate) -> ProductTemplate:
    template = ProductTemplate(**payload.model_dump())
    db.add(template)
    await db.flush()
    return template


async def update_template(
    db: AsyncSession,
    template: ProductTemplate,
    payload: ProductTemplateUpdate,
) -> ProductTemplate:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(template, key, value)
    await db.flush()
    if "style_code" in data:
        await db.execute(
            Product.__table__.update()
            .where(Product.template_id == template.id)
            .values(style_code=template.style_code),
        )
    return template


async def delete_template(db: AsyncSession, template: ProductTemplate) -> None:
    await db.delete(template)


async def list_template_variants(
    db: AsyncSession,
    template_id: int,
) -> TemplateVariantsResponse | None:
    template = await get_template(db, template_id)
    if template is None:
        return None
    vc, ts = await _template_stats(db, template_id)
    result = await db.execute(
        select(Product)
        .where(Product.template_id == template_id)
        .order_by(Product.color, Product.size, Product.sku),
    )
    variants = [
        VariantBriefRead(
            id=p.id,
            sku=p.sku,
            name=p.name,
            color=p.color,
            size=p.size,
            color_value_id=p.color_value_id,
            size_value_id=p.size_value_id,
            stock=p.stock,
            lifecycle_status=p.lifecycle_status,
            price=p.price,
        )
        for p in result.scalars().all()
    ]
    return TemplateVariantsResponse(
        template=_template_read(template, variant_count=vc, total_stock=ts),
        variants=variants,
    )


async def run_matrix_generate(
    db: AsyncSession,
    template_id: int,
    payload: MatrixGenerateRequest,
    *,
    user_id: int | None = None,
) -> MatrixGenerateResult | None:
    template = await get_template(db, template_id)
    if template is None:
        return None
    return await generate_variant_matrix(db, template, payload, user_id=user_id)


async def list_attributes(db: AsyncSession, *, active_only: bool = True) -> list[ProductAttributeRead]:
    stmt = select(ProductAttribute).options(selectinload(ProductAttribute.values))
    if active_only:
        stmt = stmt.where(ProductAttribute.is_active.is_(True))
    result = await db.execute(stmt.order_by(ProductAttribute.sort_order, ProductAttribute.code))
    attrs = result.scalars().all()
    reads: list[ProductAttributeRead] = []
    for attr in attrs:
        values = [v for v in attr.values if v.is_active] if active_only else list(attr.values)
        value_reads = [
            AttributeValueRead.model_validate(v)
            for v in sorted(values, key=lambda x: (x.sort_order, x.label))
        ]
        reads.append(
            ProductAttributeRead(
                id=attr.id,
                code=attr.code,
                name=attr.name,
                sort_order=attr.sort_order,
                is_active=attr.is_active,
                values=value_reads,
            ),
        )
    return reads


async def create_attribute(db: AsyncSession, payload: ProductAttributeCreate) -> ProductAttribute:
    attr = ProductAttribute(**payload.model_dump())
    db.add(attr)
    await db.flush()
    return attr


async def add_attribute_value(
    db: AsyncSession,
    attribute_id: int,
    payload: AttributeValueCreate,
) -> AttributeValue | None:
    result = await db.execute(select(ProductAttribute).where(ProductAttribute.id == attribute_id))
    if result.scalar_one_or_none() is None:
        return None
    value = AttributeValue(attribute_id=attribute_id, **payload.model_dump())
    db.add(value)
    await db.flush()
    return value
