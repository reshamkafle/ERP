from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import customer as customer_crud
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.schemas.customer import (
    CustomerCreate,
    CustomerDetailRead,
    CustomerListResponse,
    CustomerRead,
    CustomerSaleSummary,
    CustomerUpdate,
)

router = APIRouter(prefix="/customers")

CustomerReadRoles = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER)
CustomerManageRoles = require_roles(UserRole.ADMIN, UserRole.MANAGER)


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
        items=[CustomerRead.model_validate(c) for c in items],
        total=total,
    )


@router.get("/{customer_id}", response_model=CustomerDetailRead)
async def get_customer(
    customer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CustomerManageRoles)],
) -> CustomerDetailRead:
    customer, sales = await customer_crud.get_customer_with_recent_sales(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return CustomerDetailRead(
        id=customer.id,
        name=customer.name,
        phone=customer.phone,
        email=customer.email,
        notes=customer.notes,
        recent_sales=[
            CustomerSaleSummary(
                id=sale.id,
                created_at=sale.created_at,
                item_count=item_count,
                total=total,
            )
            for sale, item_count, total in sales
        ],
    )


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
    _: Annotated[User, Depends(CustomerManageRoles)],
) -> CustomerRead:
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    updated = await customer_crud.update_customer(db, customer, body)
    return CustomerRead.model_validate(updated)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
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
