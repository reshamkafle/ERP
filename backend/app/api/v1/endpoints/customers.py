from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import crm as crm_crud
from app.crud import customer as customer_crud
from app.dependencies.auth import require_permission
from app.models.user import User
from app.schemas.crm import (
    CrmActivityCreate,
    CrmActivityRead,
    CrmActivityUpdate,
    CrmOpportunityListResponse,
    CrmOpportunityRead,
    CustomerContactCreate,
    CustomerContactRead,
    CustomerContactUpdate,
)
from app.schemas.customer import (
    CustomerAuditLogRead,
    CustomerCreate,
    CustomerDetailRead,
    CustomerListItem,
    CustomerListResponse,
    CustomerOverviewRead,
    CustomerRead,
    CustomerSaleSummary,
    CustomerUpdate,
)
from app.crud import erp_document as erp_document_crud
from app.models.customer_audit_log import CustomerAuditLog
from app.schemas.erp_document import ErpDocumentListResponse
from app.services.customer_overview import build_customer_overview

router = APIRouter(prefix="/customers")

CustomerReadRoles = require_permission("sales.customers.read")
CustomerManageRoles = require_permission("sales.customers.write")
ContactsRead = require_permission("crm.contacts.read")
ContactsWrite = require_permission("crm.contacts.write")
ActivitiesRead = require_permission("crm.activities.read")
ActivitiesWrite = require_permission("crm.activities.write")
OppsRead = require_permission("crm.opportunities.read")


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CustomerReadRoles)],
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> CustomerListResponse:
    items, total = await customer_crud.list_customers(
        db,
        search=search,
        skip=skip,
        limit=limit,
    )
    return CustomerListResponse(
        items=[CustomerListItem.model_validate(c) for c in items],
        total=total,
    )


@router.get("/{customer_id}/overview", response_model=CustomerOverviewRead)
async def get_customer_overview(
    customer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CustomerReadRoles)],
) -> CustomerOverviewRead:
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return await build_customer_overview(db, customer_id)


@router.get("/{customer_id}/contacts", response_model=list[CustomerContactRead])
async def list_customer_contacts(
    customer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ContactsRead)],
) -> list[CustomerContactRead]:
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    contacts = await crm_crud.list_contacts_for_customer(db, customer_id)
    return [CustomerContactRead.model_validate(c) for c in contacts]


@router.post(
    "/{customer_id}/contacts",
    response_model=CustomerContactRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer_contact(
    customer_id: int,
    body: CustomerContactCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ContactsWrite)],
) -> CustomerContactRead:
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    contact = await crm_crud.create_contact(db, customer_id, body)
    return CustomerContactRead.model_validate(contact)


@router.patch("/{customer_id}/contacts/{contact_id}", response_model=CustomerContactRead)
async def update_customer_contact(
    customer_id: int,
    contact_id: int,
    body: CustomerContactUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ContactsWrite)],
) -> CustomerContactRead:
    contact = await crm_crud.get_contact(db, contact_id)
    if contact is None or contact.customer_id != customer_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Contact not found")
    updated = await crm_crud.update_contact(db, contact, body)
    return CustomerContactRead.model_validate(updated)


@router.delete("/{customer_id}/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer_contact(
    customer_id: int,
    contact_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ContactsWrite)],
) -> None:
    contact = await crm_crud.get_contact(db, contact_id)
    if contact is None or contact.customer_id != customer_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Contact not found")
    await crm_crud.delete_contact(db, contact)


@router.get("/{customer_id}/activities", response_model=list[CrmActivityRead])
async def list_customer_activities(
    customer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ActivitiesRead)],
    limit: int = Query(50, ge=1, le=200),
) -> list[CrmActivityRead]:
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    activities = await crm_crud.list_activities_for_customer(db, customer_id, limit=limit)
    return [CrmActivityRead.model_validate(a) for a in activities]


