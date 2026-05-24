from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import customer as customer_crud
from app.models.customer import Customer
from app.models.enums import (
    AtpCheckStatus,
    BillingStatus,
    CreditCheckStatus,
    DeliveryStatus,
    DocumentPaymentStatus,
    InventoryTransactionType,
    ItemLifecycleStatus,
    SaleLineStatus,
    SaleOrderStatus,
)
from app.models.product import Product
from app.models.sale import Sale, SaleItem, SalePartner
from app.schemas.sale import (
    PosCheckoutCreate,
    SaleConfirmRequest,
    SaleItemLineCreate,
    SaleOrderCreate,
    SaleOrderUpdate,
    _validate_b2b_fields,
)
from app.services.customer_snapshot import json_to_dict, snapshot_from_customer, snapshot_to_json
from app.services.sale_atp_check import run_atp_check
from app.services.sale_credit_check import run_credit_check
from app.services.sale_order_number import resolve_order_number
from app.services.sale_partners import apply_partners_to_sale
from app.services.sale_totals import LineCalcInput, calc_line, calc_sale_totals
from app.services.tax_calculation import get_company_settings


def _append_workflow(sale: Sale, event_status: str, user_email: str | None = None, note: str | None = None) -> None:
    history = list(sale.workflow_history or [])
    history.append(
        {
            "at": datetime.now(timezone.utc).isoformat(),
            "status": event_status,
            "user_email": user_email,
            "note": note,
        },
    )
    sale.workflow_history = history


def _sync_po_from_references(sale: Sale, payload: SaleOrderCreate | SaleOrderUpdate) -> None:
    if payload.customer_po_number is not None:
        sale.customer_po_number = payload.customer_po_number
    if payload.customer_po_date is not None:
        sale.customer_po_date = payload.customer_po_date
    refs = payload.references
    if refs is None:
        return
    if sale.customer_po_number is None and refs.customer_po_number:
        sale.customer_po_number = refs.customer_po_number
    if sale.customer_po_date is None and refs.customer_po_date:
        sale.customer_po_date = refs.customer_po_date


def _json_bundle(payload: SaleOrderCreate | SaleOrderUpdate) -> dict:
    return {
        "customer_snapshot": snapshot_to_json(payload.customer_snapshot)
        if getattr(payload, "customer_snapshot", None)
        else None,
        "pricing_conditions": json_to_dict(payload.pricing_conditions),
        "delivery_logistics": json_to_dict(payload.delivery_logistics),
        "billing_financial": json_to_dict(payload.billing_financial),
        "terms_compliance": json_to_dict(payload.terms_compliance),
        "references": json_to_dict(payload.references),
        "attachments": [a.model_dump(mode="json") for a in payload.attachments]
        if payload.attachments
        else None,
    }


async def _load_products(
    db: AsyncSession,
    product_ids: list[int],
    *,
    for_update: bool = False,
) -> dict[int, Product]:
    stmt = select(Product).where(Product.id.in_(product_ids))
    if for_update:
        stmt = stmt.with_for_update()
    result = await db.execute(stmt)
    products = {p.id: p for p in result.scalars().all()}
    if len(products) != len(product_ids):
        missing = set(product_ids) - set(products.keys())
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Product(s) not found: {sorted(missing)}",
        )
    return products


def _resolve_unit_price(
    line: SaleItemLineCreate,
    product: Product,
    *,
    allow_price_override: bool,
) -> Decimal:
    """Use catalog price unless caller may override and supplies a different unit_price."""
    catalog_price = product.price
    if line.unit_price is None:
        return catalog_price
    if allow_price_override:
        return line.unit_price
    if line.unit_price != catalog_price:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Price override not permitted for {product.sku}; use catalog price",
        )
    return catalog_price


