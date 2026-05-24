from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import tax_rate as tax_rate_crud
from app.dependencies.auth import require_permission
from app.models.user import User
from app.schemas.tax import TaxRateCreate, TaxRateListResponse, TaxRateRead, TaxRateUpdate

router = APIRouter(prefix="/tax-rates")

TaxRead = require_permission("finance.tax.read", "finance.records.read")
TaxWrite = require_permission("finance.tax.write", "finance.records.write")


@router.get("", response_model=TaxRateListResponse)
async def list_tax_rates(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(TaxRead)],
    country_code: str | None = None,
    is_active: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> TaxRateListResponse:
    items, total = await tax_rate_crud.list_tax_rates(
        db,
        country_code=country_code,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )
    return TaxRateListResponse(
        items=[TaxRateRead.model_validate(i) for i in items],
        total=total,
    )


@router.get("/active", response_model=TaxRateRead)
async def get_active_tax_rate(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(TaxRead)],
    code: str,
    country_code: str,
    as_of: date | None = None,
) -> TaxRateRead:
    row = await tax_rate_crud.get_active_tax_rate(
        db,
        code=code,
        country_code=country_code,
        as_of=as_of or date.today(),
    )
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No active tax rate found")
    return TaxRateRead.model_validate(row)


@router.get("/{tax_rate_id}", response_model=TaxRateRead)
async def get_tax_rate(
    tax_rate_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(TaxRead)],
) -> TaxRateRead:
    row = await tax_rate_crud.get_tax_rate(db, tax_rate_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tax rate not found")
    return TaxRateRead.model_validate(row)


@router.post("", response_model=TaxRateRead, status_code=status.HTTP_201_CREATED)
async def create_tax_rate(
    body: TaxRateCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(TaxWrite)],
) -> TaxRateRead:
    row = await tax_rate_crud.create_tax_rate(db, body)
    return TaxRateRead.model_validate(row)


@router.patch("/{tax_rate_id}", response_model=TaxRateRead)
async def update_tax_rate(
    tax_rate_id: int,
    body: TaxRateUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(TaxWrite)],
) -> TaxRateRead:
    row = await tax_rate_crud.get_tax_rate(db, tax_rate_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tax rate not found")
    updated = await tax_rate_crud.update_tax_rate(db, row, body)
    return TaxRateRead.model_validate(updated)


@router.delete("/{tax_rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tax_rate(
    tax_rate_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(TaxWrite)],
) -> None:
    row = await tax_rate_crud.get_tax_rate(db, tax_rate_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tax rate not found")
    await tax_rate_crud.delete_tax_rate(db, row)
