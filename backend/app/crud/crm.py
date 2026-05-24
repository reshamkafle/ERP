from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.crm import (
    CrmActivity,
    CrmLead,
    CrmOpportunity,
    CrmOpportunityStageHistory,
    CustomerContact,
    build_contact_display_name,
)
from app.models.enums import LeadStatus, OpportunityStage
from app.schemas.crm import (
    CrmActivityCreate,
    CrmActivityUpdate,
    CrmLeadCreate,
    CrmLeadUpdate,
    CrmOpportunityCreate,
    CrmOpportunityUpdate,
    CustomerContactCreate,
    CustomerContactUpdate,
)


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _contact_row_data(payload: CustomerContactCreate | CustomerContactUpdate, *, is_create: bool) -> dict:
    if hasattr(payload, "model_dump"):
        data = payload.model_dump(exclude_unset=not is_create)
    else:
        data = dict(payload)
    for key in (
        "email",
        "email_secondary",
        "phone",
        "phone_secondary",
        "role",
        "title",
        "department",
        "notes",
        "relationship_strength",
        "contact_code",
        "salutation",
        "first_name",
        "middle_name",
        "last_name",
        "linkedin_url",
        "preferred_language",
    ):
        if key in data and isinstance(data[key], str):
            data[key] = _normalize_optional(data[key])
    if data.get("email"):
        data["email"] = str(data["email"])
    if data.get("email_secondary"):
        data["email_secondary"] = str(data["email_secondary"])
    data["name"] = build_contact_display_name(
        salutation=data.get("salutation"),
        first_name=data.get("first_name"),
        middle_name=data.get("middle_name"),
        last_name=data.get("last_name"),
        fallback=data.get("name") or "Contact",
    )
    return data


# --- Contacts ---


async def list_contacts_for_customer(db: AsyncSession, customer_id: int) -> list[CustomerContact]:
    result = await db.execute(
        select(CustomerContact)
        .where(CustomerContact.customer_id == customer_id)
        .order_by(CustomerContact.is_primary.desc(), CustomerContact.name),
    )
    return list(result.scalars().all())


async def list_all_contacts(
    db: AsyncSession,
    *,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[CustomerContact], int]:
    stmt = select(CustomerContact)
    count_stmt = select(func.count()).select_from(CustomerContact)
    if search:
        pattern = f"%{search.strip()}%"
        filt = or_(
            CustomerContact.name.ilike(pattern),
            CustomerContact.email.ilike(pattern),
            CustomerContact.role.ilike(pattern),
            CustomerContact.first_name.ilike(pattern),
            CustomerContact.last_name.ilike(pattern),
        )
        stmt = stmt.where(filt)
        count_stmt = count_stmt.where(filt)
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.order_by(CustomerContact.name).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def get_contact(db: AsyncSession, contact_id: int) -> CustomerContact | None:
    result = await db.execute(select(CustomerContact).where(CustomerContact.id == contact_id))
    return result.scalar_one_or_none()


async def create_contact(
    db: AsyncSession,
    customer_id: int,
    payload: CustomerContactCreate,
) -> CustomerContact:
    data = _contact_row_data(payload, is_create=True)
    if data.get("is_primary"):
        await _clear_primary_contact(db, customer_id)
    contact = CustomerContact(customer_id=customer_id, **data)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
    db: AsyncSession,
    contact: CustomerContact,
    payload: CustomerContactUpdate,
) -> CustomerContact:
    patch = payload.model_dump(exclude_unset=True)
    merged = {
        "salutation": contact.salutation,
        "first_name": contact.first_name,
        "middle_name": contact.middle_name,
        "last_name": contact.last_name,
        "name": contact.name,
        **patch,
    }
    merged["name"] = build_contact_display_name(
        salutation=merged.get("salutation"),
        first_name=merged.get("first_name"),
        middle_name=merged.get("middle_name"),
        last_name=merged.get("last_name"),
        fallback=merged.get("name") or "Contact",
    )
    data = _contact_row_data(
        CustomerContactUpdate.model_validate(merged),
        is_create=False,
    )
    if data.get("is_primary"):
        await _clear_primary_contact(db, contact.customer_id, exclude_id=contact.id)
    for key, value in data.items():
        setattr(contact, key, value)
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(db: AsyncSession, contact: CustomerContact) -> None:
    await db.delete(contact)
    await db.commit()


