"""Tests for Style-Color-Size variant matrix."""

import pytest
from sqlalchemy import select

from app.crud import product_variant as variant_crud
from app.models.product import Product
from app.models.enums import ItemType
from app.schemas.product_variant import MatrixGenerateRequest, ProductTemplateCreate
from app.services.inventory_variant_matrix import build_variant_sku


def test_build_variant_sku_pattern():
    assert build_variant_sku("shirt", "red", "m") == "SHIRT-RED-M"


@pytest.mark.asyncio
async def test_list_attributes_seeded(seeded_db):
    attrs = await variant_crud.list_attributes(seeded_db)
    codes = {a.code for a in attrs}
    assert "COLOR" in codes
    assert "SIZE" in codes
    color = next(a for a in attrs if a.code == "COLOR")
    assert len(color.values) >= 4


@pytest.mark.asyncio
async def test_generate_variant_matrix(seeded_db):
    template = await variant_crud.create_template(
        seeded_db,
        ProductTemplateCreate(
            style_code="QA-STYLE-01",
            name="QA Test Shirt",
            sku_prefix="QASHIRT",
            item_type=ItemType.FINISHED,
        ),
    )
    await seeded_db.flush()

    attrs = await variant_crud.list_attributes(seeded_db)
    color_ids = [v.id for a in attrs if a.code == "COLOR" for v in a.values[:2]]
    size_ids = [v.id for a in attrs if a.code == "SIZE" for v in a.values[:2]]

    result = await variant_crud.run_matrix_generate(
        seeded_db,
        template.id,
        MatrixGenerateRequest(color_value_ids=color_ids, size_value_ids=size_ids),
    )
    assert result is not None
    assert len(result.created) == 4
    assert result.skipped == []

    skus = {v.sku for v in result.created}
    assert len(skus) == 4

    products = await seeded_db.execute(
        select(Product).where(Product.template_id == template.id),
    )
    rows = list(products.scalars().all())
    assert len(rows) == 4
    for row in rows:
        assert row.style_code == "QA-STYLE-01"
        assert row.color_value_id is not None
        assert row.size_value_id is not None

    # Second run skips existing
    result2 = await variant_crud.run_matrix_generate(
        seeded_db,
        template.id,
        MatrixGenerateRequest(color_value_ids=color_ids, size_value_ids=size_ids),
    )
    assert result2 is not None
    assert len(result2.created) == 0
    assert len(result2.skipped) == 4
