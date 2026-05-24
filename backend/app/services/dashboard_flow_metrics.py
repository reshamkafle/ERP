from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.document_flow_cards import CARD_BY_ID, DOCUMENT_FLOW_CARDS, user_can_read_card
from app.models.customer import Customer
from app.models.enums import DeliveryStatus, ItemType, PaymentDirection
from app.models.manufacturing import BOMHeader
from app.models.manufacturing_ops import InspectionResult, MrpForecast, ProductionOrder
from app.models.module_record import ModuleRecord
from app.models.payment import Payment
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.sale import Sale
from app.models.supplier import Supplier
from app.schemas.dashboard import DocumentFlowCardMetrics, DocumentFlowChartPoint, DocumentFlowMetricsResponse


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _chart_start(period: str, now: datetime) -> datetime:
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    # week: last 7 days including today
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_today - timedelta(days=6)


async def _count_and_chart(
    db: AsyncSession,
    *,
    model,
    where=None,
    created_col=None,
    chart_start: datetime,
    chart_end: datetime,
    new_since: datetime,
) -> tuple[int, int, list[DocumentFlowChartPoint]]:
    created = created_col
    if created is None and hasattr(model, "created_at"):
        created = model.created_at

    total_stmt = select(func.count()).select_from(model)
    if where is not None:
        total_stmt = total_stmt.where(where)
    total = (await db.execute(total_stmt)).scalar_one()

    if created is None:
        return int(total), 0, []

    new_stmt = select(func.count()).select_from(model).where(created >= new_since)
    if where is not None:
        new_stmt = new_stmt.where(where)
    new_count = (await db.execute(new_stmt)).scalar_one()

    bucket = func.date_trunc("day", created)
    chart_stmt = (
        select(
            func.to_char(bucket, "Dy Mon DD").label("label"),
            func.count().label("count"),
        )
        .select_from(model)
        .where(created >= chart_start, created <= chart_end)
    )
    if where is not None:
        chart_stmt = chart_stmt.where(where)
    chart_stmt = chart_stmt.group_by(bucket).order_by(bucket)
    rows = (await db.execute(chart_stmt)).all()
    chart = [DocumentFlowChartPoint(label=r.label or "", count=int(r.count)) for r in rows]
    return int(total), int(new_count), chart


async def _combined_bom_po_metrics(
    db: AsyncSession,
    *,
    user_codes: set[str],
    chart_start: datetime,
    chart_end: datetime,
    new_since: datetime,
) -> tuple[int, int, list[DocumentFlowChartPoint]]:
    """BOM headers + production orders (sum totals; chart merges daily counts)."""
    include_bom = "warehouse.bom.read" in user_codes
    include_po = "manufacturing.ops.read" in user_codes
    if not include_bom and not include_po:
        return 0, 0, []

    total = 0
    new_count = 0
    day_counts: dict[str, int] = {}

    async def _accumulate(model, where=None) -> None:
        nonlocal total, new_count
        t, n, chart = await _count_and_chart(
            db,
            model=model,
            where=where,
            chart_start=chart_start,
            chart_end=chart_end,
            new_since=new_since,
        )
        total += t
        new_count += n
        for pt in chart:
            day_counts[pt.label] = day_counts.get(pt.label, 0) + pt.count

    if include_bom:
        await _accumulate(BOMHeader)
    if include_po:
        await _accumulate(ProductionOrder)

    chart = [DocumentFlowChartPoint(label=k, count=v) for k, v in day_counts.items()]
    return total, new_count, chart


async def _metrics_for_card(
    db: AsyncSession,
    card_id: str,
    *,
    user_codes: set[str],
    chart_start: datetime,
    chart_end: datetime,
    new_since: datetime,
) -> DocumentFlowCardMetrics | None:
    if card_id == "bom-wo":
        total, new_count, chart = await _combined_bom_po_metrics(
            db,
            user_codes=user_codes,
            chart_start=chart_start,
            chart_end=chart_end,
            new_since=new_since,
        )
        return DocumentFlowCardMetrics(id=card_id, total=total, new_count=new_count, chart=chart)

    open_delivery = Sale.delivery_status.in_(
        [DeliveryStatus.NOT_STARTED, DeliveryStatus.PENDING, DeliveryStatus.PARTIAL, DeliveryStatus.BLOCKED],
    )

    handlers: dict[str, tuple] = {
        "customer-start": (Customer, None),
        "customer-end": (Customer, None),
        "sales-order": (Sale, None),
        "mrp": (MrpForecast, None),
        "pr": (
            ModuleRecord,
            (ModuleRecord.module_code == "procurement")
            & (ModuleRecord.feature_code == "purchase_requisitions"),
        ),
        "po": (Purchase, None),
        "supplier": (Supplier, None),
        "grn": (
            ModuleRecord,
            (ModuleRecord.module_code == "procurement")
            & (ModuleRecord.feature_code == "goods_receipt"),
        ),
        "raw-inv": (Product, Product.item_type == ItemType.RAW),
        "mfg": (ProductionOrder, None),
        "qc": (InspectionResult, None),
        "fg-inv": (Product, Product.item_type == ItemType.FINISHED),
        "fg-out": (Product, Product.item_type == ItemType.FINISHED),
        "do": (Sale, open_delivery),
        "invoice": (Payment, Payment.direction == PaymentDirection.INBOUND),
    }

    spec = handlers.get(card_id)
    if spec is None:
        return None
    model, where = spec
    date_col = InspectionResult.inspected_at if card_id == "qc" else None
    total, new_count, chart = await _count_and_chart(
        db,
        model=model,
        where=where,
        created_col=date_col,
        chart_start=chart_start,
        chart_end=chart_end,
        new_since=new_since,
    )
    return DocumentFlowCardMetrics(id=card_id, total=total, new_count=new_count, chart=chart)


async def build_document_flow_metrics(
    db: AsyncSession,
    *,
    user_codes: set[str],
    period: str = "week",
    new_days: int = 30,
) -> DocumentFlowMetricsResponse:
    now = _utc_now()
    chart_start = _chart_start(period, now)
    new_since = now - timedelta(days=new_days)

    cards: list[DocumentFlowCardMetrics] = []
    for card_def in DOCUMENT_FLOW_CARDS:
        if not user_can_read_card(user_codes, card_def):
            continue
        metrics = await _metrics_for_card(
            db,
            card_def.id,
            user_codes=user_codes,
            chart_start=chart_start,
            chart_end=now,
            new_since=new_since,
        )
        if metrics is not None:
            cards.append(metrics)

    return DocumentFlowMetricsResponse(
        period=period if period in ("today", "week") else "week",
        new_days=new_days,
        cards=cards,
    )