@router.post(
    "/{customer_id}/activities",
    response_model=CrmActivityRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer_activity(
    customer_id: int,
    body: CrmActivityCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(ActivitiesWrite)],
) -> CrmActivityRead:
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    activity = await crm_crud.create_activity(db, customer_id, body, created_by_id=user.id)
    return CrmActivityRead.model_validate(activity)


@router.patch(
    "/{customer_id}/activities/{activity_id}",
    response_model=CrmActivityRead,
)
async def update_customer_activity(
    customer_id: int,
    activity_id: int,
    body: CrmActivityUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ActivitiesWrite)],
) -> CrmActivityRead:
    activity = await crm_crud.get_activity(db, activity_id)
    if activity is None or activity.customer_id != customer_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Activity not found")
    updated = await crm_crud.update_activity(db, activity, body)
    return CrmActivityRead.model_validate(updated)


@router.delete(
    "/{customer_id}/activities/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_customer_activity(
    customer_id: int,
    activity_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ActivitiesWrite)],
) -> None:
    activity = await crm_crud.get_activity(db, activity_id)
    if activity is None or activity.customer_id != customer_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Activity not found")
    await crm_crud.delete_activity(db, activity)


@router.get("/{customer_id}/opportunities", response_model=CrmOpportunityListResponse)
async def list_customer_opportunities(
    customer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(OppsRead)],
) -> CrmOpportunityListResponse:
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    items, total = await crm_crud.list_opportunities(db, customer_id=customer_id, limit=100)
    return CrmOpportunityListResponse(
        items=[CrmOpportunityRead.model_validate(i) for i in items],
        total=total,
    )


@router.get("/{customer_id}", response_model=CustomerDetailRead)
async def get_customer(
    customer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CustomerReadRoles)],
) -> CustomerDetailRead:
    customer, sales = await customer_crud.get_customer_with_recent_sales(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return CustomerDetailRead(
        **CustomerRead.model_validate(customer).model_dump(),
        recent_sales=[
            CustomerSaleSummary(
                id=sale.id,
                order_number=sale.order_number,
                created_at=sale.created_at,
                item_count=item_count,
                total=total,
                order_status=sale.order_status.value,
            )
            for sale, item_count, total in sales
        ],
    )


@router.get("/{customer_id}/documents", response_model=ErpDocumentListResponse)
async def list_customer_documents(
    customer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CustomerReadRoles)],
    limit: int = Query(50, ge=1, le=200),
) -> ErpDocumentListResponse:
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    items, total = await erp_document_crud.list_erp_documents(
        db,
        customer_id=customer_id,
        limit=limit,
    )
    return ErpDocumentListResponse(
        items=[erp_document_crud.document_to_read(d) for d in items],
        total=total,
    )


@router.get("/{customer_id}/audit-log", response_model=list[CustomerAuditLogRead])
async def list_customer_audit_log(
    customer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CustomerReadRoles)],
    limit: int = Query(50, ge=1, le=200),
) -> list[CustomerAuditLogRead]:
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    result = await db.execute(
        select(CustomerAuditLog)
        .where(CustomerAuditLog.customer_id == customer_id)
        .order_by(CustomerAuditLog.created_at.desc())
        .limit(limit),
    )
    return [CustomerAuditLogRead.model_validate(row) for row in result.scalars().all()]


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    body: CustomerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CustomerManageRoles)],
) -> CustomerRead:
    customer = await customer_crud.create_customer(db, body)
    return CustomerRead.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: int,
    body: CustomerUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(CustomerManageRoles)],
) -> CustomerRead:
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    updated = await customer_crud.update_customer(db, customer, body, user_id=user.id)
    return CustomerRead.model_validate(updated)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("sales.customers.delete"))],
) -> None:
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    sale_count = await customer_crud.count_customer_sales(db, customer_id)
    if sale_count:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Cannot delete customer with purchase history",
        )
    await customer_crud.delete_customer(db, customer)
