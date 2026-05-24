"""Generate Style-Color-Size variant SKUs from a product template."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.inventory import _ensure_default_stock_balance, set_product_manufacturing_link
from app.models.enums import ItemLifecycleStatus
from app.models.product import Product
from app.models.product_variant import AttributeValue, ProductAttribute, ProductTemplate
from app.schemas.product_variant import MatrixGenerateRequest, MatrixGenerateResult, VariantBriefRead

_SLUG_RE = re.compile(r"[^A-Z0-9]+")


def _slug(part: str) -> str:
    return _SLUG_RE.sub("", part.upper().strip()) or "X"


def build_variant_sku(prefix: str, color_code: str, size_code: str) -> str:
    return f"{_slug(prefix)}-{_slug(color_code)}-{_slug(size_code)}"[:64]


def _variant_brief(product: Product) -> VariantBriefRead:
    return VariantBriefRead(
        id=product.id,
        sku=product.sku,
        name=product.name,
        color=product.color,
        size=product.size,
        color_value_id=product.color_value_id,
        size_value_id=product.size_value_id,
        stock=product.stock,
        lifecycle_status=product.lifecycle_status,
        price=product.price,
    )


async def _load_attribute_values(
    db: AsyncSession,
    *,
    color_ids: list[int],
    size_ids: list[int],
) -> tuple[list[AttributeValue], list[AttributeValue]]:
    all_ids = set(color_ids) | set(size_ids)
    result = await db.execute(
        select(AttributeValue)
        .join(ProductAttribute)
        .where(AttributeValue.id.in_(all_ids), AttributeValue.is_active.is_(True)),
    )
    values = {v.id: v for v in result.scalars().all()}
    colors = [values[i] for i in color_ids if i in values]
    sizes = [values[i] for i in size_ids if i in values]
    color_attr = await db.execute(
        select(ProductAttribute).where(ProductAttribute.code == "COLOR"),
    )
    size_attr = await db.execute(
        select(ProductAttribute).where(ProductAttribute.code == "SIZE"),
    )
    color_attr_row = color_attr.scalar_one_or_none()
    size_attr_row = size_attr.scalar_one_or_none()
    if color_attr_row:
        colors = [v for v in colors if v.attribute_id == color_attr_row.id]
    if size_attr_row:
        sizes = [v for v in sizes if v.attribute_id == size_attr_row.id]
    return colors, sizes


async def generate_variant_matrix(
    db: AsyncSession,
    template: ProductTemplate,
    payload: MatrixGenerateRequest,
    *,
    user_id: int | None = None,
) -> MatrixGenerateResult:
    colors, sizes = await _load_attribute_values(
        db,
        color_ids=payload.color_value_ids,
        size_ids=payload.size_value_ids,
    )
    if not colors or not sizes:
        return MatrixGenerateResult(
            created=[],
            skipped=[],
            errors=["Invalid or inactive color/size value IDs"],
        )

    created: list[VariantBriefRead] = []
    skipped: list[str] = []
    errors: list[str] = []

    for color in colors:
        for size in sizes:
            sku = build_variant_sku(template.sku_prefix, color.code, size.code)
            existing = await db.execute(select(Product).where(Product.sku == sku))
            if existing.scalar_one_or_none():
                if payload.skip_existing:
                    skipped.append(sku)
                    continue
                errors.append(f"SKU already exists: {sku}")
                continue

            name = f"{template.name} — {color.label} / {size.label}"
            product = Product(
                sku=sku,
                name=name,
                description=template.description,
                category_id=template.category_id,
                product_line=template.product_line,
                item_type=template.item_type,
                template_id=template.id,
                style_code=template.style_code,
                color_value_id=color.id,
                size_value_id=size.id,
                color=color.label,
                size=size.label,
                variant=f"{color.label}-{size.label}",
                primary_uom=template.primary_uom,
                price=template.default_price,
                cost_price=template.default_cost_price,
                image_url=template.image_url,
                lifecycle_status=payload.lifecycle_status,
                stock=payload.initial_stock,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            db.add(product)
            await db.flush()
            if payload.initial_stock > 0:
                await _ensure_default_stock_balance(
                    db,
                    product,
                    initial_qty=payload.initial_stock,
                )
            mfg_sku = (template.manufacturing_item_sku or "").strip()
            if mfg_sku:
                try:
                    await set_product_manufacturing_link(db, product.id, mfg_sku)
                except ValueError as exc:
                    errors.append(f"{sku}: {exc}")
            created.append(_variant_brief(product))

    return MatrixGenerateResult(created=created, skipped=skipped, errors=errors)