async def _build_line_inputs(
    db: AsyncSession,
    lines: list[SaleItemLineCreate],
    products: dict[int, Product],
    *,
    allow_price_override: bool = False,
) -> list[tuple[SaleItemLineCreate, Product, LineCalcInput]]:
    built: list[tuple[SaleItemLineCreate, Product, LineCalcInput]] = []
    for line in lines:
        product = products[line.product_id]
        if product.lifecycle_status != ItemLifecycleStatus.ACTIVE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.sku} is not available for sale",
            )
        unit_price = _resolve_unit_price(line, product, allow_price_override=allow_price_override)
        calc_input = LineCalcInput(
            product=product,
            quantity=line.quantity,
            unit_price=unit_price,
            discount_percent=line.discount_percent,
            discount_amount=line.discount_amount,
            tax_rate_id=line.tax_rate_id,
        )
        built.append((line, product, calc_input))
    return built


def _line_item_from_row(
    idx: int,
    line: SaleItemLineCreate,
    product: Product,
    calc_input: LineCalcInput,
    result,
    *,
    header_warehouse_id: int | None,
) -> SaleItem:
    gross_price = line.gross_price or (calc_input.unit_price * line.quantity).quantize(Decimal("0.01"))
    item_category = line.item_category or line.product_category or product.sub_category
    net_weight = line.net_weight if line.net_weight is not None else product.net_weight
    gross_weight = line.gross_weight if line.gross_weight is not None else product.gross_weight
    return SaleItem(
        line_number=idx,
        product_id=product.id,
        description=line.description or product.name,
        quantity=line.quantity,
        uom=line.uom or product.sales_uom or product.primary_uom,
        alternate_uom=line.alternate_uom,
        uom_conversion_factor=line.uom_conversion_factor,
        unit_price=calc_input.unit_price,
        price_at_sale=calc_input.unit_price,
        gross_price=gross_price,
        discount_percent=line.discount_percent,
        discount_amount=line.discount_amount,
        tax_code=line.tax_code or product.tax_code,
        tax_rate_id=line.tax_rate_id or product.tax_rate_id,
        tax_amount=result.tax,
        net_amount=result.net,
        line_total=result.line_total,
        requested_delivery_date=line.requested_delivery_date,
        confirmed_delivery_date=line.confirmed_delivery_date,
        line_status=line.line_status or SaleLineStatus.OPEN,
        product_category=line.product_category or product.sub_category,
        item_category=item_category,
        warehouse_id=line.warehouse_id or product.default_warehouse_id or header_warehouse_id,
        storage_location_id=line.storage_location_id or product.default_location_id,
        batch_number=line.batch_number,
        serial_number=line.serial_number,
        delivery_block=line.delivery_block,
        billing_block=line.billing_block,
        rejection_reason=line.rejection_reason,
        net_weight=net_weight,
        gross_weight=gross_weight,
        volume=line.volume,
        substitute_product_id=line.substitute_product_id,
        line_text=line.line_text,
    )


async def _apply_totals(
    db: AsyncSession,
    sale: Sale,
    calc_inputs: list[LineCalcInput],
) -> None:
    gross, subtotal, tax, total, _discount = await calc_sale_totals(
        db,
        lines=calc_inputs,
        header_discount_amount=sale.header_discount_amount,
        freight_amount=sale.freight_amount,
        insurance_amount=sale.insurance_amount,
        handling_amount=sale.handling_amount,
    )
    sale.gross_total = gross
    sale.subtotal = subtotal
    sale.tax_amount = tax
    sale.total = total


async def _replace_items(
    db: AsyncSession,
    sale: Sale,
    line_data: list[tuple[SaleItemLineCreate, Product, LineCalcInput]],
) -> None:
    if sale.id is not None:
        existing_rows = (
            await db.execute(select(SaleItem).where(SaleItem.sale_id == sale.id))
        ).scalars().all()
        for existing in existing_rows:
            await db.delete(existing)
    await db.flush()
    for idx, (line, product, calc_input) in enumerate(line_data, start=1):
        result = await calc_line(db, calc_input)
        item = _line_item_from_row(
            idx,
            line,
            product,
            calc_input,
            result,
            header_warehouse_id=sale.warehouse_id,
        )
        item.sale_id = sale.id
        db.add(item)


