from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AccountType, JournalEntryStatus, JournalSourceType


class ChartOfAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    account_type: AccountType
    parent_id: int | None
    is_postable: bool
    is_active: bool


class ChartOfAccountListResponse(BaseModel):
    items: list[ChartOfAccountRead]


class JournalLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    account_code: str
    account_name: str
    debit: Decimal
    credit: Decimal
    currency_code: str
    memo: str | None


class JournalEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entry_number: str
    entry_date: date
    source_type: JournalSourceType
    source_id: int | None
    status: JournalEntryStatus
    description: str | None
    lines: list[JournalLineRead] = Field(default_factory=list)
    created_at: datetime


class JournalLineIn(BaseModel):
    account_id: int = Field(ge=1)
    debit: Decimal = Field(ge=0, default=Decimal("0"))
    credit: Decimal = Field(ge=0, default=Decimal("0"))
    currency_code: str = Field(default="USD", min_length=3, max_length=3)
    memo: str | None = None
