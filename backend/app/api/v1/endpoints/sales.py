from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import payment as payment_crud
from app.crud import sale as sale_crud
from app.dependencies.auth import get_current_user_permissions, require_permission
from app.models.customer import Customer
from app.models.enums import SaleOrderStatus
from app.models.sale import Sale, SalePartner
from app.models.payment_method import PaymentMethod
from app.models.tax_rate import TaxRate
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.payments import OpenBalanceRead
from app.schemas.sale import (
    PosCheckoutCreate,
    PosProductListResponse,
    PosProductRead,
    SaleConfirmRequest,
    SaleItemRead,
    SaleListItem,
    SaleListResponse,
    SaleLookupCustomer,
    SaleLookupPaymentMethod,
    SaleLookupTaxRate,
    SaleLookupUser,
    SaleLookupWarehouse,
    SaleLookupsResponse,
    SaleOrderCreate,
    SaleOrderRead,
    SaleOrderSummary,
    SaleOrderUpdate,
    SalePartnerRead,
)
from app.services.sale_totals import build_order_summary

router = APIRouter(prefix="/sales")

ReadRoles = require_permission("sales.pos.use", "sales.orders.read")
WriteRoles = require_permission("sales.orders.write")
PosCheckoutRoles = require_permission("sales.pos.use")
PRICE_OVERRIDE_PERM = "sales.orders.price_override"


def _partner_to_read(partner: SalePartner) -> SalePartnerRead:
    return SalePartnerRead(
        id=partner.id,
        role=partner.role,
        customer_id=partner.customer_id,
        customer_name=partner.customer.name if partner.customer else None,
        supplier_id=partner.supplier_id,
        supplier_name=partner.supplier.name if partner.supplier else None,
        user_id=partner.user_id,
        user_email=partner.user.email if partner.user else None,
        name_override=partner.name_override,
        address=partner.address,
    )


def _sale_to_read(sale: Sale) -> SaleOrderRead:
    items: list[SaleItemRead] = []
    for item in sale.items:
        items.append(
            SaleItemRead(
                id=item.id,
                line_number=item.line_number,
                product_id=item.product_id,
                product_name=item.product.name,
                product_sku=item.product.sku,
                description=item.description,
                quantity=item.quantity,
                uom=item.uom,
                alternate_uom=item.alternate_uom,
                uom_conversion_factor=item.uom_conversion_factor,
                unit_price=item.unit_price,
                price_at_sale=item.price_at_sale,
                gross_price=item.gross_price,
                discount_percent=item.discount_percent,
                discount_amount=item.discount_amount,
                tax_code=item.tax_code,
                tax_rate_id=item.tax_rate_id,
                tax_amount=item.tax_amount,
                net_amount=item.net_amount,
                line_total=item.line_total,
                requested_delivery_date=item.requested_delivery_date,
                confirmed_delivery_date=item.confirmed_delivery_date,
                confirmed_quantity=item.confirmed_quantity,
                delivered_quantity=item.delivered_quantity,
                line_status=item.line_status,
                backorder_quantity=item.backorder_quantity,
                product_category=item.product_category,
                item_category=item.item_category,
                warehouse_id=item.warehouse_id,
                warehouse_name=item.warehouse.name if item.warehouse else None,
                storage_location_id=item.storage_location_id,
                batch_number=item.batch_number,
                serial_number=item.serial_number,
                delivery_block=item.delivery_block,
                billing_block=item.billing_block,
                rejection_reason=item.rejection_reason,
                net_weight=item.net_weight,
                gross_weight=item.gross_weight,
                volume=item.volume,
                substitute_product_id=item.substitute_product_id,
                substitute_product_sku=item.substitute_product.sku if item.substitute_product else None,
                line_text=item.line_text,
            ),
        )
    customer_name = sale.customer.name if sale.customer else None
    cashier_email = sale.created_by_user.email if sale.created_by_user else None
    summary_data = build_order_summary(sale)
    return SaleOrderRead(
        id=sale.id,
        order_number=sale.order_number,
        order_status=sale.order_status,
        order_date=sale.order_date,
        order_type=sale.order_type,
        sales_channel=sale.sales_channel,
        order_source=sale.order_source,
        priority=sale.priority,
        salesperson_id=sale.salesperson_id,
        salesperson_email=sale.salesperson.email if sale.salesperson else None,
        is_pos_checkout=sale.is_pos_checkout,
        customer_id=sale.customer_id,
        customer_name=customer_name,
        cashier_email=cashier_email,
        created_at=sale.created_at,
        updated_at=sale.updated_at,
        updated_by_email=sale.updated_by_user.email if sale.updated_by_user else None,
        items=items,
        partners=[_partner_to_read(p) for p in sale.partners],
        summary=SaleOrderSummary(**summary_data),
        gross_total=sale.gross_total,
        header_discount_amount=sale.header_discount_amount,
        freight_amount=sale.freight_amount,
        insurance_amount=sale.insurance_amount,
        handling_amount=sale.handling_amount,
        subtotal=sale.subtotal,
        tax=sale.tax_amount,
        total=sale.total,
        amount_paid=sale.amount_paid,
        payment_status=sale.payment_status,
        currency_code=sale.currency_code,
        price_list_code=sale.price_list_code,
        pricing_procedure=sale.pricing_procedure,
        payment_terms=sale.payment_terms,
        payment_due_date=sale.payment_due_date,
        payment_method_id=sale.payment_method_id,
        warehouse_id=sale.warehouse_id,
        warehouse_name=sale.warehouse.name if sale.warehouse else None,
        shipping_point_id=sale.shipping_point_id,
        shipping_point_name=sale.shipping_point.name if sale.shipping_point else None,
        partial_delivery_allowed=sale.partial_delivery_allowed,
        complete_delivery_required=sale.complete_delivery_required,
        planned_ship_date=sale.planned_ship_date,
        requested_delivery_date=sale.requested_delivery_date,
        shipping_method=sale.shipping_method,
        shipping_conditions=sale.shipping_conditions,
        transportation_group=sale.transportation_group,
        loading_group=sale.loading_group,
        incoterms=sale.incoterms,
        incoterms_location=sale.incoterms_location,
        delivery_block=sale.delivery_block,
        sales_organization=sale.sales_organization,
        distribution_channel=sale.distribution_channel,
        division=sale.division,
        sales_office=sale.sales_office,
        sales_group=sale.sales_group,
        customer_po_number=sale.customer_po_number,
        customer_po_date=sale.customer_po_date,
        opportunity_id=sale.opportunity_id,
        campaign_id=sale.campaign_id,
        price_group=sale.price_group,
        header_text=sale.header_text,
        credit_check_status=sale.credit_check_status,
        atp_check_status=sale.atp_check_status,
        invoice_status=sale.invoice_status,
        delivery_status=sale.delivery_status,
        approval_status=sale.approval_status,
        customer_snapshot=sale.customer_snapshot,
        pricing_conditions=sale.pricing_conditions,
        delivery_logistics=sale.delivery_logistics,
        billing_financial=sale.billing_financial,
        terms_compliance=sale.terms_compliance,
        references=sale.references,
        attachments=sale.attachments,
        workflow_history=sale.workflow_history,
    )


