from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import crm as crm_crud
from app.dependencies.auth import require_permission
from app.models.enums import LeadStatus, OpportunityStage
from app.models.user import User
from app.schemas.crm import (
    CrmActivityCreate,
    CrmActivityRead,
    CrmLeadCreate,
    CrmLeadListResponse,
    CrmLeadRead,
    CrmLeadUpdate,
    CrmOpportunityCreate,
    CrmOpportunityListResponse,
    CrmOpportunityRead,
    CrmOpportunityUpdate,
    CustomerContactCreate,
    CustomerContactRead,
    CustomerContactUpdate,
    PipelineStageSummary,
    PipelineSummaryRead,
)

router = APIRouter(prefix="/crm")

LeadsRead = require_permission("crm.leads.read")
LeadsWrite = require_permission("crm.leads.write")
OppsRead = require_permission("crm.opportunities.read")
OppsWrite = require_permission("crm.opportunities.write")
ContactsRead = require_permission("crm.contacts.read")
ContactsWrite = require_permission("crm.contacts.write")
ActivitiesRead = require_permission("crm.activities.read")
ActivitiesWrite = require_permission("crm.activities.write")


@router.get("/pipeline/summary", response_model=PipelineSummaryRead)
async def pipeline_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(OppsRead)],
) -> PipelineSummaryRead:
    stage_rows, total_open = await crm_crud.pipeline_summary(db)
    open_leads = await crm_crud.count_open_leads(db)
    return PipelineSummaryRead(
        stages=[
            PipelineStageSummary(stage=stage, count=count, total_value=value)
            for stage, count, value in stage_rows
        ],
        open_lead_count=open_leads,
        total_open_value=total_open,
    )


@router.get("/leads", response_model=CrmLeadListResponse)
async def list_leads(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(LeadsRead)],
    search: str | None = None,
    status: LeadStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> CrmLeadListResponse:
    items, total = await crm_crud.list_leads(db, search=search, status=status, skip=skip, limit=limit)
    return CrmLeadListResponse(
        items=[CrmLeadRead.model_validate(i) for i in items],
        total=total,
    )


@router.post("/leads", response_model=CrmLeadRead, status_code=status.HTTP_201_CREATED)
async def create_lead(
    body: CrmLeadCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(LeadsWrite)],
) -> CrmLeadRead:
    lead = await crm_crud.create_lead(db, body)
    return CrmLeadRead.model_validate(lead)


@router.get("/leads/{lead_id}", response_model=CrmLeadRead)
async def get_lead(
    lead_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(LeadsRead)],
) -> CrmLeadRead:
    lead = await crm_crud.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return CrmLeadRead.model_validate(lead)


@router.patch("/leads/{lead_id}", response_model=CrmLeadRead)
async def update_lead(
    lead_id: int,
    body: CrmLeadUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(LeadsWrite)],
) -> CrmLeadRead:
    lead = await crm_crud.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Lead not found")
    updated = await crm_crud.update_lead(db, lead, body)
    return CrmLeadRead.model_validate(updated)


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(LeadsWrite)],
) -> None:
    lead = await crm_crud.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Lead not found")
    await crm_crud.delete_lead(db, lead)


@router.get("/opportunities", response_model=CrmOpportunityListResponse)
async def list_opportunities(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(OppsRead)],
    customer_id: int | None = None,
    stage: OpportunityStage | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> CrmOpportunityListResponse:
    items, total = await crm_crud.list_opportunities(
        db,
        customer_id=customer_id,
        stage=stage,
        search=search,
        skip=skip,
        limit=limit,
    )
    return CrmOpportunityListResponse(
        items=[CrmOpportunityRead.model_validate(i) for i in items],
        total=total,
    )


@router.post("/opportunities", response_model=CrmOpportunityRead, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    body: CrmOpportunityCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(OppsWrite)],
) -> CrmOpportunityRead:
    opp = await crm_crud.create_opportunity(db, body, changed_by_id=user.id)
    return CrmOpportunityRead.model_validate(opp)


@router.get("/opportunities/{opportunity_id}", response_model=CrmOpportunityRead)
async def get_opportunity(
    opportunity_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(OppsRead)],
) -> CrmOpportunityRead:
    opp = await crm_crud.get_opportunity(db, opportunity_id)
    if opp is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return CrmOpportunityRead.model_validate(opp)


@router.patch("/opportunities/{opportunity_id}", response_model=CrmOpportunityRead)
async def update_opportunity(
    opportunity_id: int,
    body: CrmOpportunityUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(OppsWrite)],
) -> CrmOpportunityRead:
    opp = await crm_crud.get_opportunity(db, opportunity_id)
    if opp is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    updated = await crm_crud.update_opportunity(db, opp, body, changed_by_id=user.id)
    return CrmOpportunityRead.model_validate(updated)


@router.delete("/opportunities/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(OppsWrite)],
) -> None:
    opp = await crm_crud.get_opportunity(db, opportunity_id)
    if opp is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    await crm_crud.delete_opportunity(db, opp)


@router.get("/contacts", response_model=list[CustomerContactRead])
async def list_contacts(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ContactsRead)],
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[CustomerContactRead]:
    items, _ = await crm_crud.list_all_contacts(db, search=search, skip=skip, limit=limit)
    return [CustomerContactRead.model_validate(c) for c in items]