async def _resolve_customer(
    db: AsyncSession,
    payload: SaleOrderCreate | SaleOrderUpdate,
    *,
    existing_customer_id: int | None = None,
) -> tuple[Customer | None, dict | None]:
    customer: Customer | None = None
    snapshot_json = None
    customer_id = payload.customer_id if payload.customer_id is not None else existing_customer_id
    if customer_id is not None:
        customer = await customer_crud.get_customer(db, customer_id)
        if customer is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Customer not found")
        if payload.customer_snapshot:
            snapshot_json = snapshot_to_json(payload.customer_snapshot)
        else:
            snapshot_json = snapshot_to_json(snapshot_from_customer(customer))
    elif payload.customer_snapshot:
        snapshot_json = snapshot_to_json(payload.customer_snapshot)
    return customer, snapshot_json


def _header_from_payload(
    sale: Sale,
    payload: SaleOrderCreate | SaleOrderUpdate,
    *,
    snapshot_json: dict | None,
    bundles: dict,
    settings_currency: str,
) -> None:
    data = payload.model_dump(
        exclude_unset=True,
        exclude={
            "items",
            "confirm",
            "customer_snapshot",
            "partners",
            "references",
            "require_b2b_fields",
            "order_number_override",
            "workflow_approval",
        },
    )
    for key, value in data.items():
        if key in (
            "pricing_conditions",
            "delivery_logistics",
            "billing_financial",
            "terms_compliance",
            "attachments",
        ):
            continue
        setattr(sale, key, value)
    if not sale.currency_code:
        sale.currency_code = settings_currency
    if snapshot_json is not None:
        sale.customer_snapshot = snapshot_json
    for json_key in (
        "pricing_conditions",
        "delivery_logistics",
        "billing_financial",
        "terms_compliance",
        "references",
    ):
        if bundles.get(json_key) is not None:
            setattr(sale, json_key, bundles[json_key])
    if bundles.get("attachments") is not None:
        sale.attachments = bundles["attachments"]
    _sync_po_from_references(sale, payload)


def _apply_workflow_approval(sale: Sale, payload: SaleOrderCreate | SaleOrderUpdate) -> None:
    approval = getattr(payload, "workflow_approval", None)
    if approval is None:
        return
    data = approval.model_dump(mode="json", exclude_none=True)
    if not data:
        return
    history = list(sale.workflow_history or [])
    history.append(
        {
            "at": datetime.now(timezone.utc).isoformat(),
            "status": "APPROVAL",
            **data,
        },
    )
    sale.workflow_history = history


