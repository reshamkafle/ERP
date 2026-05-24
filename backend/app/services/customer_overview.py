from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.crm import CrmActivity, CrmOpportunity, CustomerContact
from app.models.enums import DocumentPaymentStatus, OpportunityStage
from app.models.erp_document import ErpDocument
from app.models.payment import Payment
from app.models.sale import Sale
from app.schemas.customer import CustomerOverviewRead

_OPEN_STAGES = (
    OpportunityStage.PROSPECTING,
    OpportunityStage.QUALIFICATION,
    OpportunityStage.PROPOSAL,
    OpportunityStage.NEGOTIATION,
)


def _sale_total(sale: Sale) -> Decimal:
    return sum((item.price_at_sale * item.quantity for item in sale.items), Decimal("0"))


async def build_customer_overview(db: AsyncSession, customer_id: int) -> CustomerOverviewRead:
    sales_result = await db.execute(
        select(Sale).options(selectinload(Sale.items)).where(Sale.customer_id == customer_id),
    )
    sales = list(sales_result.scalars().all())
    now = datetime.now(timezone.utc)
    ytd_start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
    last_year_start = datetime(now.year - 1, 1, 1, tzinfo=timezone.utc)
    last_year_end = datetime(now.year, 1, 1, tzinfo=timezone.utc)

    total_revenue = Decimal("0")
    revenue_ytd = Decimal("0")
    revenue_last_year = Decimal("0")
    open_balance = Decimal("0")
    last_purchase_date: datetime | None = None

    for sale in sales:
        sale_total = _sale_total(sale)
        total_revenue += sale_total
        created = sale.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created >= ytd_start:
            revenue_ytd += sale_total
        if last_year_start <= created < last_year_end:
            revenue_last_year += sale_total
        if last_purchase_date is None or created > last_purchase_date:
            last_purchase_date = created
        if sale.payment_status != DocumentPaymentStatus.PAID:
            open_balance += sale_total - (sale.amount_paid or Decimal("0"))

    open_receivables = open_balance

    sale_count = len(sales)
    average_order_value = (total_revenue / sale_count) if sale_count else Decimal("0")
    years_span = max(1, now.year - (last_purchase_date.year if last_purchase_date else now.year) + 1)
    purchase_frequency = Decimal(str(sale_count)) / Decimal(str(years_span)) if sale_count else Decimal("0")

    opp_result = await db.execute(
        select(
            func.count(),
            func.coalesce(func.sum(CrmOpportunity.expected_value), 0),
        )
        .select_from(CrmOpportunity)
        .where(
            CrmOpportunity.customer_id == customer_id,
            CrmOpportunity.stage.in_(_OPEN_STAGES),
        ),
    )
    opp_row = opp_result.one()
    open_opp_count = opp_row[0]
    open_opp_value = Decimal(str(opp_row[1]))

    activity_count = (
        await db.execute(
            select(func.count()).select_from(CrmActivity).where(CrmActivity.customer_id == customer_id),
        )
    ).scalar_one()

    contact_count = (
        await db.execute(
            select(func.count()).select_from(CustomerContact).where(CustomerContact.customer_id == customer_id),
        )
    ).scalar_one()

    document_count = (
        await db.execute(
            select(func.count()).select_from(ErpDocument).where(ErpDocument.customer_id == customer_id),
        )
    ).scalar_one()

    payment_count = (
        await db.execute(
            select(func.count()).select_from(Payment).where(Payment.customer_id == customer_id),
        )
    ).scalar_one()

    return CustomerOverviewRead(
        customer_id=customer_id,
        total_revenue=total_revenue,
        lifetime_value=total_revenue,
        revenue_ytd=revenue_ytd,
        revenue_last_year=revenue_last_year,
        open_balance=open_balance,
        open_receivables=open_receivables,
        sale_count=sale_count,
        last_purchase_date=last_purchase_date,
        average_order_value=average_order_value,
        purchase_frequency_per_year=purchase_frequency,
        open_opportunity_count=open_opp_count,
        open_opportunity_value=open_opp_value,
        activity_count=activity_count,
        contact_count=contact_count,
        document_count=document_count,
        payment_count=payment_count,
    )
