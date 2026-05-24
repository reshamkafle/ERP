from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.product_variant import ProductAttribute
from app.crud import inventory as inventory_crud
from app.crud import product_variant as variant_crud
from app.dependencies.auth import require_permission
from app.models.user import User
from app.schemas.product_variant import (
    AttributeValueCreate,
    MatrixGenerateRequest,
    MatrixGenerateResult,
    ProductAttributeCreate,
    ProductAttributeRead,
    ProductTemplateCreate,
    ProductTemplateListResponse,
    ProductTemplateRead,
    ProductTemplateUpdate,
    TemplateVariantsResponse,
)

router = APIRouter(prefix="/inventory")

InventoryReadRoles = require_permission("warehouse.inventory.read")
InventoryWriteRoles = require_permission("warehouse.inventory.write")


@router.get("/attributes", response_model=list[ProductAttributeRead])
async def list_product_attributes(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryReadRoles)],
    active_only: bool = True,
) -> list[ProductAttributeRead]:
    return await variant_crud.list_attributes(db, active_only=active_only)


@router.post("/attributes", response_model=ProductAttributeRead, status_code=status.HTTP_201_CREATED)
async def create_product_attribute(
    body: ProductAttributeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryWriteRoles)],
) -> ProductAttributeRead:
    code = body.code.upper()
    existing = await db.execute(select(ProductAttribute).where(ProductAttribute.code == code))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Attribute code already exists")
    attr = await variant_crud.create_attribute(
        db,
        ProductAttributeCreate(**{**body.model_dump(), "code": code}),
    )
    await db.commit()
    attrs = await variant_crud.list_attributes(db, active_only=False)
    for a in attrs:
        if a.id == attr.id:
            return a
    return ProductAttributeRead(
        id=attr.id,
        code=attr.code,
        name=attr.name,
        sort_order=attr.sort_order,
        is_active=attr.is_active,
        values=[],
    )


@router.post(
    "/attributes/{attribute_id}/values",
    status_code=status.HTTP_201_CREATED,
)
async def create_attribute_value(
    attribute_id: int,
    body: AttributeValueCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryWriteRoles)],
) -> dict:
    value = await variant_crud.add_attribute_value(
        db,
        attribute_id,
        AttributeValueCreate(**{**body.model_dump(), "code": body.code.upper()}),
    )
    if value is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Attribute not found")
    await db.commit()
    return {"id": value.id, "code": value.code, "label": value.label}


@router.get("/templates", response_model=ProductTemplateListResponse)
async def list_product_templates(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryReadRoles)],
    search: str | None = None,
    is_active: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> ProductTemplateListResponse:
    items, total = await variant_crud.list_templates(
        db,
        search=search,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )
    return ProductTemplateListResponse(items=items, total=total)


@router.post("/templates", response_model=ProductTemplateRead, status_code=status.HTTP_201_CREATED)
async def create_product_template(
    body: ProductTemplateCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryWriteRoles)],
) -> ProductTemplateRead:
    if await variant_crud.get_template_by_style_code(db, body.style_code):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Style code already exists")
    template = await variant_crud.create_template(db, body)
    await db.commit()
    read = await variant_crud.get_template_read(db, template.id)
    assert read is not None
    return read


@router.get("/templates/{template_id}", response_model=ProductTemplateRead)
async def get_product_template(
    template_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryReadRoles)],
) -> ProductTemplateRead:
    read = await variant_crud.get_template_read(db, template_id)
    if read is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Template not found")
    return read


@router.patch("/templates/{template_id}", response_model=ProductTemplateRead)
async def update_product_template(
    template_id: int,
    body: ProductTemplateUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryWriteRoles)],
) -> ProductTemplateRead:
    template = await variant_crud.get_template(db, template_id)
    if template is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Template not found")
    if body.style_code and body.style_code != template.style_code:
        if await variant_crud.get_template_by_style_code(db, body.style_code):
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Style code already exists")
    if body.category_id is not None:
        category = await inventory_crud.get_category(db, body.category_id)
        if category is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Category not found")
    await variant_crud.update_template(db, template, body)
    await db.commit()
    read = await variant_crud.get_template_read(db, template_id)
    assert read is not None
    return read


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_template(
    template_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryWriteRoles)],
) -> None:
    template = await variant_crud.get_template(db, template_id)
    if template is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Template not found")
    await variant_crud.delete_template(db, template)
    await db.commit()


@router.get("/templates/{template_id}/variants", response_model=TemplateVariantsResponse)
async def list_template_variants(
    template_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(InventoryReadRoles)],
) -> TemplateVariantsResponse:
    response = await variant_crud.list_template_variants(db, template_id)
    if response is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Template not found")
    return response


@router.post(
    "/templates/{template_id}/generate-matrix",
    response_model=MatrixGenerateResult,
)
async def generate_template_matrix(
    template_id: int,
    body: MatrixGenerateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(InventoryWriteRoles)],
) -> MatrixGenerateResult:
    result = await variant_crud.run_matrix_generate(
        db,
        template_id,
        body,
        user_id=current_user.id,
    )
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Template not found")
    await db.commit()
    return result