@router.get("/lookups", response_model=SaleLookupsResponse)
async def sale_lookups(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ReadRoles)],
) -> SaleLookupsResponse:
    customers = (
        await db.execute(
            select(Customer).order_by(Customer.name).limit(500),
        )
    ).scalars().all()
    warehouses = (
        await db.execute(
            select(Warehouse).order_by(Warehouse.name).limit(200),
        )
    ).scalars().all()
    users = (
        await db.execute(
            select(User).where(User.is_active.is_(True)).order_by(User.email).limit(200),
        )
    ).scalars().all()
    tax_rates = (
        await db.execute(
            select(TaxRate).order_by(TaxRate.code).limit(100),
        )
    ).scalars().all()
    payment_methods = await payment_crud.list_payment_methods(db)
    return SaleLookupsResponse(
        customers=[
            SaleLookupCustomer(id=c.id, customer_code=c.customer_code, name=c.name)
            for c in customers
        ],
        warehouses=[
            SaleLookupWarehouse(id=w.id, code=w.code, name=w.name) for w in warehouses
        ],
        users=[SaleLookupUser(id=u.id, email=u.email) for u in users],
        tax_rates=[
            SaleLookupTaxRate(
                id=t.id,
                code=t.code,
                name=t.name,
                rate_percent=t.rate_percent,
            )
            for t in tax_rates
        ],
        payment_methods=[
            SaleLookupPaymentMethod(id=m.id, code=m.code, name=m.name)
            for m in payment_methods
        ],
    )


@router.get("", response_model=SaleListResponse)
async def list_sales(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ReadRoles)],
    customer_id: int | None = None,
    order_status: SaleOrderStatus | None = None,
    order_number: str | None = None,
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> SaleListResponse:
    rows, total = await sale_crud.list_sales(
        db,
        customer_id=customer_id,
        order_status=order_status,
        order_number=order_number,
        search=search or order_number,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return SaleListResponse(
        items=[
            SaleListItem(
                id=sale.id,
                order_number=sale.order_number,
                order_status=sale.order_status,
                order_type=sale.order_type,
                customer_id=sale.customer_id,
                customer_name=customer_name,
                cashier_email=cashier_email,
                created_at=sale.created_at,
                order_date=sale.order_date,
                item_count=item_count,
                total=sale_total,
                payment_status=sale.payment_status,
                currency_code=sale.currency_code,
                delivery_status=sale.delivery_status,
            )
            for sale, customer_name, cashier_email, item_count, sale_total in rows
        ],
        total=total,
    )


@router.get("/products", response_model=PosProductListResponse)
async def list_pos_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ReadRoles)],
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
) -> PosProductListResponse:
    items, total = await sale_crud.search_pos_products(
        db,
        search=search,
        skip=skip,
        limit=limit,
    )
    return PosProductListResponse(
        items=[PosProductRead.model_validate(i) for i in items],
        total=total,
    )