def _validate_b2b_payload(
    payload: SaleOrderCreate | SaleOrderUpdate,
    *,
    sale: Sale | None = None,
) -> None:
    if not payload.require_b2b_fields:
        return
    customer_id = payload.customer_id if payload.customer_id is not None else (sale.customer_id if sale else None)
    customer_po = payload.customer_po_number if payload.customer_po_number is not None else (sale.customer_po_number if sale else None)
    payment_terms = payload.payment_terms if payload.payment_terms is not None else (sale.payment_terms if sale else None)
    sales_org = payload.sales_organization if payload.sales_organization is not None else (sale.sales_organization if sale else None)
    if payload.items is not None:
        items = payload.items
    elif sale is not None:
        items = [
            SaleItemLineCreate(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in sale.items
        ]
    else:
        items = []
    _validate_b2b_fields(
        customer_id=customer_id,
        customer_po_number=customer_po,
        payment_terms=payment_terms,
        sales_organization=sales_org,
        items=items,
    )


async def create_sale_order(
    db: AsyncSession,
    payload: SaleOrderCreate,
    *,
    created_by_id: int,
    is_pos_checkout: bool = False,
    allow_price_override: bool = False,
) -> Sale:
    settings = await get_company_settings(db)
    _validate_b2b_payload(payload)
    customer, snapshot_json = await _resolve_customer(db, payload)
    bundles = _json_bundle(payload)

    product_ids = [line.product_id for line in payload.items]
    products = await _load_products(db, product_ids, for_update=payload.confirm)
    line_data = await _build_line_inputs(
        db, payload.items, products, allow_price_override=allow_price_override,
    )
    calc_inputs = [c for _, _, c in line_data]

    order_number = await resolve_order_number(
        db,
        override=getattr(payload, "order_number_override", None),
        as_of=payload.order_date,
    )
    sale = Sale(
        order_number=order_number,
        order_status=SaleOrderStatus.DRAFT,
        order_date=payload.order_date or date.today(),
        is_pos_checkout=is_pos_checkout,
        customer_id=payload.customer_id,
        created_by_id=created_by_id,
        currency_code=payload.currency_code or (customer.currency_code if customer else settings.default_currency),
        payment_terms=payload.payment_terms or (customer.payment_terms if customer else None),
        incoterms=payload.incoterms or (customer.incoterms if customer else None),
        price_group=payload.price_group or (customer.customer_group if customer else None),
    )
    _header_from_payload(sale, payload, snapshot_json=snapshot_json, bundles=bundles, settings_currency=settings.default_currency)
    apply_partners_to_sale(sale, payload.partners, customer=customer)
    _apply_workflow_approval(sale, payload)
    db.add(sale)
    await db.flush()
    await _replace_items(db, sale, line_data)
    await _apply_totals(db, sale, calc_inputs)
    _append_workflow(sale, "DRAFT", note="Order created")

    if payload.confirm or is_pos_checkout:
        await confirm_sale_order(
            db,
            sale,
            SaleConfirmRequest(run_credit_check=not is_pos_checkout, run_atp_check=True),
            user_id=created_by_id,
            is_pos_checkout=is_pos_checkout,
        )
    else:
        await db.commit()

    return await get_sale(db, sale.id)  # type: ignore[return-value]


async def update_sale_order(
    db: AsyncSession,
    sale: Sale,
    payload: SaleOrderUpdate,
    *,
    updated_by_id: int,
    allow_price_override: bool = False,
) -> Sale:
    if sale.order_status != SaleOrderStatus.DRAFT:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Only draft orders can be updated")

    settings = await get_company_settings(db)
    _validate_b2b_payload(payload, sale=sale)
    customer, snapshot_json = await _resolve_customer(
        db, payload, existing_customer_id=sale.customer_id,
    )
    bundles = _json_bundle(payload)
    _header_from_payload(sale, payload, snapshot_json=snapshot_json, bundles=bundles, settings_currency=settings.default_currency)
    if payload.customer_id is not None:
        sale.customer_id = payload.customer_id
    sale.updated_at = datetime.now(timezone.utc)
    sale.updated_by_id = updated_by_id

    if payload.partners is not None or (payload.customer_id is not None and customer):
        apply_partners_to_sale(sale, payload.partners, customer=customer)

    _apply_workflow_approval(sale, payload)

    if payload.items is not None:
        product_ids = [line.product_id for line in payload.items]
        products = await _load_products(db, product_ids)
        line_data = await _build_line_inputs(
            db, payload.items, products, allow_price_override=allow_price_override,
        )
        await _replace_items(db, sale, line_data)
        calc_inputs = [c for _, _, c in line_data]
        await _apply_totals(db, sale, calc_inputs)

    _append_workflow(sale, "DRAFT", note="Order updated")
    await db.commit()
    return await get_sale(db, sale.id)  # type: ignore[return-value]


async def confirm_sale_order(
    db: AsyncSession,
    sale: Sale,
    request: SaleConfirmRequest,
    *,
    user_id: int,
    is_pos_checkout: bool = False,
) -> Sale:
    if sale.order_status not in (SaleOrderStatus.DRAFT, SaleOrderStatus.CREATED):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Order cannot be confirmed")

    result = await db.execute(
        select(Sale)
        .options(selectinload(Sale.items).selectinload(SaleItem.product))
        .where(Sale.id == sale.id)
        .with_for_update(),
    )
    sale = result.scalar_one()
    customer = await customer_crud.get_customer(db, sale.customer_id) if sale.customer_id else None

    if request.run_atp_check:
        await run_atp_check(db, sale)
        if sale.atp_check_status == AtpCheckStatus.UNAVAILABLE and not is_pos_checkout:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="ATP check failed: insufficient stock")

    if request.run_credit_check:
        await run_credit_check(
            db,
            sale,
            customer,
            override=request.override_credit_failure,
        )
        if (
            sale.credit_check_status == CreditCheckStatus.FAILED
            and not request.override_credit_failure
            and not is_pos_checkout
        ):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Credit check failed")

    from app.services.inventory_posting import adjust_product_stock

    for item in sale.items:
        product = item.product
        if product.stock < item.quantity:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.sku}",
            )
        await adjust_product_stock(
            db,
            product,
            -item.quantity,
            transaction_type=InventoryTransactionType.ISSUE,
            reference_document=f"SALE-{sale.id}",
            user_id=user_id,
        )
        item.price_at_sale = item.unit_price
        if item.confirmed_quantity == 0:
            item.confirmed_quantity = item.quantity
        item.line_status = SaleLineStatus.ALLOCATED

    sale.order_status = SaleOrderStatus.RELEASED
    sale.delivery_status = sale.delivery_status or DeliveryStatus.PENDING
    sale.invoice_status = sale.invoice_status or BillingStatus.NOT_INVOICED

    if is_pos_checkout:
        sale.amount_paid = sale.total
        sale.payment_status = DocumentPaymentStatus.PAID
    else:
        sale.amount_paid = Decimal("0")
        sale.payment_status = DocumentPaymentStatus.UNPAID

    _append_workflow(sale, "RELEASED", note="Order confirmed")
    await db.commit()
    return await get_sale(db, sale.id)  # type: ignore[return-value]


