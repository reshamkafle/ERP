from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import chart_of_account as coa_crud
from app.models.enums import JournalEntryStatus, JournalSourceType
from app.models.journal_entry import JournalEntry, JournalLine
from app.schemas.accounting import JournalLineIn


async def _next_entry_number(db: AsyncSession) -> str:
    year = date.today().year
    prefix = f"JE-{year}-"
    result = await db.execute(
        select(func.count())
        .select_from(JournalEntry)
        .where(JournalEntry.entry_number.like(f"{prefix}%")),
    )
    count = result.scalar_one() or 0
    return f"{prefix}{count + 1:06d}"


async def post_entry(
    db: AsyncSession,
    *,
    entry_date: date,
    source_type: JournalSourceType,
    source_id: int | None,
    description: str | None,
    lines: list[JournalLineIn],
    created_by_id: int | None,
    reversal_of_id: int | None = None,
) -> JournalEntry:
    if not lines:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Journal entry requires lines")

    total_debit = Decimal("0")
    total_credit = Decimal("0")
    validated_lines: list[tuple[JournalLineIn, object]] = []

    for line_in in lines:
        account = await coa_crud.get_account(db, line_in.account_id)
        if account is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Account {line_in.account_id} not found")
        if not account.is_postable:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Account {account.code} is not postable",
            )
        if line_in.debit > 0 and line_in.credit > 0:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="A line cannot have both debit and credit",
            )
        if line_in.debit == 0 and line_in.credit == 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Line must have debit or credit")
        total_debit += line_in.debit
        total_credit += line_in.credit
        validated_lines.append((line_in, account))

    if total_debit != total_credit:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Debits ({total_debit}) must equal credits ({total_credit})",
        )

    entry = JournalEntry(
        entry_number=await _next_entry_number(db),
        entry_date=entry_date,
        source_type=source_type,
        source_id=source_id,
        status=JournalEntryStatus.POSTED,
        description=description,
        reversal_of_id=reversal_of_id,
        created_by_id=created_by_id,
    )
    db.add(entry)
    await db.flush()

    for line_in, account in validated_lines:
        db.add(
            JournalLine(
                journal_entry_id=entry.id,
                account_id=account.id,
                debit=line_in.debit,
                credit=line_in.credit,
                currency_code=line_in.currency_code,
                memo=line_in.memo,
            ),
        )

    await db.flush()
    return entry


async def get_journal_for_source(
    db: AsyncSession,
    *,
    source_type: JournalSourceType,
    source_id: int,
) -> JournalEntry | None:
    result = await db.execute(
        select(JournalEntry)
        .options(selectinload(JournalEntry.lines).selectinload(JournalLine.account))
        .where(
            JournalEntry.source_type == source_type,
            JournalEntry.source_id == source_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
        )
        .order_by(JournalEntry.id.desc())
        .limit(1),
    )
    return result.scalar_one_or_none()