async def _clear_primary_contact(
    db: AsyncSession,
    customer_id: int,
    *,
    exclude_id: int | None = None,
) -> None:
    result = await db.execute(
        select(CustomerContact).where(
            CustomerContact.customer_id == customer_id,
            CustomerContact.is_primary.is_(True),
        ),
    )
    for row in result.scalars().all():
        if exclude_id is None or row.id != exclude_id:
            row.is_primary = False


# --- Activities ---


async def list_activities_for_customer(
    db: AsyncSession,
    customer_id: int,
    *,
    limit: int = 50,
) -> list[CrmActivity]:
    result = await db.execute(
        select(CrmActivity)
        .where(CrmActivity.customer_id == customer_id)
        .order_by(CrmActivity.occurred_at.desc())
        .limit(limit),
    )
    return list(result.scalars().all())


async def get_activity(db: AsyncSession, activity_id: int) -> CrmActivity | None:
    result = await db.execute(select(CrmActivity).where(CrmActivity.id == activity_id))
    return result.scalar_one_or_none()


async def create_activity(
    db: AsyncSession,
    customer_id: int,
    payload: CrmActivityCreate,
    *,
    created_by_id: int | None = None,
) -> CrmActivity:
    activity = CrmActivity(
        customer_id=customer_id,
        created_by_id=created_by_id,
        **payload.model_dump(),
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def update_activity(
    db: AsyncSession,
    activity: CrmActivity,
    payload: CrmActivityUpdate,
) -> CrmActivity:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if isinstance(value, str):
            value = _normalize_optional(value)
        setattr(activity, key, value)
    await db.commit()
    await db.refresh(activity)
    return activity


async def delete_activity(db: AsyncSession, activity: CrmActivity) -> None:
    await db.delete(activity)
    await db.commit()


# --- Leads ---


async def list_leads(
    db: AsyncSession,
    *,
    search: str | None = None,
    status: LeadStatus | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[CrmLead], int]:
    stmt = select(CrmLead)
    count_stmt = select(func.count()).select_from(CrmLead)
    if status:
        stmt = stmt.where(CrmLead.status == status)
        count_stmt = count_stmt.where(CrmLead.status == status)
    if search:
        pattern = f"%{search.strip()}%"
        filt = or_(
            CrmLead.company_name.ilike(pattern),
            CrmLead.contact_name.ilike(pattern),
            CrmLead.email.ilike(pattern),
        )
        stmt = stmt.where(filt)
        count_stmt = count_stmt.where(filt)
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.order_by(CrmLead.updated_at.desc()).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def get_lead(db: AsyncSession, lead_id: int) -> CrmLead | None:
    result = await db.execute(select(CrmLead).where(CrmLead.id == lead_id))
    return result.scalar_one_or_none()


async def create_lead(db: AsyncSession, payload: CrmLeadCreate) -> CrmLead:
    data = payload.model_dump()
    for key in (
        "contact_name",
        "phone",
        "source",
        "description",
        "campaign_source",
        "bant_budget",
        "bant_authority",
        "bant_need",
        "bant_timeline",
    ):
        if key in data:
            data[key] = _normalize_optional(data.get(key))
    if data.get("email"):
        data["email"] = str(data["email"])
    lead = CrmLead(**data)
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


async def update_lead(db: AsyncSession, lead: CrmLead, payload: CrmLeadUpdate) -> CrmLead:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if isinstance(value, str):
            value = _normalize_optional(value)
        setattr(lead, key, value)
    lead.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(lead)
    return lead


async def delete_lead(db: AsyncSession, lead: CrmLead) -> None:
    await db.delete(lead)
    await db.commit()


# --- Opportunities ---

_OPEN_STAGES = (
    OpportunityStage.PROSPECTING,
    OpportunityStage.QUALIFICATION,
    OpportunityStage.PROPOSAL,
    OpportunityStage.NEGOTIATION,
)


async def _record_stage_change(
    db: AsyncSession,
    opp: CrmOpportunity,
    from_stage: str | None,
    to_stage: str,
    *,
    changed_by_id: int | None = None,
) -> None:
    if from_stage == to_stage:
        return
    history = CrmOpportunityStageHistory(
        opportunity_id=opp.id,
        from_stage=from_stage,
        to_stage=to_stage,
        changed_by_id=changed_by_id,
    )
    db.add(history)


async def list_opportunities(
    db: AsyncSession,
    *,
    customer_id: int | None = None,
    stage: OpportunityStage | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[CrmOpportunity], int]:
    stmt = select(CrmOpportunity).options(selectinload(CrmOpportunity.stage_history))
    count_stmt = select(func.count()).select_from(CrmOpportunity)
    if customer_id is not None:
        stmt = stmt.where(CrmOpportunity.customer_id == customer_id)
        count_stmt = count_stmt.where(CrmOpportunity.customer_id == customer_id)
    if stage is not None:
        stmt = stmt.where(CrmOpportunity.stage == stage)
        count_stmt = count_stmt.where(CrmOpportunity.stage == stage)
    if search:
        pattern = f"%{search.strip()}%"
        filt = CrmOpportunity.title.ilike(pattern)
        stmt = stmt.where(filt)
        count_stmt = count_stmt.where(filt)
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(CrmOpportunity.updated_at.desc()).offset(skip).limit(limit),
    )
    return list(result.scalars().unique().all()), total