@router.get("/{sale_id}/open-balance", response_model=OpenBalanceRead)
async def get_sale_open_balance(
    sale_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ReadRoles)],
) -> OpenBalanceRead:
    sale = await sale_crud.get_sale(db, sale_id)
    if sale is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sale not found")
    total = sale.total or sum(item.line_total for item in sale.items)
    paid = sale.amount_paid or Decimal("0")
    return OpenBalanceRead(
        document_id=sale.id,
        total=total,
        amount_paid=paid,
        open_balance=payment_crud.sale_open_balance(sale),
        payment_status=sale.payment_status.value,
        currency_code=sale.currency_code,
    )


@router.get("/{sale_id}", response_model=SaleOrderRead)
async def get_sale(
    sale_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ReadRoles)],
) -> SaleOrderRead:
    sale = await sale_crud.get_sale(db, sale_id)
    if sale is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return _sale_to_read(sale)


@router.post("", response_model=SaleOrderRead, status_code=status.HTTP_201_CREATED)
async def create_sale(
    body: SaleOrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(WriteRoles)],
    permissions: Annotated[set[str], Depends(get_current_user_permissions)],
) -> SaleOrderRead:
    sale = await sale_crud.create_sale_order(
        db,
        body,
        created_by_id=user.id,
        allow_price_override=PRICE_OVERRIDE_PERM in permissions,
    )
    loaded = await sale_crud.get_sale(db, sale.id)
    if loaded is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sale not found after create")
    return _sale_to_read(loaded)


@router.post("/checkout", response_model=SaleOrderRead, status_code=status.HTTP_201_CREATED)
async def checkout_sale(
    body: PosCheckoutCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PosCheckoutRoles)],
) -> SaleOrderRead:
    sale = await sale_crud.create_sale(db, body, created_by_id=user.id)
    loaded = await sale_crud.get_sale(db, sale.id)
    if loaded is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sale not found after checkout")
    return _sale_to_read(loaded)


@router.patch("/{sale_id}", response_model=SaleOrderRead)
async def update_sale(
    sale_id: int,
    body: SaleOrderUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(WriteRoles)],
    permissions: Annotated[set[str], Depends(get_current_user_permissions)],
) -> SaleOrderRead:
    sale = await sale_crud.get_sale(db, sale_id)
    if sale is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sale not found")
    updated = await sale_crud.update_sale_order(
        db,
        sale,
        body,
        updated_by_id=user.id,
        allow_price_override=PRICE_OVERRIDE_PERM in permissions,
    )
    loaded = await sale_crud.get_sale(db, updated.id)
    if loaded is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sale not found after update")
    return _sale_to_read(loaded)


@router.post("/{sale_id}/confirm", response_model=SaleOrderRead)
async def confirm_sale(
    sale_id: int,
    body: SaleConfirmRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(WriteRoles)],
) -> SaleOrderRead:
    sale = await sale_crud.get_sale(db, sale_id)
    if sale is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sale not found")
    confirmed = await sale_crud.confirm_sale_order(db, sale, body, user_id=user.id)
    loaded = await sale_crud.get_sale(db, confirmed.id)
    if loaded is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sale not found after confirm")
    return _sale_to_read(loaded)


@router.post("/{sale_id}/cancel", response_model=SaleOrderRead)
async def cancel_sale(
    sale_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(WriteRoles)],
    reason: str | None = None,
) -> SaleOrderRead:
    sale = await sale_crud.get_sale(db, sale_id)
    if sale is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sale not found")
    cancelled = await sale_crud.cancel_sale_order(db, sale, user_id=user.id, reason=reason)
    loaded = await sale_crud.get_sale(db, cancelled.id)
    if loaded is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sale not found after cancel")
    return _sale_to_read(loaded)


@router.post("/{sale_id}/credit-check", response_model=SaleOrderRead)
async def credit_check_sale(
    sale_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WriteRoles)],
) -> SaleOrderRead:
    from app.crud import customer as customer_crud
    from app.services.sale_credit_check import run_credit_check

    sale = await sale_crud.get_sale(db, sale_id)
    if sale is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sale not found")
    customer = await customer_crud.get_customer(db, sale.customer_id) if sale.customer_id else None
    await run_credit_check(db, sale, customer)
    await db.commit()
    loaded = await sale_crud.get_sale(db, sale_id)
    if loaded is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return _sale_to_read(loaded)


@router.post("/{sale_id}/atp-check", response_model=SaleOrderRead)
async def atp_check_sale(
    sale_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WriteRoles)],
) -> SaleOrderRead:
    from app.services.sale_atp_check import run_atp_check

    sale = await sale_crud.get_sale(db, sale_id)
    if sale is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sale not found")
    await run_atp_check(db, sale)
    await db.commit()
    loaded = await sale_crud.get_sale(db, sale_id)
    if loaded is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return _sale_to_read(loaded)
