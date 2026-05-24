from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import erp_document as erp_document_crud
from app.dependencies.auth import require_permission
from app.documents.journey import JOURNEY_STEPS
from app.models.enums import ErpDocumentType
from app.models.user import User
from app.schemas.erp_document import (
    ErpDocumentCreate,
    ErpDocumentJourneyGroup,
    ErpDocumentJourneyViewResponse,
    ErpDocumentListResponse,
    ErpDocumentRead,
    ErpDocumentUpdate,
    JourneyResponse,
    JourneyStepRead,
)

router = APIRouter(prefix="/erp-documents")

DocumentReadRoles = require_permission("warehouse.documents.read")
DocumentManageRoles = require_permission("warehouse.documents.write")


@router.get("/journey", response_model=JourneyResponse)
async def get_journey(
    _: Annotated[User, Depends(DocumentReadRoles)],
) -> JourneyResponse:
    steps = [
        JourneyStepRead(
            document_type=s.document_type,
            journey_step=s.journey_step,
            phase=s.phase,
            label=s.label,
            slug=s.slug,
            number_prefix=s.number_prefix,
        )
        for s in JOURNEY_STEPS
    ]
    return JourneyResponse(steps=steps, phases=erp_document_crud.journey_phases())


@router.get("/journey-view", response_model=ErpDocumentJourneyViewResponse)
async def get_journey_view(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(DocumentReadRoles)],
) -> ErpDocumentJourneyViewResponse:
    all_docs = await erp_document_crud.list_all_for_journey_view(db)
    by_type: dict[ErpDocumentType, list] = {}
    for doc in all_docs:
        by_type.setdefault(doc.document_type, []).append(erp_document_crud.document_to_read(doc))

    phases: list[ErpDocumentJourneyGroup] = []
    current_phase: str | None = None
    group: ErpDocumentJourneyGroup | None = None

    for step in JOURNEY_STEPS:
        step_read = JourneyStepRead(
            document_type=step.document_type,
            journey_step=step.journey_step,
            phase=step.phase,
            label=step.label,
            slug=step.slug,
            number_prefix=step.number_prefix,
        )
        docs_for_step = by_type.get(step.document_type, [])
        if step.phase != current_phase:
            if group is not None:
                phases.append(group)
            current_phase = step.phase
            group = ErpDocumentJourneyGroup(
                phase=step.phase,
                journey_step_start=step.journey_step,
                steps=[],
                documents=[],
            )
        assert group is not None
        group.steps.append(step_read)
        group.documents.extend(docs_for_step)

    if group is not None:
        phases.append(group)

    return ErpDocumentJourneyViewResponse(
        phases=phases,
        total_documents=len(all_docs),
    )


@router.get("", response_model=ErpDocumentListResponse)
async def list_erp_documents(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(DocumentReadRoles)],
    search: str | None = None,
    document_type: ErpDocumentType | None = None,
    phase: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> ErpDocumentListResponse:
    items, total = await erp_document_crud.list_erp_documents(
        db,
        search=search,
        document_type=document_type,
        phase=phase,
        skip=skip,
        limit=limit,
    )
    return ErpDocumentListResponse(
        items=[erp_document_crud.document_to_read(d) for d in items],
        total=total,
    )


@router.get("/{document_id}", response_model=ErpDocumentRead)
async def get_erp_document(
    document_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(DocumentReadRoles)],
) -> ErpDocumentRead:
    doc = await erp_document_crud.get_erp_document(db, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Document not found")
    return erp_document_crud.document_to_read(doc)


@router.post("", response_model=ErpDocumentRead, status_code=status.HTTP_201_CREATED)
async def create_erp_document(
    body: ErpDocumentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(DocumentManageRoles)],
) -> ErpDocumentRead:
    doc = await erp_document_crud.create_erp_document(db, body, created_by_id=user.id)
    return erp_document_crud.document_to_read(doc)


@router.patch("/{document_id}", response_model=ErpDocumentRead)
async def update_erp_document(
    document_id: int,
    body: ErpDocumentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(DocumentManageRoles)],
) -> ErpDocumentRead:
    doc = await erp_document_crud.get_erp_document(db, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Document not found")
    updated = await erp_document_crud.update_erp_document(db, doc, body)
    return erp_document_crud.document_to_read(updated)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_erp_document(
    document_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("warehouse.documents.delete"))],
) -> None:
    doc = await erp_document_crud.get_erp_document(db, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Document not found")
    await erp_document_crud.delete_erp_document(db, doc)