async def get_opportunity(db: AsyncSession, opportunity_id: int) -> CrmOpportunity | None:
    result = await db.execute(
        select(CrmOpportunity)
        .options(selectinload(CrmOpportunity.stage_history))
        .where(CrmOpportunity.id == opportunity_id),
    )
    return result.scalar_one_or_none()


async def create_opportunity(
    db: AsyncSession,
    payload: CrmOpportunityCreate,
    *,
    changed_by_id: int | None = None,
) -> CrmOpportunity:
    opp = CrmOpportunity(**payload.model_dump())
    db.add(opp)
    await db.flush()
    await _record_stage_change(
        db,
        opp,
        from_stage=None,
        to_stage=opp.stage.value,
        changed_by_id=changed_by_id,
    )
    await db.commit()
    await db.refresh(opp)
    return opp


async def update_opportunity(
    db: AsyncSession,
    opp: CrmOpportunity,
    payload: CrmOpportunityUpdate,
    *,
    changed_by_id: int | None = None,
) -> CrmOpportunity:
    data = payload.model_dump(exclude_unset=True)
    old_stage = opp.stage.value if opp.stage else None
    if "stage" in data and data["stage"] is not None:
        new_stage = data["stage"].value if hasattr(data["stage"], "value") else data["stage"]
        if new_stage != old_stage:
            await _record_stage_change(
                db,
                opp,
                from_stage=old_stage,
                to_stage=new_stage,
                changed_by_id=changed_by_id,
            )
    for key, value in data.items():
        if isinstance(value, str):
            value = _normalize_optional(value)
        setattr(opp, key, value)
    opp.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(opp)
    return opp


async def delete_opportunity(db: AsyncSession, opp: CrmOpportunity) -> None:
    await db.delete(opp)
    await db.commit()


async def list_opportunity_stage_history(
    db: AsyncSession,
    opportunity_id: int,
) -> list[CrmOpportunityStageHistory]:
    result = await db.execute(
        select(CrmOpportunityStageHistory)
        .where(CrmOpportunityStageHistory.opportunity_id == opportunity_id)
        .order_by(CrmOpportunityStageHistory.changed_at.desc()),
    )
    return list(result.scalars().all())


async def count_open_leads(db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(CrmLead)
        .where(CrmLead.status.not_in((LeadStatus.CONVERTED, LeadStatus.LOST))),
    )
    return result.scalar_one()


async def pipeline_summary(db: AsyncSession) -> tuple[list[tuple[OpportunityStage, int, Decimal]], Decimal]:
    rows = await db.execute(
        select(
            CrmOpportunity.stage,
            func.count(),
            func.coalesce(func.sum(CrmOpportunity.expected_value), 0),
        )
        .where(CrmOpportunity.stage.in_(_OPEN_STAGES))
        .group_by(CrmOpportunity.stage),
    )
    stage_rows = [(r[0], r[1], Decimal(str(r[2]))) for r in rows.all()]
    total_open = sum(v for _, _, v in stage_rows)
    return stage_rows, total_open