async def cancel_sale_order(
    db: AsyncSession,
    sale: Sale,
    *,
    user_id: int,
    reason: str | None = None,
) -> Sale:
    if sale.order_status == SaleOrderStatus.CANCELLED:
        return sale
    if sale.order_status == SaleOrderStatus.DRAFT:
        sale.order_status = SaleOrderStatus.CANCELLED
        _append_workflow(sale, "CANCELLED", note=reason or "Draft cancelled")
        await db.commit()
        return await get_sale(db, sale.id)  # type: ignore[return-value]

    if sale.order_status in (SaleOrderStatus.RELEASED, SaleOrderStatus.IN_PROCESS):
        from app.services.inventory_posting import adjust_product_stock

        result = await db.execute(
            select(Sale)
            .options(selectinload(Sale.items).selectinload(SaleItem.product))
            .where(Sale.id == sale.id)
            .with_for_update(),
        )
        sale = result.scalar_one()
        for item in sale.items:
            await adjust_product_stock(
                db,
                item.product,
                item.quantity,
                transaction_type=InventoryTransactionType.RECEIPT,
                reference_document=f"SALE-{sale.id}-CANCEL",
                user_id=user_id,
            )
            item.line_status = SaleLineStatus.CANCELLED

    sale.order_status = SaleOrderStatus.CANCELLED
    _append_workflow(sale, "CANCELLED", note=reason)
    await db.commit()
    return await get_sale(db, sale.id)  # type: ignore[return-value]


async def create_sale(
    db: AsyncSession,
    payload: PosCheckoutCreate,
    *,
    created_by_id: int,
) -> Sale:
    order_payload = SaleOrderCreate(
        customer_id=payload.customer_id,
        items=payload.items,
        confirm=payload.confirm,
        require_b2b_fields=False,
    )
    return await create_sale_order(
        db,
        order_payload,
        created_by_id=created_by_id,
        is_pos_checkout=True,
    )


