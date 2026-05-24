from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.journey import JOURNEY_BY_TYPE, JOURNEY_STEPS
from app.models.erp_document import ErpDocument
from app.models.enums import ErpDocumentType
from app.schemas.erp_document import ErpDocumentCreate, ErpDocumentRead, ErpDocumentUpdate


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def document_to_read(doc: ErpDocument) -> ErpDocumentRead:
    meta = JOURNEY_BY_TYPE[doc.document_type]
    return ErpDocumentRead(
        id=doc.id,
        document_number=doc.document_number,
        document_type=doc.document_type,
        type_label=meta.label,
        journey_step=doc.journey_step,
        phase=doc.phase,
        status=doc.status,
        title=doc.title,
        reference_number=doc.reference_number,
        notes=doc.notes,
        content=doc.content or {},
        supplier_id=doc.supplier_id,
        customer_id=doc.customer_id,
        purchase_id=doc.purchase_id,
        sale_id=doc.sale_id,
        related_document_id=doc.related_document_id,
        created_by_id=doc.created_by_id,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


async def _next_document_number(db: AsyncSession, document_type: ErpDocumentType) -> str:
    prefix = JOURNEY_BY_TYPE[document_type].number_prefix
    result = await db.execute(
        select(func.count())
        .select_from(ErpDocument)
        .where(ErpDocument.document_type == document_type),
    )
    count = result.scalar_one()
    return f"{prefix}-{count + 1:06d}"


async def list_erp_documents(
    db: AsyncSession,
    *,
    search: str | None = None,
    document_type: ErpDocumentType | None = None,
    phase: str | None = None,
    customer_id: int | None = None,
    sale_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[ErpDocument], int]:
    stmt = select(ErpDocument)
    count_stmt = select(func.count()).select_from(ErpDocument)

    if customer_id is not None:
        stmt = stmt.where(ErpDocument.customer_id == customer_id)
        count_stmt = count_stmt.where(ErpDocument.customer_id == customer_id)
    if sale_id is not None:
        stmt = stmt.where(ErpDocument.sale_id == sale_id)
        count_stmt = count_stmt.where(ErpDocument.sale_id == sale_id)
    if document_type is not None:
        stmt = stmt.where(ErpDocument.document_type == document_type)
        count_stmt = count_stmt.where(ErpDocument.document_type == document_type)
    if phase:
        stmt = stmt.where(ErpDocument.phase == phase)
        count_stmt = count_stmt.where(ErpDocument.phase == phase)
    if search:
        pattern = f"%{search.strip()}%"
        filter_expr = or_(
            ErpDocument.title.ilike(pattern),
            ErpDocument.document_number.ilike(pattern),
            ErpDocument.reference_number.ilike(pattern),
            ErpDocument.notes.ilike(pattern),
        )
        stmt = stmt.where(filter_expr)
        count_stmt = count_stmt.where(filter_expr)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(ErpDocument.journey_step, ErpDocument.created_at.desc())
        .offset(skip)
        .limit(limit),
    )
    return list(result.scalars().all()), total


async def get_erp_document(db: AsyncSession, document_id: int) -> ErpDocument | None:
    result = await db.execute(select(ErpDocument).where(ErpDocument.id == document_id))
    return result.scalar_one_or_none()


async def create_erp_document(
    db: AsyncSession,
    payload: ErpDocumentCreate,
    *,
    created_by_id: int | None = None,
) -> ErpDocument:
    meta = JOURNEY_BY_TYPE[payload.document_type]
    document_number = await _next_document_number(db, payload.document_type)
    content: dict[str, Any] = payload.content if payload.content is not None else {}
    doc = ErpDocument(
        document_number=document_number,
        document_type=payload.document_type,
        journey_step=meta.journey_step,
        phase=meta.phase,
        status=payload.status,
        title=payload.title.strip(),
        reference_number=_normalize_optional(payload.reference_number),
        notes=_normalize_optional(payload.notes),
        content=content,
        supplier_id=payload.supplier_id,
        customer_id=payload.customer_id,
        purchase_id=payload.purchase_id,
        sale_id=payload.sale_id,
        related_document_id=payload.related_document_id,
        created_by_id=created_by_id,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def update_erp_document(
    db: AsyncSession,
    doc: ErpDocument,
    payload: ErpDocumentUpdate,
) -> ErpDocument:
    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"] is not None:
        data["title"] = data["title"].strip()
    if "reference_number" in data:
        data["reference_number"] = _normalize_optional(data["reference_number"])
    if "notes" in data:
        data["notes"] = _normalize_optional(data["notes"])
    for key, value in data.items():
        setattr(doc, key, value)
    await db.commit()
    await db.refresh(doc)
    return doc


async def delete_erp_document(db: AsyncSession, doc: ErpDocument) -> None:
    await db.delete(doc)
    await db.commit()


async def list_all_for_journey_view(db: AsyncSession) -> list[ErpDocument]:
    result = await db.execute(
        select(ErpDocument).order_by(ErpDocument.journey_step, ErpDocument.created_at.desc()),
    )
    return list(result.scalars().all())


def journey_phases() -> list[str]:
    seen: list[str] = []
    for step in JOURNEY_STEPS:
        if step.phase not in seen:
            seen.append(step.phase)
    return seen