async def search_pos_products(
    db: AsyncSession,
    *,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Product], int]:
    stmt = select(Product).where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE)
    count_stmt = (
        select(func.count())
        .select_from(Product)
        .where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE)
    )

    if search:
        pattern = f"%{search.strip()}%"
        filter_expr = or_(
            Product.sku.ilike(pattern),
            Product.name.ilike(pattern),
            Product.barcode.ilike(pattern),
        )
        stmt = stmt.where(filter_expr)
        count_stmt = count_stmt.where(filter_expr)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.order_by(Product.name).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def list_sales(
    db: AsyncSession,
    *,
    customer_id: int | None = None,
    order_status: SaleOrderStatus | None = None,
    order_number: str | None = None,
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[tuple[Sale, str | None, str | None, int, Decimal]], int]:
    stmt = (
        select(Sale)
        .options(
            selectinload(Sale.items),
            selectinload(Sale.customer),
            selectinload(Sale.created_by_user),
        )
        .order_by(Sale.created_at.desc())
    )
    count_stmt = select(func.count()).select_from(Sale)

    if customer_id is not None:
        stmt = stmt.where(Sale.customer_id == customer_id)
        count_stmt = count_stmt.where(Sale.customer_id == customer_id)
    if order_status is not None:
        stmt = stmt.where(Sale.order_status == order_status)
        count_stmt = count_stmt.where(Sale.order_status == order_status)
    term = (search or order_number or "").strip()
    if term:
        pattern = f"%{term}%"
        search_filter = or_(
            Sale.order_number.ilike(pattern),
            Sale.customer_po_number.ilike(pattern),
        )
        stmt = (
            stmt.outerjoin(Customer, Sale.customer_id == Customer.id)
            .outerjoin(SaleItem, SaleItem.sale_id == Sale.id)
            .outerjoin(Product, SaleItem.product_id == Product.id)
            .where(
                or_(
                    search_filter,
                    Customer.name.ilike(pattern),
                    Product.sku.ilike(pattern),
                    Product.name.ilike(pattern),
                ),
            )
            .distinct()
        )
        count_stmt = (
            select(func.count(func.distinct(Sale.id)))
            .select_from(Sale)
            .outerjoin(Customer, Sale.customer_id == Customer.id)
            .outerjoin(SaleItem, SaleItem.sale_id == Sale.id)
            .outerjoin(Product, SaleItem.product_id == Product.id)
            .where(
                or_(
                    search_filter,
                    Customer.name.ilike(pattern),
                    Product.sku.ilike(pattern),
                    Product.name.ilike(pattern),
                ),
            )
        )
        if customer_id is not None:
            count_stmt = count_stmt.where(Sale.customer_id == customer_id)
        if order_status is not None:
            count_stmt = count_stmt.where(Sale.order_status == order_status)
    if date_from is not None:
        stmt = stmt.where(Sale.order_date >= date_from)
        count_stmt = count_stmt.where(Sale.order_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Sale.order_date <= date_to)
        count_stmt = count_stmt.where(Sale.order_date <= date_to)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.offset(skip).limit(limit))
    sales = list(result.scalars().all())

    rows: list[tuple[Sale, str | None, str | None, int, Decimal]] = []
    for sale in sales:
        customer_name = sale.customer.name if sale.customer else None
        cashier_email = sale.created_by_user.email if sale.created_by_user else None
        item_count = len(sale.items)
        sale_total = sale.total if sale.total else sum(
            item.line_total for item in sale.items
        )
        rows.append((sale, customer_name, cashier_email, item_count, sale_total))
    return rows, total


async def get_sale(db: AsyncSession, sale_id: int) -> Sale | None:
    result = await db.execute(
        select(Sale)
        .options(
            selectinload(Sale.items).selectinload(SaleItem.product),
            selectinload(Sale.items).selectinload(SaleItem.substitute_product),
            selectinload(Sale.items).selectinload(SaleItem.warehouse),
            selectinload(Sale.customer),
            selectinload(Sale.created_by_user),
            selectinload(Sale.updated_by_user),
            selectinload(Sale.salesperson),
            selectinload(Sale.warehouse),
            selectinload(Sale.shipping_point),
            selectinload(Sale.partners).selectinload(SalePartner.customer),
            selectinload(Sale.partners).selectinload(SalePartner.supplier),
            selectinload(Sale.partners).selectinload(SalePartner.user),
        )
        .where(Sale.id == sale_id),
    )
    return result.scalar_one_or_none()
